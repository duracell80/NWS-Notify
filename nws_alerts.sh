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


while true
do
 sort $DIR_WDATA/nws_seen.txt | uniq > $DIR_WDATA/nws_seen.tmp && cat $DIR_WDATA/nws_seen.tmp > $DIR_WDATA/nws_seen.txt && rm $DIR_WDATA/nws_seen.tmp
 python3 $DIR_LOCAL/nws_watch.py
 sleep 120
done
