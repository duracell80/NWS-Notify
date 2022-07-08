import os, subprocess, time, configparser, feedparser, pandas
from datetime import datetime




# Change TN to your state for example KY
# Change Davison to your county for example Benton

# Documentation	: https://alerts.weather.gov/cap/pdf/CAP%20v12%20guide%20web%2006052013.pdf
cfg = configparser.ConfigParser()
cfg.sections()
cfg.read('/usr/share/nws_alerts/config.ini')


# CONF: Set The State Scope
try:
    cfg['nws_conf']['state']
except KeyError:
    cfg_state = "TN"
else:
    cfg_state = cfg['nws_conf']['state'].upper()

# CONF: Set The County Scope
try:
    cfg['nws_conf']['county']
except KeyError:
    cfg_cname = "Davidson"
else:
    cfg_cname = cfg['nws_conf']['county']

# CONF: Audible Alert Voice (Uses espeak for text to speech)
try:
    cfg['alert_conf']['voice']
except KeyError:
    cfg_voice = "off"
else:
    cfg_voice = cfg['alert_conf']['voice']

# CONF: Audible Alert Siren (Uses alsa speaker test)
try:
    cfg['alert_conf']['alert']
except KeyError:
    cfg_alert = "off"
else:
    cfg_alert = cfg['alert_conf']['alert']

# CONF: Audible Alert Siren Volume
try:
    cfg['alert_conf']['level']
except KeyError:
    cfg_level = "80"
else:
    cfg_level = cfg['alert_conf']['level']

# CONF: NWS Feed Backoff
try:
    cfg['alert_conf']['timer']
except KeyError:
    cfg_timer = "5"
else:
    cfg_timer = cfg['alert_conf']['timer']
    
# CONF: NWS Alert Trigger Words
try:
    cfg['alert_conf']['keywords']
except KeyError:
    cfg_kwords      = "tornado warning, special weather statement"
    cfg_keywords    = cfg_kwords.split(",")
else:
    cfg_kwords      = cfg['alert_conf']['keywords']
    cfg_keywords    = cfg_kwords.split(",")
    
# CONF: QR CODES
try:
    cfg['nws_conf']['qrcode']
except KeyError:
    cfg_qrcodes      = "off"
else:
    cfg_qrcodes      = cfg['nws_conf']['qrcode']
    
# CONF: SHORTEN URLS
try:
    cfg['nws_conf']['urlsht']
except KeyError:
    cfg_urlsht      = "off"
else:
    cfg_urlsht      = cfg['nws_conf']['urlsht']


cfg_log   = "/tmp/nws_seen.txt"
cfg_cmd   = "notify-send"
cfg_start = 'espeak "'
cfg_end   = '" -w /tmp/espeak-wx.wav -g 10 -p 50 -s 175 -v en-us && play /tmp/espeak-wx.wav'
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""




        
# Main script
data_exists = os.path.exists('/tmp/nws_data.xml')

if data_exists:
    feed_url = "https://alerts.weather.gov/cap/"+ cfg_state.lower() +".php?x=0"
    feed_age = subprocess.check_output('find /tmp/nws_data.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    if len(feed_age) > 0:
        os.system('wget --quiet -O "/tmp/nws_data.xml" ' + feed_url + '');
        print("\n\n[-] Weather fetched from NWS [" + cfg_cname + ", " + cfg_state  + "]")
    else:
        feed_now = float(time.time())
        feed_dif = float(feed_now + (float(cfg_timer) * 60))
        feed_nxt = datetime.fromtimestamp(feed_dif)
        print("[-] Weather threat monitoring (" + cfg_cname + ", " + cfg_state + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

else:
    os.system('touch /tmp/nws_data.xml')
    os.system('chmod a+rw /tmp/nws_data.xml')
    os.system('touch /tmp/nws_seen.txt')
    os.system('chmod a+rw /tmp/nws_seen.txt')

feed_xml = open("/tmp/nws_data.xml", "r")
feed_dat = feed_xml.read().replace("cap:", "cap_")
feed_xml.close()

blog_feed = feedparser.parse(feed_dat)

# READ THE FEED
posts = blog_feed.entries

# GO THROUGH THE FEED
for post in posts:
    if cfg_cname in post.cap_areadesc:

        # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
        file = open(cfg_log, 'r')
        lines = file.readlines()
        
        # LOOK FOR SEEN ALERT ID's
        n_seen = "no"
        for line in lines:
            if post.id in line:
                n_seen = "yes"

        # CONTINUE IF ALERT NOT ALREADY SEEN        
        if n_seen == "no":
            url = post.id
            cfg_tit = "Weather Alert For " + cfg_cname.upper() + " County."
            cfg_msg = post.summary.replace("*", " ")
            print(cfg_msg)
            
            # SHORTEN URL FIRST
            if cfg_urlsht == "on":
                import pyshorteners
                
                shorten = pyshorteners.Shortener()
                url_sht = shorten.tinyurl.short(url)
                url = url_sht

            # GENERATE A QRCODE TO THE NWS
            if cfg_qrcodes == "on":
                import pyqrcode
                import png
                from pyqrcode import QRCode
                
                url_bits = post.id.split("?x=")
                
                frl = "/tmp/nwsqr_" + url_bits[1] + ".png"
                qrl = pyqrcode.create(url)
                qrl.png(frl, scale =10, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])


                cfg_script = cfg_cmd + ' --hint=string:image-path:'+frl+' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + cfg_cname.upper() + ' County ]" "' + cfg_msg + '"'
            else:
                if cfg_urlsht == "on":
                    # SHORTEN URL
                    cfg_script = cfg_cmd + ' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + cfg_cname.upper() + ' County ]" "' + cfg_msg + ' ' + url + '"'
                    
                else:
                    # USE NWS LONG URL
                    cfg_script = cfg_cmd + ' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + cfg_cname.upper() + ' County ]" "' + cfg_msg + ' ' + post.id + '"'
            
            # TRIGGER NOTIFIY SEND
            os.system(cfg_script)
            os.system('echo '+post.id+' >> '+cfg_log+'')

            # SOUND ALERT - only if title contains keywords defined in configuration and sound alerts enabled
            kfound = [fn for fn in cfg_keywords if(fn.lower() in post.cap_event.lower())]
            if bool(kfound):
                if cfg_alert == "on":
                    os.system(cfg_sound)
                if cfg_voice == "on":
                    os.system(cfg_start + cfg_tit + cfg_msg + cfg_end)
