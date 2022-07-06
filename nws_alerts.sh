#!/bin/bash
echo  "National Weather Service Notifications - Looping mode - every 5 to 15 minutes"

while true
do
 sort /tmp/nws_seen.txt | uniq > /tmp/nws_seen.tmp && cat /tmp/nws_seen.tmp > /tmp/nws_seen.txt && rm /tmp/nws_seen.tmp
 python3 /usr/share/nws_alerts/nws_watch.py
 #python3 nws_watch.py
 sleep 310
done