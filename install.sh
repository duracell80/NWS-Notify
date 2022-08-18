DIR_LOCAL="$HOME/.local/share/nws_alerts"
mkdir -p $DIR_LOCAL
chmod u+rw $DIR_LOCAL

echo $DIR_LOCAL

mkdir -p ~/.local/share/nws_alerts
mkdir -p /tmp/nws_data
mkdir -p /tmp/qrcodes

sudo chmod a+rwx /tmp/nws_data/

sudo chmod a+x nws_watch.py
sudo chmod a+rw nws_seen.txt
sudo chmod a+x nws_alerts.sh
sudo chmod a+rw nws_data.xml
sudo chmod a+rw nws-nonus_seen.txt
sudo chmod a+r config.ini



cp nws_watch.py $DIR_LOCAL
cp nws_alerts.sh $DIR_LOCAL
sudo cp nws_data.xml /tmp/nws_data.xml
sudo cp nws_data.xml /tmp/nws-nonus_data.xml
cp config.ini ~/.local/share/nws_alerts
sudo cp nws_seen.txt /tmp
sudo cp nws_seen.txt /tmp/nws-nonus_seen.txt
#cp web_server.py $DIR_LOCAL

sudo chmod a+rw /tmp/nws-nonus_seen.txt
sudo chmod a+rw /tmp/nws-nonus_data.xml

sudo chmod a+rw /tmp/nws_seen.txt
sudo chmod a+rw /tmp/nws_data.xml

sed -i "s|#478db2|${MAINSHADE_HEX}|g" NWS-Notify.desktop

cp NWS-Notify.desktop ~/.config/autostart
sed -i "s|~/.local|${HOME}/.local|g" ~/.config/autostart/NWS-Notify.desktop

chmod u+x wx_check.sh
cp wx_check.sh ~/.local/bin/wx_check


sudo apt-get install wget espeak python3-pip zenity

sudo pip3 install configparser
sudo pip3 install feedparser
sudo pip3 install capparselib
sudo pip3 install numpy
sudo pip3 install pandas
sudo pip3 install pyqrcode
sudo pip3 install pypng
sudo pip3 install pyshorteners
