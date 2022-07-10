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
    cfg['nws_conf']['region-nonus']
except KeyError:
    cfg_region = "FN"
else:
    cfg_region = cfg['nws_conf']['region-nonus'].upper()

# CONF: Set The County Scope
try:
    cfg['nws_conf']['locale-nonus']
except KeyError:
    cfg_locale = "Uusimaa,Tornio"
else:
    cfg_locale = cfg['nws_conf']['locale-nonus']
    
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
    cfg['nws_conf-nonus']['keywords']
except KeyError:
    cfg_kwords      = "fire Warning,forest-fire"
    cfg_keywords    = cfg_kwords.split(",")
else:
    cfg_kwords      = cfg['nws_conf-nonus']['keywords']
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


cfg_log   = "/tmp/nws-nonus_seen.txt"
cfg_cmd   = "notify-send"
cfg_start = 'espeak "'
cfg_end   = '" -w /tmp/espeak-nonus-wx.wav -g 10 -p 50 -s 175 -v en-us && play /tmp/espeak-nonus-wx.wav'
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""
cfg_para  = ""



        
# Main script

feed_xml = open("/home/lee/nz.xml", "r")
feed_dat = feed_xml.read().replace("cap:", "cap_")
feed_xml.close()

blog_feed = feedparser.parse(feed_dat)

# READ THE FEED
posts = blog_feed.entries

# GO THROUGH THE FEED
for post in posts:
    
    areas = post.cap_areadesc.split(",")
    for area in areas:
        area_item = area.lower().strip()
        for locale in cfg_locales:
            locale_item = locale.strip()
            print(locale_item.lower())

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
                    cfg_tit = "Weather Alert For " + locale_item.upper() + "."
                    cfg_msg = ""
                    #print(cfg_msg)

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

                    frl = "/tmp/qrcodes/nwsqr_" + post.cap_identifier + ".png"
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
                    #os.system(cfg_script)
                    os.system('echo '+post.id+' >> '+cfg_log+'')

                    # SOUND ALERT - only if title contains keywords defined in configuration and sound alerts enabled
                    kfound = [fn for fn in cfg_keywords if(fn.lower() in post.cap_event.lower())]
                    if bool(kfound):
                        if cfg_alert == "on":
                            os.system(cfg_sound)
                        if cfg_voice == "on":
                            os.system(cfg_start + cfg_tit + cfg_msg + cfg_end)
