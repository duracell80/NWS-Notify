#!/usr/bin/env python3

import os, re, subprocess, time, configparser, feedparser, pandas
from datetime import datetime
from gtts import gTTS

from capparselib.parsers import CAPParser


global HOME
HOME = str(os.popen('echo $HOME').read()).replace('\n', '')
FILE_CONF = HOME + '/.local/share/nws_alerts/config.ini'
DIR_ASSET = HOME + '/.local/share/nws_alerts/assets'
DIR_WDATA = HOME + '/.local/share/nws_alerts/assets/data'

cfg = configparser.ConfigParser()
cfg.sections()
cfg.read(FILE_CONF)

# GENERAL CONFIGURATION
cfg_level           = cfg.get('alert_conf', 'level', fallback='80')
cfg_timer           = cfg.get('alert_conf', 'timer', fallback='15')
cfg_para            = ""


# FILE LOCATION AND COMMAND HEAD TAIL
cfg_log   = DIR_WDATA + "/nws-nonus_seen.txt"
cfg_cmd   = "notify-send"
cfg_start = 'espeak "'
cfg_end   = '" -w '+ DIR_ASSET +'/espeak-wx.wav -g 10 -p 50 -s 175 -v en-us && play '+ DIR_ASSET +'/espeak-wx.wav'
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""
cfg_usloc = DIR_WDATA + "/nws_data.xml"
cfg_ukloc = DIR_WDATA + "/nws_data-ukmetoffice.xml"

# US CONFIGURATION (Primary Service - National Weather Service)
cfg_us_enable          = cfg.get('nws_conf', 'enable', fallback='on')







# US MAIN SCRIPT
if cfg_us_enable == "on":
    cfg_us_log          = DIR_WDATA + "/nws_seen.txt"
    cfg_qrcodes         = cfg.get('nws_conf', 'qrcode', fallback='off')
    cfg_urlsht          = cfg.get('nws_conf', 'urlsht', fallback='off')
    cfg_kwords          = cfg.get('nws_conf', 'keywords', fallback='tornado warning,severe thunderstorm warning,hurricane warning,red flag,blizzard warning,sepcial weather statement,severe weather statement')
    cfg_keywords        = cfg_kwords.lower().split(",")
    cfg_us_alertfor     = cfg.get('nws_conf', 'alertfor', fallback='severe thunderstorm,tornado warning,dust storm warning')
    cfg_us_alertkeys    = cfg_us_alertfor.lower().split(",")
    
    cfg_region          = cfg.get('nws_conf', 'region', fallback='TN')
    cfg_locale          = cfg.get('nws_conf', 'locale_main', fallback='Davidson,Williamson')
    cfg_locales         = cfg_locale.lower().split(",")
    cfg_watch           = cfg.get('nws_conf', 'watch', fallback='off')
    
    cfg_locale_watch    = cfg.get('nws_conf', 'locale_watch', fallback='Dickson,Cheatham,Wilson,Williamson,Robertson,Rutherford,Sumner,Montgomery')
    cfg_locales_watch   = cfg_locale_watch.lower().split(",")
    
    cfg_us_voice           = cfg.get('nws_conf', 'voice', fallback='off')
    cfg_us_alert           = cfg.get('nws_conf', 'alert', fallback='off')
    cfg_us_dopower         = "no"
    cfg_us_shutdown        = cfg.get('nws_conf', 'shutdown', fallback='off')
    
    
    # CHECK FOR DATA FILE
    data_exists = os.path.exists(DIR_WDATA + '/nws_data.xml')

    if data_exists:       
        
        
        # CHECK OUTSIDE AREA FOR APPROACHING THUNDERSTORMS IF watch=on
        if cfg_watch == "on":
            # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
            file = open(cfg_us_log, 'r')
            lines = file.readlines()

            # BALANCE SAFETY WITH SERVER LOAD
            feed_xml = open(DIR_WDATA + "/nws_data.xml", "r")
            feed_dat = feed_xml.read().replace("cap:", "cap_")
            feed_xml.close()
            
            if "There are no active watches, warnings or advisories" in feed_dat:
                print('[i] NWS: There are no active watches, warnings or advisories for ' + cfg_region.upper())
            else:
            
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
                            if post.cap_areadesc.lower() in cfg_locale_watch.lower():
                                cfg_para+= "Storms: " + post.cap_areadesc.upper() + "\n"
                                os.system('echo '+post.id+' >> '+cfg_us_log+'')


                if len(cfg_para) > 0:
                    print(cfg_para)
                    os.system('notify-send --urgency=low --category=im.received --icon=weather-storm-symbolic "Stay Weather Aware in ' + cfg_region.upper() + '" "' + cfg_para + '"')

                # READ THE FEED - BE KIND TO THE SERVICE EVEN IF CONFIGURED TO CHECK ONCE A MINUTE
                if int(cfg_timer) < 5:
                    cfg_timer = "5"



            feed_url = "https://alerts.weather.gov/cap/"+ cfg_region.lower() +".php?x=0"
            feed_age = subprocess.check_output('find '+ DIR_WDATA +'/nws_data.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)

            # CHECK THE AGE OF THE DATA
            if len(feed_age) > 0:
                os.system('wget --quiet -O "'+ DIR_WDATA +'/nws_data.xml" ' + feed_url + '');
                print("\n\n[-] Weather fetched from NWS [" + cfg_locale + ", " + cfg_region  + "]")
            else:
                feed_now = float(time.time())
                feed_dif = float(feed_now + (float(cfg_timer) * 60))
                feed_nxt = datetime.fromtimestamp(feed_dif)
                print("[-] Weather threat monitoring (" + cfg_locale + ", " + cfg_region + ")")
        
    # DATA FILE DOESNT EXIST
    else:
        os.system('touch ' + DIR_WDATA + '/nws_data.xml')
        os.system('chmod a+rw ' + DIR_WDATA + '/nws_data.xml')
        os.system('touch ' + cfg_us_log)
        os.system('chmod a+rw ' + cfg_us_log)
        
# READ US FEED
feed_xml = open(DIR_WDATA + "/nws_data.xml", "r")
feed_dat = feed_xml.read().replace("cap:", "cap_")
feed_xml.close()

blog_feed = feedparser.parse(feed_dat)

# READ THE FEED
posts = blog_feed.entries


# GO THROUGH THE FEED
for post in posts:
    
    if hasattr(post, "cap_areadesc"):
        areas = post.cap_areadesc.split(";")
        for area in areas:
            area_item = area.lower().strip()
            for locale in cfg_locales:
                locale_item = locale.strip()


                if locale_item.lower() in area_item:
                    
                    # LOOK FOR KEYWORDS IN TITLE
                    kword_match = "no"
                    if cfg_kwords == "all":
                        kword_match = "yes"
                    else:
                        for kword in range(len(cfg_keywords)):
                            if cfg_keywords[kword].lower() in post.title.lower():
                                kword_match = "yes"
                    
                    # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
                    file = open(cfg_us_log, 'r')
                    lines = file.readlines()

                    # LOOK FOR SEEN ALERT ID's
                    n_seen = "no"
                    for line in lines:
                        if post.id in line:
                            n_seen = "yes"

                    # CONTINUE IF ALERT NOT ALREADY SEEN AND NOT CANCELLED AND MATCHED KEYWORDS GIVEN IN CONFIG       
                    if n_seen == "no" and "cancelled" not in post.summary.lower() and kword_match == "yes":
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

                        frl = DIR_ASSET + "/qrcodes/nwsqr_" + url_bits[1] + ".png"
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
                        os.system('echo '+post.id+' >> '+cfg_us_log+'')

                        # TRIGGER THE SYSTEM SHUTDOWN PROMPT FOR STORM AND TORNADO WARNINGS
                        if ("tornado warning") in post.title.lower():
                            cfg_us_dopower = "yes"
                        if ("severe thunderstorm warning") in post.title.lower():
                            cfg_us_dopower = "yes"
                        if ("strong thunderstorm") in post.summary.lower():
                            cfg_us_dopower = "yes"
                            
                        lastmsg = post.title + '\n' + cfg_msg
                        
                        # SOUND ALERT - only if title contains keywords defined in configuration and sound alerts enabled
                        kfound = [fn for fn in cfg_us_alertkeys if(fn.lower() in post.cap_event.lower())]
                        if bool(kfound):
                            if cfg_us_alert == "on":
                                os.system(cfg_sound)
                            if cfg_us_voice == "on":

                                # GOOGLE TTS - ESPEAK AS BACKUP
                                tts = gTTS(cfg_msg.replace("mph", "miles per hour"), lang='en', tld='com')
                                tts.save(DIR_ASSET + '/wx_alert.mp3')
                                os.system("ffmpeg -y -i " + DIR_ASSET + "/wx_alert.mp3 -acodec pcm_u8 -ar 22050 " + DIR_ASSET + "/wx_alert.wav")
                                os.system("play "+ DIR_ASSET +"/wx_alert.wav")
                                
                                #os.system(cfg_start + cfg_tit + cfg_msg.replace("mph", "miles per hour") + cfg_end)
                                

                            
                            
# SHUTDOWN ON SEVERE STORM IN US ONLY
# Not reliable globally since not all weather alerts around the world offer immediate storm warnings
if cfg_us_dopower == "yes":
    print("[i] Potenitally destructive weather is near by!")
    if cfg_us_shutdown == "on":
        QUESTION = str(os.system('zenity --question --width=500 --default-cancel --timeout 300 --text="Potenitally destructive weather is near by! \n' + lastmsg + ' \n\nDo you wish to suspend your system?"'))
        if QUESTION == "0":
            os.system('zenity --warning --width=250 --timeout 30 --text="Please save your work during the next 2 minutes!"')
            os.system("sleep 90 && notify-send --urgency=critical --category=im.received --icon=weather-storm-symbolic 'Your system is about to suspend in the next 30 seconds ...' && sleep 30 && systemctl suspend")
                            
                            
                            
    
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
    data_exists = os.path.exists(cfg_ukloc)
    if data_exists:
        os.system('touch '+ DIR_WDATA +'/nws-uk_seen.txt')
        if os.stat(cfg_ukloc).st_size == 0:
            feed_age = "30"
        else:
            feed_age = subprocess.check_output('find '+ DIR_WDATA +'/nws_data-ukmetoffice.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    else:
        os.system('touch '+ DIR_WDATA +'/nws-uk_seen.txt')
        os.system('touch '+ DIR_WDATA +'/nws_data-ukmetoffice.xml')
        
        os.system('chmod a+rw '+ DIR_WDATA +'/nws-uk_seen.txt')
        os.system('chmod a+rw '+ DIR_WDATA +'/nws_data-ukmetoffice.xml')
        feed_age = "30"

    # ALLOW FOR BACK OFF IN CHECKING SERVICE
    if len(feed_age) > 0:
        os.system('wget --quiet -O "'+ DIR_WDATA +'/nws_data-ukmetoffice.xml" ' + feed_uk + '');
        print("\n\n[-] Weather fetched [ UK MET OFFICE ]")
    else:
        feed_now = float(time.time())
        feed_dif = float(feed_now + (float(cfg_timer) * 60))
        feed_nxt = datetime.fromtimestamp(feed_dif)
        print("[-] Weather threat monitoring (" + cfg_locale_uk + ", " + cfg_region_uk + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

    if data_exists:
        feed_xml = open(DIR_WDATA + '/nws_data-ukmetoffice.xml', 'r')
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



                    frl = DIR_ASSET + "/qrcodes/nwsqr_" + post_guid + ".png"
                    qrl = pyqrcode.create(url)
                    qrl.png(frl, scale =10, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])

                    date_items = post_date.split("-")

                    # PREVENT ALERTS SHOWING TOO FAR INTO THE FUTURE
                    # (Met Office can alert too early. Example extreme heat 5 days out, overloading notifications isn't good.)
                    dif = (int(round(datetime(int(date_items[0]), int(date_items[1]), int(int(date_items[2]) - 0), 0, 0).timestamp())) - int(round(time.time())))      

                    
                    if dif < 172800:
                        # AVOID LOGGING A SEEN EVENT UNTIL ACTUALLY SEEN
                        
                        if "red" in str(post.title).lower():
                            post_urgency = "normal"
                            post_icon = "dialog-warning-symbolic"
                        else:
                            post_urgency = "normal"
                            post_icon = "dialog-warning-symbolic"
                        
                        print(f"\n\nHeadline: {post.title} Summary: {post.description} Area: {cfg_region_uk} Link: {url} Sender: UK Met Office")
                        # CHECK FOR QR AND SHORTENING
                        if cfg_qrcodes_uk == "on":
                            if cfg_urlsht_uk == "on":
                                cfg_script = f'{cfg_cmd} --hint=string:image-path:{frl} --urgency={post_urgency} --category=im.received --icon={post_icon} "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office - {url}"'
                            else:
                                cfg_script = f'{cfg_cmd} --hint=string:image-path:{frl} --urgency={post_urgency} --category=im.received --icon={post_icon} "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office"'
                        # FALL BACK ON LINK IN FEED
                        else:
                            cfg_script = f'{cfg_cmd} --urgency={post_urgency} --category=im.received --icon={post_icon} "{cfg_region_uk}: {post.title}" "{post.description} - UK Met Office - {url}"'
                        
                        os.system('echo '+post_guid_u+' >> '+cfg_log+'')
                        os.system(cfg_script)
                        
                    else:
                        print(f"{post.title} - ( Too Early To Alert On - {post_date} )")

                    



    else:
        print(f"Main RSS Feed not found for {feed_uk}")
        #os.system('zenity --error --text="Main RSS Feed not found for ' + feed_uk + '"')
    


# The Non-US/UK Feeds use a demo collection service from the WMO
# Set The WMO CAP Feed ID in config.ini from https://severeweather.wmo.int/v2/feeds.html 
# Example eg es-aemet-es for Spain

# Not all feeds will have usable links for QR Codes
# Usually the WMO feeds point to single CAP files for each event, cycle the main feed to wget single event CAP's

cfg_enable_nonus    = cfg.get('nws_conf-nonus', 'enable', fallback='off')

if cfg_enable_nonus == "on":
    cfg_region_nonus    = cfg.get('nws_conf-nonus', 'region', fallback='PR')
    cfg_locale_nonus    = cfg.get('nws_conf-nonus', 'locale', fallback='Guarda,Vila Real')
    cfg_feedid_nonus    = cfg.get('nws_conf-nonus', 'feedid', fallback='pt-ipma-pt')
    if not cfg_locale_nonus == "all":
        cfg_locales_nonus   = cfg_locale_nonus.lower().split(",")
    else:
        cfg_locales_nonus = "all,all"
    feed_nonus          = f"http://alert-feed.worldweather.org/{cfg_feedid_nonus.lower()}/rss.xml"
    cfg_kwords_nonus    = cfg.get('nws_conf-nonus', 'keywords', fallback='thunderstorm,wind')
    cfg_keywords_nonus  = cfg_kwords_nonus.lower().split(",")
    cfg_soundfor_nonus  = cfg.get('nws_conf-nonus', 'soundfor', fallback='thunderstorm,wind').lower().split(",")

    # Main script - WMO (NON-NWS)
    data_exists = os.path.exists(DIR_WDATA + '/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
    if data_exists:
        os.system('touch '+ DIR_WDATA +'/nws-nonus_seen.txt')
        os.system('chmod a+rw '+ DIR_WDATA +'/nws-nonus_seen.txt')
        if os.stat(DIR_WDATA + '/nws_data-' + cfg_feedid_nonus.lower() + '.xml').st_size == 0:
            feed_age = "30"
        else:
            feed_age = subprocess.check_output('find '+ DIR_WDATA +'/nws_data-' + cfg_feedid_nonus.lower() + '.xml -mmin +' + cfg_timer, shell=True, universal_newlines=True)
    else:
        os.system('touch '+ DIR_WDATA +'/nws-nonus_seen.txt')
        os.system('touch '+ DIR_WDATA +'/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
        
        os.system('chmod a+rw '+ DIR_WDATA +'/nws-nonus_seen.txt')
        os.system('chmod a+rw '+ DIR_WDATA +'/nws_data-' + cfg_feedid_nonus.lower() + '.xml')
        feed_age = "30"


    if len(feed_age) > 0:
        os.system('wget --quiet -O "'+ DIR_WDATA +'/nws_data-' + cfg_feedid_nonus.lower() + '.xml" ' + feed_nonus + '');
        print("\n\n[-] Weather fetched [" + cfg_locale_nonus + ", " + cfg_region_nonus  + "]")
    else:
        feed_now = float(time.time())
        feed_dif = float(feed_now + (float(cfg_timer) * 60))
        feed_nxt = datetime.fromtimestamp(feed_dif)
        print("[-] Weather threat monitoring (" + cfg_locale_nonus + ", " + cfg_region_nonus + " - Next update: " + feed_nxt.strftime('%H:%M:%S') + ")")

    if data_exists:
        feed_xml = open(DIR_WDATA + '/nws_data-' + cfg_feedid_nonus.lower() + '.xml', 'r')
        feed_dat = feed_xml.read()
        feed_xml.close()
        alert_feed = feedparser.parse(feed_dat)
        alertsound_nonus = "no"
        
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
            if cfg_kwords_nonus == "all":
                kword_match = "yes"
            else:
                for kword in range(len(cfg_keywords_nonus)):
                    if cfg_keywords_nonus[kword].lower() in post.title.lower():
                        kword_match = "yes"

            # LIMIT TO ABOUT A 24 HOUR PERIOD
            dif = (int(round(time.time())) - int(time.strftime('%s', post.published_parsed)))      
            if dif < 86400 and post.category == "Met" and kword_match == "yes":
                
                # DEPLOY THE SIREN (ONLY ONCE) AT THE END OF THE LOOPS IF KEYWORDS FOUND
                # Thunderstorm warnings in Europe last a whole ass day, sirens may not be effective!
                for tword in range(len(cfg_soundfor_nonus)):
                    if cfg_soundfor_nonus[tword].lower() in post.title.lower():
                        alertsound_nonus = "yes"
                
                # DIVE DEEPER INTO THE SINGLE CAP FILE
                data_exists = os.path.exists(DIR_WDATA + '/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml')
                if not data_exists:
                    os.system('wget --quiet -O "'+ DIR_WDATA +'/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml" ' + post.link + '');


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

                    alert_cap = DIR_WDATA + '/nws-' + cfg_feedid_nonus.lower() + '_' + post.guid + '.xml'
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
                                    alert_area       = "all"

                                for locale in cfg_locales_nonus:
                                    if locale in alert_areas:
                                        area_seen = "yes"


                    if alert_severity != "Minor" and area_seen == "yes":
                        #print(f"\n\nDate: {post.published_parsed} Headline: {alert_headline} Summary: {alert_description} Area: {alert_area.upper()} Link: {alert_link} Sender: {alert_sender}")
                        
                        if "thunderstorm" in str(post.title).lower():
                            post_urgency = "normal"
                            post_icon = "weather-storm-symbolic"
                        else:
                            post_urgency = "normal"
                            post_icon = "dialog-warning-symbolic"
                        
                        if not alert_area == "all":
                            cfg_script = f'{cfg_cmd} --urgency={post_urgency} --category=im.received --icon={post_icon} "{cfg_region_nonus} - {alert_areas.upper()}: {alert_headline}" "{alert_severity} - {alert_description} - {alert_sender} - {alert_link}"'
                        else:
                            cfg_script = f'{cfg_cmd} --urgency={post_urgency} --category=im.received --icon={post_icon} "{cfg_region_nonus}: {alert_headline} - {alert_severity}" "Areas: {alert_areas.upper()} - {alert_description} - {alert_sender} - {alert_link}"'

                        os.system(cfg_script)
                        
    else:
        print(f"Main RSS Feed not found for {cfg_feedid_nonus.lower()}")
        #os.system('zenity --error --text="Main RSS Feed not found for ' + cfg_feedid_nonus.lower() + '"')
