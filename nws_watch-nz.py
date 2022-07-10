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
    cfg_region = "NZ"
else:
    cfg_region = cfg['nws_conf']['region-nonus'].upper()

# CONF: Set The County Scope
try:
    cfg['nws_conf']['locale-nonus']
except KeyError:
    cfg_locale = "Gisborne,Christchurch"
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
    cfg_kwords      = "heavy rain warning,heavy snow warning"
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
from capparselib.parsers import CAPParser


feed_xml = open("/home/lee/nz.xml", "r")
feed_dat = feed_xml.read()
feed_xml.close()

alert_feed = feedparser.parse(feed_dat)

# READ THE FEED
posts = alert_feed.entries

# COLLECT EACH ALERT FILE
for post in posts:
    data_exists = os.path.exists('/tmp/nws-nz_' + post.guid + '.xml')
    if not data_exists:
        os.system('wget --quiet -O "/tmp/nws-nz_' + post.guid + '.xml" ' + post.link + '');
    
    
    file = open(cfg_log, 'r')
    lines = file.readlines()

    # LOOK FOR SEEN ALERT ID's
    n_seen = "no"
    for line in lines:
        if post.id in line:
            n_seen = "yes"
    
    
    
    # CONTINUE IF ALERT NOT ALREADY SEEN        
    if n_seen == "no":
        os.system('echo '+post.guid+' >> '+cfg_log+'')
        
        alert_cap = "/tmp/nws-nz_" + post.guid + ".xml"
        alert_src = open(alert_cap, 'r').read()
        alert_list = CAPParser(alert_src).as_dict()

        alert = alert_list[0]["cap_info"]

        for item in alert:
            alert_link          = item["cap_link"]
            alert_sender        = item["cap_sender_name"]
            alert_headline      = item["cap_headline"]
            alert_description   = item["cap_description"]
            alert_severity      = item["cap_severity"]
            for area in item["cap_area"]:
                alert_area      = area["area_description"]
                
        if alert_severity != "Minor":
            print(f"Headline: {alert_headline} Summary: {alert_description} Area: {alert_area} Link: {alert_link} Sender: {alert_sender}")
        
            cfg_script = f'{cfg_cmd} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region}: {alert_headline} - {alert_severity}" "{alert_description} Areas: {alert_area} - {alert_sender} - {alert_link}"'
        
        
            os.system(cfg_script)