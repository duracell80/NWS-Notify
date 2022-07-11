import os, subprocess, time, configparser, feedparser, pandas
from datetime import datetime

from capparselib.parsers import CAPParser

cfg = configparser.ConfigParser()
cfg.sections()
cfg.read('/usr/share/nws_alerts/config.ini')




# Set The NON-US CAP Feed ID From: https://severeweather.wmo.int/v2/feeds.html

cfg_qrcodes         = cfg.get('nws_conf', 'qrcode', fallback='off')
cfg_urlsht          = cfg.get('nws_conf', 'urlsht', fallback='off')


cfg_region_nonus    = cfg.get('nws_conf-nonus', 'region', fallback='PR')
cfg_locale_nonus    = cfg.get('nws_conf-nonus', 'locale', fallback='Guarda,Vila Real')
cfg_locales_nonus   = cfg_locale_nonus.lower().split(",")
cfg_feedid_nonus    = cfg.get('nws_conf-nonus', 'feedid', fallback='pt-ipma-pt')
feed_nonus          = f"http://alert-feed.worldweather.org/{cfg_feedid_nonus.lower()}/rss.xml"
cfg_kwords_nonus    = cfg.get('nws_conf-nonus', 'keywords', fallback='heavy rain warning,heavy snow warning')
cfg_keywords_nonus  = cfg_kwords_nonus.lower().split(",")


cfg_watch           = cfg.get('alert_conf', 'watch', fallback='off')
cfg_voice           = cfg.get('alert_conf', 'voice', fallback='off')
cfg_alert           = cfg.get('alert_conf', 'alert', fallback='off')
cfg_level           = cfg.get('alert_conf', 'level', fallback='80')
cfg_timer           = cfg.get('alert_conf', 'timer', fallback='15')



cfg_log   = "/tmp/nws-nonus_seen.txt"
cfg_cmd   = "notify-send"
cfg_start = 'espeak "'
cfg_end   = '" -w /tmp/espeak-nonus-wx.wav -g 10 -p 50 -s 175 -v en-us && play /tmp/espeak-nonus-wx.wav'
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""
cfg_para  = ""



        
# Main script
data_exists = os.path.exists('/tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
if data_exists:
    feed_age = subprocess.check_output('find /tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
else:
    os.system('touch /tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
    feed_age = "30"


if len(feed_age) > 0:
    os.system('wget --quiet -O "/tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml" ' + feed_nonus + '');
    print("\n\n[-] Weather fetched [" + cfg_locale_nonus + ", " + cfg_region_nonus  + "]")
else:
    feed_now = float(time.time())
    feed_dif = float(feed_now + (float(cfg_timer) * 60))
    feed_nxt = datetime.fromtimestamp(feed_dif)
    print("[-] Weather threat monitoring (" + cfg_locale_nonus + ", " + cfg_region_nonus + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

if data_exists:
    feed_xml = open('/tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml', 'r')
    feed_dat = feed_xml.read()
    feed_xml.close()
    alert_feed = feedparser.parse(feed_dat)

    
    
    

    # READ THE FEED
    posts = alert_feed.entries

    #for x in range(len(posts)):
        #print(posts[x])

    #exit()

    # COLLECT EACH ALERT FILE
    for post in posts:
        
        
        # LOOK FOR KEYWORDS IN TITLE
        kword_match = "no"
        for kword in range(len(cfg_keywords_nonus)):
            if cfg_keywords_nonus[kword].lower() in post.title.lower():
                kword_match = "yes"
        
        # LIMIT TO ABOUT A 24 HOUR PERIOD
        dif = (int(round(time.time())) - int(time.strftime('%s', post.published_parsed)))      
        if dif < 86400 and post.category == "Met" and kword_match == "yes":
            
            data_exists = os.path.exists('/tmp/nws_data/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml')
            if not data_exists:
                os.system('wget --quiet -O "/tmp/nws_data/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml" ' + post.link + '');


            file = open(cfg_log, 'r')
            lines = file.readlines()

            # LOOK FOR SEEN ALERT ID's
            n_seen = "no"
            for line in lines:
                if post.guid in line:
                    n_seen = "yes"

            


            # CONTINUE IF ALERT NOT ALREADY SEEN        
            if n_seen == "no":
                os.system('echo '+post.guid+' >> '+cfg_log+'')
                
                alert_cap = '/tmp/nws_data/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml'
                alert_src = open(alert_cap, 'r').read()
                alert_list = CAPParser(alert_src).as_dict()

                alert = alert_list[0]["cap_info"]

                for item in alert:
                    area_seen           = "no"
                    alert_link          = item["cap_link"]
                    alert_sender        = item["cap_sender_name"]
                    alert_headline      = item["cap_headline"]
                    alert_description   = item["cap_description"]
                    alert_severity      = item["cap_severity"]
                    
                    
                    for area in item["cap_area"]:
                        if len(area["area_description"]) < 2:
                            alert_areas      = str(area["area_description"]).lower()
                            alert_area       = alert_areas
                        else:
                            alert_areas      = "multiple"
                        
                        for locale in cfg_locales_nonus:
                            if locale in alert_areas:
                                area_seen = "yes"
                            
                            
                if alert_severity != "Minor" and area_seen == "yes":
                    print(f"Headline: {alert_headline} Summary: {alert_description} Area: {alert_area} Link: {alert_link} Sender: {alert_sender}")

                    cfg_script = f'{cfg_cmd} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_nonus}: {alert_headline} - {alert_severity}" "{alert_description} Areas: {alert_area} - {alert_sender} - {alert_link}"'


                    os.system(cfg_script)
else:
    print(f"Main RSS Feed not found for {cfg_feedid_nonus.lower()}")