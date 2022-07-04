import os, subprocess, time, configparser
from datetime import datetime

import feedparser, pandas



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


cfg_cwarn = "Severe Thunderstorm Warning"
#cfg_timer = "15"
cfg_cmd   = "notify-send"
cfg_sound = "speaker-test -t sine -f 1000 -l 1 -S " + cfg_level + ""
cfg_go    = "no"


cfg_start = 'espeak "'
cfg_end   = '" -w /tmp/espeak-wx.wav -g 10 -p 50 -s 175 -v en-us && play /tmp/espeak-wx.wav'





# Main script
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
feed_xml = open("/tmp/nws_data.xml", "r")
feed_dat = feed_xml.read().replace("cap:", "cap_")
feed_xml.close()

blog_feed = feedparser.parse(feed_dat)

posts = blog_feed.entries

for post in posts:
    if "Thunderstorm Watch" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: Storm Watch is in effect for your area ... (" + cfg_cname + ")"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if (cfg_cwarn or "Thunderstorm Warning") in post.title and cfg_cname in post.summary:
        cfg_msg = "Weather Alert: A Severe Storm Warning is in effect for your area ... (" + post.cap_areadesc + ")" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Tornado Watch" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Tornado Watch is in effect for your area ... (" + cfg_cname + ")"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if (cfg_cwarn or "Tornado Warning") in post.title and cfg_cname in post.summary:
        cfg_msg = "Weather Alert: A Tornado Warning in efefct for your area ... (" + post.cap_areadesc + ")" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Severe Weather Statement" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Severe Weather Statement has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Special Weather Statement" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Special Weather Statement has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Hurricane Watch" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Hurricane Watch has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Hurricane Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Hurricane Warning has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        cfg_go = "yes"
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Tropical Storm Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Tropical Storm Warning has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ") + ' Expires: ' + post.cap_expires
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        cfg_go = "yes"
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Flood Advisory" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Flood Advisory is in effect for your area ... (" + cfg_cname + ")\n\n"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Flash Flood Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Flash Flood Warning is in effect for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Heat Advisory" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Heat Advisory is in effect for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_alert == "on":
            os.system(cfg_sound)
        if cfg_voice == "on":
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Snow Advisory" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Snow Advisory is in effect for your area ... (" + cfg_cname + ")\n\n"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Ice Storm Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: An Ice Storm Warning is in effect for your area ... (" + cfg_cname + ")\n\n"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Freezing Rain Advisory" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Freezing Rain Advisory is in effect for your area ... (" + cfg_cname + ")\n\n"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Freezing Rain Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Freezing Rain Warning has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "Blizzard Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Blizzard Warning has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        if cfg_voice == "on":
            os.system(cfg_sound)
            os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "High Wind Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A High Wind Warning in effect for your area ... (" + cfg_cname + ")" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Red Flag Warning" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Red Flag Warning in effect for your area ... (" + cfg_cname + ")" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "Wind Advisory" in post.title and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Wind Advisory is in effect for your area ... (" + cfg_cname + ")"
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "air quailty" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: An Air Quality Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "smoke" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: An Air Quality Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "ice" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Winter Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "fire" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Fire Danger Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)
        os.system(cfg_sound)
        os.system(cfg_start + cfg_msg + cfg_end)

for post in posts:
    if "tornado" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Weather Alert: A Tornado Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "amber alert" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Child Alert: A Citizen Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

for post in posts:
    if "silver alert" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Elderly Alert: A Citizen Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)


for post in posts:
    if "blue alert" in post.summary and cfg_cname in post.cap_areadesc:
        cfg_msg = "Responder Alert: A First Responder Alert has been issued for your area ... (" + cfg_cname + ")\n\n" + post.summary.replace("*", " ")
        print(cfg_msg)

        cfg_script = cfg_cmd + ' "' + cfg_msg + '"'
        os.system(cfg_script)

