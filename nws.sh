#!/bin/bash
clear
echo -e "National Weather Service Notifications - Looping mode"

echo -e "\n \nWeather data obtained from The National Weather Service every 15 to 30 minutes"
echo -e "- Press [CTRL+C] to stop"
echo -e "- Change state and county alerted on in nws.py"
echo -e "- Uses espeak for voice alerts and linux mints notication system \n\n"

while true
do
 python3 nws_watch.py
 sleep 880
done
