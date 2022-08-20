#!/bin/bash
DIR_LOCAL="$HOME/.local/share/nws_alerts"
DIR_ASSET="$DIR_LOCAL/assets"
DIR_WDATA="$DIR_ASSET/data"
DIR_QCODE="$DIR_ASSET/qrcodes"

mkdir -p $DIR_LOCAL
mkdir -p $DIR_ASSET
mkdir -p $DIR_WDATA
mkdir -p $DIR_QCODE

chmod u+rw $DIR_LOCAL
chmod u+rw $DIR_ASSET
chmod u+rw $DIR_WDATA
chmod u+rw $DIR_QCODE



cp -f nws_watch.py $DIR_LOCAL
cp -f nws_alerts.sh $DIR_LOCAL
cp -f config.ini ~/.local/share/nws_alerts
chmod u+rw ~/.local/share/nws_alerts/config.ini
cp -f nws_seen.txt $DIR_WDATA
cp -f nws_seen.txt $DIR_WDATA/nws-uk_seen.txt
cp -f nws_seen.txt $DIR_WDATA/nws-nonus_seen.txt
#cp web_server.py $DIR_LOCAL



cp -f nws_data.xml $DIR_WDATA/nws-nonus_data.xml
chmod u+rw $DIR_WDATA/nws-nonus_seen.txt
chmod u+rw $DIR_WDATA/nws-nonus_data.xml

cp -f nws_data.xml $DIR_WDATA/nws_data.xml
chmod u+rw $DIR_WDATA/nws_seen.txt
chmod u+rw $DIR_WDATA/nws_data.xml


cp -f NWS-Notify.desktop ~/.config/autostart
sed -i "s|~/.local|${HOME}/.local|g" ~/.config/autostart/NWS-Notify.desktop

cp -f wx_check.sh ~/.local/bin/wx_check
chmod u+x ~/.local/bin/wx_check







sudo apt-get install wget espeak python3-pip zenity

# TO FIX URL REQUEST WARNINGS
#sudo pip3 install requests
#sudo python3 -m pip install --upgrade requests

sudo pip3 install configparser
sudo pip3 install feedparser
sudo pip3 install capparselib
sudo pip3 install numpy
sudo pip3 install pandas
sudo pip3 install pyqrcode
sudo pip3 install pypng
sudo pip3 install pyshorteners
sudo pip3 install gTTS
