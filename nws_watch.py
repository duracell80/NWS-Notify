#!/usr/bin/env python3

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
    cfg['nws_conf']['region']
except KeyError:
    cfg_region = "TN"
else:
    cfg_region = cfg['nws_conf']['region'].upper()

# CONF: Set The County Scope
try:
    cfg['nws_conf']['locale']
except KeyError:
    cfg_locale = "Davidson,Dickson"
else:
    cfg_locale = cfg['nws_conf']['locale']
    
cfg_locales = cfg_locale.split(",")

# CONF: Watch Entire Region (Heads up outside your locale/county, increases frequency of checks when storms approaching).
try:
    cfg['alert_conf']['watch']
except KeyError:
    cfg_watch = "off"
else:
    cfg_watch = cfg['alert_conf']['watch']

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
    cfg_timer = "15"
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
cfg_para  = ""



        
# Main script
data_exists = os.path.exists('/tmp/nws_data.xml')

if data_exists:
    
    # CHECK OUTSIDE AREA FOR APPROACHING THUNDERSTORMS IF watch=on
    if cfg_watch == "on":
        # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
        file = open(cfg_log, 'r')
        lines = file.readlines()

        # BALANCE SAFETY WITH SERVER LOAD
        feed_xml = open("/tmp/nws_data.xml", "r")
        feed_dat = feed_xml.read().replace("cap:", "cap_")
        feed_xml.close()

        blog_feed = feedparser.parse(feed_dat)

        # READ THE FEED - CHECK FOR THUNDERSTORM OR TORNADO KEYWORDS TO INCREASE FREQUENCY OF CHECKS
        posts = blog_feed.entries


        for post in posts:
            if "thunderstorm" in post.summary.lower():
                cfg_timer = "10"
                a_seen = "no"
                for line in lines:
                    if post.id.lower() in line.lower():
                        a_seen = "yes"

                if a_seen == "no":
                    cfg_para+= "Storms: " + post.cap_areadesc.upper() + "\n"
                    os.system('echo '+post.id+' >> '+cfg_log+'')


        if len(cfg_para) > 0:
            print(cfg_para)
            os.system('notify-send --urgency=low --category=im.received --icon=weather-storm-symbolic "Stay Weather Aware in ' + cfg_region.upper() + '" "' + cfg_para + '"')

        # READ THE FEED - BE KIND TO THE SERVICE EVEN IF CONFIGURED TO CHECK ONCE A MINUTE
        if int(cfg_timer) < 5:
            cfg_timer = "5"

    
    
    feed_url = "https://alerts.weather.gov/cap/"+ cfg_region.lower() +".php?x=0"
    feed_age = subprocess.check_output('find /tmp/nws_data.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    if len(feed_age) > 0:
        os.system('wget --quiet -O "/tmp/nws_data.xml" ' + feed_url + '');
        print("\n\n[-] Weather fetched from NWS [" + cfg_locale + ", " + cfg_region  + "]")
    else:
        feed_now = float(time.time())
        feed_dif = float(feed_now + (float(cfg_timer) * 60))
        feed_nxt = datetime.fromtimestamp(feed_dif)
        print("[-] Weather threat monitoring (" + cfg_locale + ", " + cfg_region + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

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
    
    areas = post.cap_areadesc.split(";")
    for area in areas:
        area_item = area.lower().strip()
        for locale in cfg_locales:
            locale_item = locale.strip()


            if locale_item.lower() in area_item:

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
                    cfg_tit = "Weather Alert For " + locale_item.upper() + " County."
                    cfg_msg = post.summary.replace("*", " ")
                    print(cfg_msg)

                    # SHORTEN URL FIRST ...
                    # To create simpler QR Codes and shorter links in the notification text, change to off in config if tinyURL erroring
                    if cfg_urlsht == "on":
                        import pyshorteners

                        shorten = pyshorteners.Shortener()
                        url_sht = shorten.tinyurl.short(url)
                        url = url_sht

                    # GENERATE A QRCODE TO THE NWS ... 
                    # Config on or off relates to showing QR in notifcation, so we get QR codes in the /tmp directory to serve
                    import pyqrcode
                    import png
                    from pyqrcode import QRCode

                    url_bits = post.id.split("?x=")

                    frl = "/tmp/qrcodes/nwsqr_" + url_bits[1] + ".png"
                    qrl = pyqrcode.create(url)
                    qrl.png(frl, scale =10, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])

                    if cfg_qrcodes == "on":
                        cfg_script = cfg_cmd + ' --hint=string:image-path:'+frl+' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + locale_item.upper() + ' County ]" "' + cfg_msg + '"'

                    else:
                        if cfg_urlsht == "on":
                            # SHORTEN URL
                            cfg_script = cfg_cmd + ' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + locale_item.upper() + ' County ]" "' + cfg_msg + ' ' + url + '"'

                        else:
                            # USE NWS LONG URL
                            cfg_script = cfg_cmd + ' --urgency=normal --category=im.received --icon=dialog-warning-symbolic "' + post.title + ' [ ' + locale_item.upper() + ' County ]" "' + cfg_msg + ' ' + post.id + '"'
                            

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
