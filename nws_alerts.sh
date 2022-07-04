#!/bin/bash
echo  "National Weather Service Notifications - Looping mode - every 15 to 30 minutes"

while true
do
 python3 /usr/share/nws_alerts/nws_watch.py
 sleep 880
done
