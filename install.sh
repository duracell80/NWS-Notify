#!/bin/bash
DIR_CACHE="$HOME/.cache"
DIR_LOCAL="$HOME/.local/share/nws_alerts"
DIR_ASSET="$DIR_LOCAL/assets"
DIR_WDATA="$DIR_ASSET/data"
DIR_QCODE="$DIR_ASSET/qrcodes"

mkdir -p $DIR_LOCAL
mkdir -p $DIR_ASSET
mkdir -p $DIR_WDATA
mkdir -p $DIR_WDATA/active
mkdir -p $DIR_QCODE
#touch $DIR_CACHE/alerts_history.txt

chmod u+rw $DIR_LOCAL
chmod u+rw $DIR_ASSET
chmod u+rw $DIR_WDATA
chmod u+rw $DIR_QCODE




cp -f nws_watch.py $DIR_LOCAL
cp -f nws_alerts.sh $DIR_LOCAL
cp -f config.ini ~/.local/share/nws_alerts
chmod u+rw ~/.local/share/nws_alerts/config.ini
cp -f nws_alerts_us.log $DIR_WDATA
cp -f nws_seen.txt $DIR_WDATA
cp -f nws_seen.txt $DIR_WDATA/nws-uk_seen.txt
cp -f nws_seen.txt $DIR_WDATA/nws-nonus_seen.txt
#cp web_server.py $DIR_LOCAL

#cp -f notifications_read.py $HOME/.local/share/


cp -f nws_data.xml $DIR_WDATA/nws-nonus_data.xml
chmod u+rw $DIR_WDATA/nws-nonus_seen.txt
chmod u+rw $DIR_WDATA/nws-nonus_data.xml

cp -f nws_data.xml $DIR_WDATA/nws_data.xml
chmod u+rw $DIR_WDATA/nws_seen.txt
chmod u+rw $DIR_WDATA/nws_alerts_us.log
chmod u+rw $DIR_WDATA/nws_data.xml

mkdir -p ~/.config/autostart
cp -f NWS-Notify.desktop ~/.config/autostart
sed -i "s|~/.local|${HOME}/.local|g" ~/.config/autostart/NWS-Notify.desktop

mkdir -p ~/.local/bin
cp -f wx_check.sh ~/.local/bin/wx_check
chmod u+x ~/.local/bin/wx_check







sudo apt-get install wget espeak sox python3-pip zenity libxml2-dev libxslt-dev

# TO FIX URL REQUEST WARNINGS
#sudo pip3 install requests
#sudo python3 -m pip install --upgrade requests

pip3 install configparser
pip3 install feedparser
pip3 install capparselib
pip3 install numpy
pip3 install pandas
pip3 install pyqrcode
pip3 install pypng
pip3 install pyshorteners
pip3 install gTTS
