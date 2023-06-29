#!/usr/bin/env python3

import os, sys, re, subprocess, time, configparser, feedparser, pandas
from datetime import datetime
from gtts import gTTS
from gtts.tokenizer import pre_processors
import gtts.tokenizer.symbols

from capparselib.parsers import CAPParser

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


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
cfg_timer           = cfg.get('alert_conf', 'timer', fallback='60')
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
    cfg_us_logtxt       = DIR_WDATA + "/nws_alerts_us.log"
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
    
    cfg_region_aqi      = cfg.get('aqi_conf', 'region', fallback='TN')
    cfg_aqi_cities      = cfg.get('aqi_conf', 'cities', fallback='memphis,nashville,clarksville')
    cfg_cities_aqi      = cfg_aqi_cities.lower().split(",")
    cfg_aqi_usid        = cfg.get('aqi_conf', 'usid', fallback='89')
    aqi_curr_timer      = cfg.get('aqi_conf', 'timer_conditions', fallback='60')
    cfg_aqi_timer       = cfg.get('aqi_conf', 'timer_alerts', fallback='360')
    
    cfg_locale_watch    = cfg.get('nws_conf', 'locale_watch', fallback='Dickson,Cheatham,Wilson,Williamson,Robertson,Rutherford,Sumner,Montgomery')
    cfg_locales_watch   = cfg_locale_watch.lower().split(",")
    
    cfg_us_voice           = cfg.get('nws_conf', 'voice', fallback='off')
    cfg_us_speed           = cfg.get('nws_conf', 'speed', fallback='1.125')
    cfg_us_alert           = cfg.get('nws_conf', 'alert', fallback='off')
    cfg_us_dopower         = "no"
    cfg_us_shutdown        = cfg.get('nws_conf', 'shutdown', fallback='off')
    
    cfg_pds_timer          = "120"
    
    
    
    
    #DEBUG VOICE
    #ttc = "Hello this is a test of the emergency alert test system and is only a test. Thank you for listening!"
    #tts = gTTS(str(ttc), lang='en', tld='com')
    #tts.save(DIR_ASSET + '/wx_alert.mp3')
    #os.system("ffmpeg -y -i " + DIR_ASSET + "/wx_alert.mp3  -filter:a \"atempo="+str(cfg_us_speed)+"\" -acodec pcm_u8 -ar 44100 " + DIR_ASSET + "/wx_alert.wav")
    #os.system("play "+ DIR_ASSET +"/wx_alert.wav")
    
    
    file = open(cfg_us_log, 'r')
    lines = file.readlines()
    file.close()
    
    # BALANCE SAFETY WITH SERVER LOAD
    feed_xml = open(DIR_WDATA + "/nws_data.xml", "r")
    feed_dat = feed_xml.read().replace("cap:", "cap_")
    feed_xml.close()
    
    # CHECK FOR DATA FILE
    data_exists = os.path.exists(DIR_WDATA + '/nws_data.xml')

    if data_exists:       
        
        # CHECK OUTSIDE AREA FOR APPROACHING THUNDERSTORMS IF watch=on
        if cfg_watch == "on":
            # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
            file = open(cfg_us_log, 'r')
            lines = file.readlines()
            file.close()
            
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
                    if "thunderstorm" in post.summary.lower() or "tornado" in post.title.lower():
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
                print("[-] Weather threat monitoring (" + cfg_locale + ", " + cfg_region + ") Updates every " + str(cfg_timer) + " minutes")
        
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

os.system('rm -f ' + DIR_WDATA + '/active-nws/tornado_watch')
os.system('rm -f ' + DIR_WDATA + '/active-nws/tornado_warning')
os.system('rm -f ' + DIR_WDATA + '/active-nws/severe_thunderstorm_warning')
os.system('rm -f ' + DIR_WDATA + '/active-nws/wind_warning')

# GO THROUGH THE FEED
for post in posts:

    if hasattr(post, "cap_areadesc"):
        areas = post.cap_areadesc.split(";")
        for area in areas:
            area_item = area.lower().strip()
            for locale in cfg_locales:
                locale_item = locale.strip()


                if locale_item.lower() in area_item:
                    if "wind warning" in post.title.lower():
                        cfg_timer = "30"
                        os.system('touch ' + DIR_WDATA + '/active-nws/wind_warning')
                    if "tornado watch" in post.title.lower():
                        cfg_timer = "10"
                        os.system('touch ' + DIR_WDATA + '/active-nws/tornado_watch')
                    if "severe thunderstorm" in post.title.lower():
                        cfg_timer = "10"
                        os.system('touch ' + DIR_WDATA + '/active-nws/severe_thunderstorm_warning')
                    if "tornado warning" in post.title.lower():
                        cfg_timer = "5"
                        os.system('touch ' + DIR_WDATA + '/active-nws/tornado_warning')

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
                        
                        # WRITE TO LOG OF EVENTS
                        
                        log_us_msg = str(int(time.time())) + '|' + post.title + '|' + locale_item.upper() + ' County|' + cfg_msg + '|' + url
                        
                        os.system('echo "' + str(log_us_msg) + '" >> ' + cfg_us_logtxt)

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
                                ttc = cfg_msg.replace("TN", "Tennessee")
                                ttc = ttc.replace("mph", "miles per hour")
                                tts = gTTS(str(ttc), lang='en', tld='com')
                                tts.save(DIR_ASSET + '/wx_alert.mp3')
                                os.system("ffmpeg -y -i " + DIR_ASSET + "/wx_alert.mp3  -filter:a \"atempo="+str(cfg_us_speed)+"\" -acodec pcm_u8 -ar 44100 " + DIR_ASSET + "/wx_alert.wav")
                                os.system("play "+ DIR_ASSET +"/wx_alert.wav")
                                

                            
                            
# SHUTDOWN ON SEVERE STORM IN US ONLY
# Not reliable globally since not all weather alerts around the world offer immediate storm warnings
if cfg_us_dopower == "yes":
    print("[i] Potenitally destructive weather is near by!")
    if cfg_us_shutdown == "on":
        QUESTION = str(os.system('zenity --question --width=500 --default-cancel --timeout 300 --text="Potenitally destructive weather is near by! \n' + lastmsg + ' \n\nDo you wish to suspend your system?"'))
        if QUESTION == "0":
            os.system('zenity --warning --width=250 --timeout 30 --text="Please save your work during the next 2 minutes!"')
            os.system("sleep 90 && notify-send --urgency=critical --category=im.received --icon=weather-storm-symbolic 'Your system is about to suspend in the next 30 seconds ...' && sleep 30 && systemctl suspend")
                            
# US SPC - PDS (Particularly Dangerous Situation)
# https://www.spc.noaa.gov/products/spcpdswwrss.xml                

pds_feed_url            = "https://www.spc.noaa.gov/products/spcpdswwrss.xml"
pds_us_file             = DIR_WDATA + "/nws_pds_data.xml"

# CHECK FOR US PDS DATA FILE
pds_us_exists           = os.path.exists(pds_us_file)

if pds_us_exists:
        pds_us_ts = subprocess.check_output('date -r ' + pds_us_file +' "+%s"', shell=True, universal_newlines=True)
        pds_us_delta = int(time.time()) - int(pds_us_ts)
        
        # CHECK THE AGE OF THE US PDS DATA
        if int(pds_us_delta) < 172800:
            os.system('wget --quiet -O "'+ pds_us_file + '" ' + pds_feed_url + '');
            print("\n\n[-] PDS Data fetched from Storm Prediction Center [US-ALL]")
        else:
            print("[-] SPC PDS Monitoring (US-ALL) Data window = 2 days")
            
        
        if int(pds_us_delta) < 172800:
            # READ US FEED
            pds_us_xml = open(pds_us_file, "r")
            pds_us_dat = pds_us_xml.read().replace("cap:", "cap_")
            pds_us_xml.close()

            pds_us_feed = feedparser.parse(pds_us_dat)

            # READ THE FEED
            pds_posts = pds_us_feed.entries

            # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
            file = open(cfg_us_logtxt, 'r')
            lines = file.readlines()
            file.close()
            
            # GO THROUGH THE FEED
            for post in pds_posts:
                pds_us_url = str(post.link)
                pds_us_guid = str(post.guid)
                pds_us_title = str(post.title)
                pds_us_desc = str(remove_html_tags(str(post.description)))

                pds_us_area = pds_us_desc.partition('\n')[0]

                # LOOK FOR SEEN ALERT ID's
                n_seen = "no"
                for line in lines:
                    if post.id in line:
                        n_seen = "yes"

                # CONTINUE IF ALERT NOT ALREADY SEEN       
                if n_seen != "yes":
                    # WRITE TO LOG OF EVENTS
                    log_pds_us_msg = str(int(time.time())) + '|' + str(pds_us_title) + '|All State|' + pds_us_guid + '|' + str(pds_us_area)

                    os.system('echo "' + str(log_pds_us_msg) + '" >> ' + cfg_us_logtxt)

                    if str(cfg_region).lower() in str(pds_us_area).lower():
                        os.system('notify-send --urgency=normal --category=im.received --icon=weather-severe-alert-symbolic "'+ str(pds_us_title) + '" "' + str(pds_us_desc) + '"')


else:
    os.system('touch ' + pds_us_file)
    os.system('chmod a+rw ' + pds_us_file)
    os.system('wget --quiet -O "'+ pds_us_file + '" ' + pds_feed_url + '');

# US Air Quality
aqi_feed_url            = "https://feeds.enviroflash.info/cap/aggregate.xml"
aqi_us_file             = DIR_WDATA + "/nws_aqi_data.xml"

# CHECK FOR US AQI DATA FILE
aqi_us_exists           = os.path.exists(aqi_us_file)

if aqi_us_exists:
        aqi_us_age = subprocess.check_output('find '+ aqi_us_file +' -mmin +' + cfg_aqi_timer, shell=True, universal_newlines=True)

        # CHECK THE AGE OF THE US AQI DATA
        if len(aqi_us_age) > 0:
            os.system('wget --quiet -O "'+ aqi_us_file + '" ' + aqi_feed_url + '');
            print("\n\n[-] Air Quality Data fetched from AirNow [US-ALL]")
        else:
            print("[-] Air Quality Monitoring (US-ALL) (Updates every " + str(cfg_aqi_timer) + " minutes)")

            # READ US FEED
            aqi_us_xml = open(aqi_us_file, "r")
            aqi_us_dat = aqi_us_xml.read().replace("cap:", "cap_")
            aqi_us_xml.close()

            aqi_us_feed = feedparser.parse(aqi_us_dat)

            # READ THE FEED
            aqi_posts = aqi_us_feed.entries

            # READ THE SEEN ALERTS FILE (Cleared on system reboot, logout etc)
            file = open(cfg_us_logtxt, 'r')
            lines = file.readlines()
            file.close()

            # GO THROUGH THE FEED
            for post in aqi_posts:

                if str(cfg_region_aqi).lower() in str(post.cap_areadesc).lower():
                    for city in cfg_cities_aqi:
                        if city.lower() in post.description.lower():
                            print( "[!] Air Quality Alert: " + str(post.cap_areadesc).upper())

                    # LOOK FOR SEEN ALERT ID's
                    n_seen = "no"
                    for line in lines:
                        if post.id in line:
                            n_seen = "yes"

                    # CONTINUE IF ALERT NOT ALREADY SEEN AND NOT CANCELLED AND MATCHED KEYWORDS GIVEN IN CONFIG       
                    if n_seen != "yes":
                        url = post.id

                        aqi_us_msg = str(post.cap_description)

                        for city in cfg_cities_aqi:
                            if city.lower() in post.description.lower():
                                
                                os.system('notify-send --urgency=low --category=im.received --icon=weather-severe-alert-symbolic "'+ str(post.cap_headline) + '" "' + str(post.cap_description) + '.. ' +  str(post.cap_instruction) + '"')
                            
                                if cfg_us_alert == "on":
                                    os.system(cfg_sound)
                                if cfg_us_voice == "on":
                                    cfg_msg = str(post.cap_headline) + ". " + str(aqi_us_msg) + ". " + str(post.cap_instruction)

                                    # GOOGLE TTS
                                    ttc = cfg_msg.replace("A(n)", "An")
                                    ttc = ttc.replace("AQI ", ", on the air quality index. ,")
                                    tts = gTTS(str(ttc), lang='en', tld='com')
                                    tts.save(DIR_ASSET + '/wx_alert.mp3')
                                    os.system("ffmpeg -y -i " + DIR_ASSET + "/wx_alert.mp3  -filter:a \"atempo="+str(cfg_us_speed)+"\" -acodec pcm_u8 -ar 44100 " + DIR_ASSET + "/wx_alert.wav")
                                    os.system("play "+ DIR_ASSET +"/wx_alert.wav")


                                # WRITE TO LOG OF EVENTS
                                log_aqi_us_msg = str(int(time.time())) + '|' + post.cap_headline + '|All County|' + aqi_us_msg + '|' + url

                                os.system('echo "' + str(log_aqi_us_msg) + '" >> ' + cfg_us_logtxt)
else:
    os.system('touch ' + aqi_us_file)
    os.system('chmod a+rw ' + aqi_us_file)
    os.system('touch ' + aqi_us_file)
    os.system('chmod a+rw ' + aqi_us_file)                

                                
            
            
# US CURRENT AIRQUALITY FOR LOCATION 89=Nashville, TN 593=Willamsport, PA
#https://feeds.enviroflash.info/rss/realtime/<indexnumber>.xml

aqi_curr_url            = "https://feeds.enviroflash.info/rss/realtime/" + cfg_aqi_usid + ".xml"
aqi_curr_file           = DIR_WDATA + "/nws_aqi_curr.xml"

# CHECK FOR US AQI DATA FILE
aqi_curr_exists         = os.path.exists(aqi_curr_file)

if aqi_curr_exists:
        aqi_curr_age = subprocess.check_output('find '+ aqi_curr_file +' -mmin +' + aqi_curr_timer, shell=True, universal_newlines=True)
        
        # CHECK THE AGE OF THE US AQI DATA
        if len(aqi_curr_age) > 0:
            os.system("rm -f " + aqi_curr_file)
            time.sleep(2)
            os.system('wget --quiet -O '+ aqi_curr_file + ' ' + aqi_curr_url + '');
            #print("[-] Air Quality Current Conditions [UPDATED]")
        else:
            print("[-] Air Quality Current Conditions  (updates every " + str(aqi_curr_timer) + " minutes)")
            
        if len(aqi_curr_age) > 0:
            # READ US FEED
            aqi_curr_xml = open(aqi_curr_file, "r")
            aqi_curr_dat = aqi_curr_xml.read().replace("cap:", "cap_")
            aqi_curr_xml.close()

            aqi_curr_feed = feedparser.parse(aqi_curr_dat)

            # READ THE FEED
            aqi_curr = aqi_curr_feed.entries

            # GO THROUGH THE FEED
            for post in aqi_curr:
                aqi_curr_raw    = str(remove_html_tags(str(post.description)))
                aqi_conditions  = re.sub(r"[\t]*", "", aqi_curr_raw)
                aqi_bits        = aqi_conditions.split("\n")
                
                print(aqi_bits[14])
                
                aqi_conditions = str(aqi_bits[14] + "\n" + aqi_bits[16])
                
                if "good" in str(aqi_conditions).lower():
                    print(str(aqi_curr_raw))
                    
                elif "hazardous" in str(aqi_conditions).lower():
                    os.system('notify-send --urgency=low --category=im.received --icon=weather-severe-alert-symbolic "'+ str(post.title) + '" (Alert Level: URGENT)"' + str(aqi_conditions) + '"')
                
                    if cfg_us_alert == "on":
                        os.system(cfg_sound)
                        
                        if cfg_us_voice == "on":
                            cfg_msg = "Current Air Quality Alert. " + str(aqi_conditions)
                            
                            # GOOGLE TTS
                            ttc = cfg_msg.replace("AQI ", ", on the Air Quality Index for ")
                            tts = gTTS(str(ttc), lang='en', tld='com')
                            tts.save(DIR_ASSET + '/wx_alert.mp3')
                            os.system("ffmpeg -y -i " + DIR_ASSET + "/wx_alert.mp3  -filter:a \"atempo="+str(cfg_us_speed)+"\" -acodec pcm_u8 -ar 44100 " + DIR_ASSET + "/wx_alert.wav")
                            os.system("play "+ DIR_ASSET +"/wx_alert.wav")
                
                elif "moderate" in str(aqi_conditions).lower() or "unhealthy" in str(aqi_conditions).lower():
                    os.system('notify-send --urgency=low --category=im.received --icon=weather-severe-alert-symbolic "'+ str(post.title) + ' (Alert Level: MONITOR)" "' + str(aqi_conditions) + '"')
                    
                else:
                    print(str(aqi_curr_raw))
                    
            
else:
    os.system('touch ' + aqi_curr_file)
    os.system('chmod a+rw ' + aqi_curr_file)
    os.system('touch ' + aqi_curr_file)
    os.system('chmod a+rw ' + aqi_curr_file)                

                
                            
    
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
