import os, re, subprocess, time, configparser, feedparser, pandas
from datetime import datetime

from capparselib.parsers import CAPParser


cfg = configparser.ConfigParser()
cfg.sections()
cfg.read('/usr/share/nws_alerts/config.ini')


# GENERAL CONFIGURATION
cfg_watch           = cfg.get('alert_conf', 'watch', fallback='off')
cfg_voice           = cfg.get('alert_conf', 'voice', fallback='off')
cfg_alert           = cfg.get('alert_conf', 'alert', fallback='off')
cfg_level           = cfg.get('alert_conf', 'level', fallback='80')
cfg_timer           = cfg.get('alert_conf', 'timer', fallback='15')

# FILE LOCATION AND COMMAND HEAD TAIL
cfg_log   = "/tmp/nws-nonus_seen.txt"
cfg_cmd   = "notify-send"
cfg_start = 'espeak "'
cfg_end   = '" -w /tmp/espeak-nonus-wx.wav -g 10 -p 50 -s 175 -v en-us && play /tmp/espeak-nonus-wx.wav'
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""


# US CONFIGURATION (Primary Service - National Weather Service)
cfg_enable          = cfg.get('nws_conf', 'enable', fallback='on')

# US MAIN SCRIPT
if cfg_enable == "on":
    cfg_qrcodes         = cfg.get('nws_conf', 'qrcode', fallback='off')
    cfg_urlsht          = cfg.get('nws_conf', 'urlsht', fallback='off')
    cfg_kwords          = cfg.get('nws_conf', 'keywords', fallback='tornado warning,severe thunderstorm warning,hurricane warning,red flag,blizzard warning,sepcial weather statement,severe weather statement')
    cfg_keywords        = cfg_kwords.lower().split(",")

    
    
# Main script - UK (MET OFFICE)
cfg_enable_uk    = cfg.get('nws_conf-uk', 'enable', fallback='on')

if cfg_enable_uk == "on":
    cfg_urlsht_uk    = cfg.get('nws_conf-uk', 'urlsht', fallback='off')
    cfg_qrcodes_uk   = cfg.get('nws_conf-uk', 'qrcode', fallback='off')

    cfg_region_uk    = cfg.get('nws_conf-uk', 'region', fallback='UK')
    cfg_locale_uk    = cfg.get('nws_conf-uk', 'locale', fallback='West Midlands,East Midlands')
    cfg_locales_uk   = cfg_locale_uk.lower().split(",")
    cfg_feedid_uk    = cfg.get('nws_conf-uk', 'feedid', fallback='https://www.metoffice.gov.uk/public/data/PWSCache/WarningsRSS/Region/UK')
    feed_uk          = cfg_feedid_uk
    cfg_kwords_uk    = cfg.get('nws_conf-uk', 'keywords', fallback='extreme heat,flood,thunderstorm warning')
    cfg_keywords_uk  = cfg_kwords_uk.lower().split(",")

    # CHECK FEED FILE EXISTS
    data_exists = os.path.exists('/tmp/nws_data/nws_data-ukmetoffice.xml')
    if data_exists:
        os.system('touch /tmp/nws-nonus_seen.txt')
        feed_age = subprocess.check_output('find /tmp/nws_data/nws_data-ukmetoffice.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    else:
        os.system('touch /tmp/nws-nonus_seen.txt')
        os.system('mkdir -p /tmp/nws_data')
        os.system('touch /tmp/nws_data/nws_data-ukmetoffice.xml')
        feed_age = "30"

    # ALLOW FOR BACK OFF IN CHECKING SERVICE
    if len(feed_age) > 0:
        os.system('wget --quiet -O "/tmp/nws_data/nws_data-ukmetoffice.xml" ' + feed_uk + '');
        print("\n\n[-] Weather fetched [ UK MET OFFICE ]")
    else:
        feed_now = float(time.time())
        feed_dif = float(feed_now + (float(cfg_timer) * 60))
        feed_nxt = datetime.fromtimestamp(feed_dif)
        print("[-] Weather threat monitoring (" + cfg_locale_uk + ", " + cfg_region_uk + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

    if data_exists:
        feed_xml = open('/tmp/nws_data/nws_data-ukmetoffice.xml', 'r')
        feed_dat = feed_xml.read()
        feed_xml.close()
        alert_feed = feedparser.parse(feed_dat)

        # READ THE FEED
        posts = alert_feed.entries
        for post in posts:

            file = open(cfg_log, 'r')
            lines = file.readlines()

            # FIND UUID IN LINK TO USE AS ID
            url_bits    = post.guid.split("=")
            post_region = url_bits[4]
            post_guid   = url_bits[2].replace("&referrer", "")
            post_guid_u = post_guid + post_region.lower().replace(" ", "")
            post_date   = url_bits[1].replace("&id", "")
            
            # LOOK FOR SEEN ALERT ID's
            n_seen = "no"
            for line in lines:
                if post_guid_u in line:
                    n_seen = "yes"
            
            # RUN SCRIPT ONLY IF ALERT ID NOT SEEN IN LOG
            if n_seen == "no":
                

                # LOOK FOR KEYWORDS IN TITLE
                kword_match = "no"
                for kword in range(len(cfg_keywords_uk)):
                    if cfg_keywords_uk[kword].lower() in post.title.lower():
                        kword_match = "yes"

                area_seen = "no"
                if cfg_locale_uk == "all":
                    area_seen   = "yes"
                    alert_area  = "all"
                else:
                    for locale in cfg_locales_uk:
                        if locale in post.description.lower():
                                area_seen = "yes"

                if area_seen == "yes" and kword_match == "yes":
                    url = post.link
                    # SHORTEN URL FIRST ...
                    # To create simpler QR Codes and shorter links in the notification text, change to off in config if tinyURL erroring
                    if cfg_urlsht_uk == "on":
                        import pyshorteners

                        shorten = pyshorteners.Shortener()
                        url_sht = shorten.tinyurl.short(url)
                        url = url_sht

                    # GENERATE A QRCODE TO THE MET OFFICE ... 
                    # Config on or off relates to showing QR in notifcation, so we get QR codes in the /tmp directory to serve
                    import pyqrcode
                    import png
                    from pyqrcode import QRCode



                    frl = "/tmp/qrcodes/nwsqr_" + post_guid + ".png"
                    qrl = pyqrcode.create(url)
                    qrl.png(frl, scale =10, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])

                    date_items = post_date.split("-")

                    # PREVENT ALERTS SHOWING TOO FAR INTO THE FUTURE
                    # (Met Office can alert too early. Example extreme heat 5 days out, overloading notifications isn't good.)
                    dif = (int(round(datetime(int(date_items[0]), int(date_items[1]), int(int(date_items[2]) - 0), 0, 0).timestamp())) - int(round(time.time())))      

                    
                    if dif < 86400:
                        # AVOID LOGGING A SEEN EVENT UNTIL ACTUALLY SEEN
                        
                        print(f"\n\nHeadline: {post.title} Summary: {post.description} Area: {cfg_region_uk} Link: {url} Sender: UK Met Office")
                        # CHECK FOR QR AND SHORTENING
                        if cfg_qrcodes_uk == "on":
                            if cfg_urlsht_uk == "on":
                                cfg_script = f'{cfg_cmd} --hint=string:image-path:{frl} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office - {url}"'
                            else:
                                cfg_script = f'{cfg_cmd} --hint=string:image-path:{frl} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office"'
                        # FALL BACK ON LINK IN FEED
                        else:
                            cfg_script = f'{cfg_cmd} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office - {url}"'
                        
                        os.system('echo '+post_guid_u+' >> '+cfg_log+'')
                        os.system(cfg_script)
                        
                    else:
                        print(f"{post.title} - ( Too Early To Alert On - {post_date} )")

                    



    else:
        print(f"Main RSS Feed not found for {feed_uk}")    
    


# The Non-US/UK Feeds use a demo collection service from the WMO
# Set The WMO CAP Feed ID in config.ini from https://severeweather.wmo.int/v2/feeds.html 
# Example eg es-aemet-es for Spain

# Not all feeds will have usable links for QR Codes
# Usually the WMO feeds point to single CAP files for each event, cycle the main feed to wget single event CAP's

cfg_enable_nonus    = cfg.get('nws_conf-nonus', 'enable', fallback='off')

if cfg_enable_nonus == "on":
    cfg_region_nonus    = cfg.get('nws_conf-nonus', 'region', fallback='PR')
    cfg_locale_nonus    = cfg.get('nws_conf-nonus', 'locale', fallback='Guarda,Vila Real')
    if not cfg_locale_nonus == "all":
        cfg_locales_nonus   = cfg_locale_nonus.lower().split(",")
    else:
        cfg_locales_nonus = "all,areas"
    cfg_feedid_nonus    = cfg.get('nws_conf-nonus', 'feedid', fallback='pt-ipma-pt')
    feed_nonus          = f"http://alert-feed.worldweather.org/{cfg_feedid_nonus.lower()}/rss.xml"
    cfg_kwords_nonus    = cfg.get('nws_conf-nonus', 'keywords', fallback='heavy rain warning,heavy snow warning')
    cfg_keywords_nonus  = cfg_kwords_nonus.lower().split(",")


    # Main script - WMO (NON-NWS)
    data_exists = os.path.exists('/tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
    if data_exists:
        os.system('touch /tmp/nws-nonus_seen.txt')
        feed_age = subprocess.check_output('find /tmp/nws_data/nws_data-' + cfg_feedid_nonus.lower() + '.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    else:
        os.system('touch /tmp/nws-nonus_seen.txt')
        os.system('mkdir -p /tmp/nws_data')
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

        # DEBUG THE DICT
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

                        if cfg_locale_nonus == "all":
                            area_seen   = "yes"
                            alert_area  = "all"
                        else:
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
                        print(f"\n\nHeadline: {alert_headline} Summary: {alert_description} Area: {alert_area} Link: {alert_link} Sender: {alert_sender}")

                        if not alert_area == "all":
                            cfg_script = f'{cfg_cmd} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_nonus}: {alert_headline} - {alert_severity}" "{alert_description} Areas: {alert_area} - {alert_sender} - {alert_link}"'
                        else:
                            cfg_script = f'{cfg_cmd} --urgency=normal --category=im.received --icon=dialog-warning-symbolic "{cfg_region_nonus}: {alert_headline} - {alert_severity}" "{alert_description} - {alert_sender} - {alert_link}"'

                        os.system(cfg_script)
    else:
        print(f"Main RSS Feed not found for {cfg_feedid_nonus.lower()}")
