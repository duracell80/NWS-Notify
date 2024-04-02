#!/bin/bash
DIR_LOCAL="$HOME/.local/share/nws_alerts"
DIR_ASSET="$DIR_LOCAL/assets"
DIR_WDATA="$DIR_ASSET/data"
DIR_QCODE="$DIR_ASSET/qrcodes"


echo  "National Weather Service Notifications - Looping mode - every 5 to 15 minutes"
mkdir -p $DIR_QCODE
#$HOME/.local/nws_alerts/web_server.py&

notify-send --urgency=low --category=im.received --icon=help-info-symbolic "Weather Alerts Active" "Visit the Startup Applications to turn off for next login."

#$HOME/.local/share/notifications_read.py&

# KEEP A MONTH OF DATA
find $DIR_WDATA -name "*.xml" -type f -mtime +31 -delete

wget --quiet -O "${DIR_WDATA}/nws_pds_data.xml" "https://www.spc.noaa.gov/products/spcpdswwrss.xml"
wget --quiet -O "${DIR_WDATA}/nws_data.xml" "https://alerts.weather.gov/cap/TN.php?x=0"

sleep 2

TW_COUNT=$(cat "${DIR_WDATA}/nws_data.xml" | grep -i -A30 "tornado watch" | grep -i "davidson" | wc -l)

if [[ $TW_COUNT > 0 ]]; then
	notify-send --urgency=low --category=im.received --icon=weather-storm-symbolic "TORNADO WATCH IN EFFECT" "A tornado watch is in effect for Davidson County in Tenneessee, stay weather aware!"
fi


while true
do
 sort $DIR_WDATA/nws_seen.txt | uniq > $DIR_WDATA/nws_seen.tmp && cat $DIR_WDATA/nws_seen.tmp > $DIR_WDATA/nws_seen.txt && rm $DIR_WDATA/nws_seen.tmp
 python3 $DIR_LOCAL/nws_watch.py
 sleep 120
done
