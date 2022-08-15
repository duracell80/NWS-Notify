#!/bin/bash
echo  "National Weather Service Notifications - Looping mode - every 5 to 15 minutes"
mkdir -p /tmp/qrcodes
#$HOME/.local/nws_alerts/web_server.py&


while true
do
 sort /tmp/nws_seen.txt | uniq > /tmp/nws_seen.tmp && cat /tmp/nws_seen.tmp > /tmp/nws_seen.txt && rm /tmp/nws_seen.tmp
 python3 $HOME/.local/share/nws_alerts/nws_watch.py
 sleep 60
done
