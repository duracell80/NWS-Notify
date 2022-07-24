sudo apt-get install wget espeak python3-pip

sudo pip3 install configparser
sudo pip3 install feedparser
sudo pip3 install capparselib
sudo pip3 install numpy
sudo pip3 install pandas
sudo pip3 install pyqrcode
sudo pip3 install pypng
sudo pip3 install pyshorteners


mkdir -p ~/.nws_alerts
mkdir -p /tmp/nws_data
sudo chmod a+x nws_watch.py
sudo chmod a+rw nws_seen.txt
sudo chmod a+x nws_alerts.sh
sudo chmod a+rw nws_data.xml
sudo chmod a+r config.ini


sudo mkdir -p /usr/share/nws_alerts
sudo cp nws_watch.py /usr/share/nws_alerts
sudo cp nws_alerts.sh /usr/share/nws_alerts
sudo cp nws_data.xml /tmp/nws_data.xml
sudo cp nws_data.xml /tmp/nws-nonus_data.xml
sudo cp config.ini /usr/share/nws_alerts
cp config.ini ~/.nws_alerts
cp nws_seen.txt /tmp
cp nws_seen.txt /tmp/nws-nonus_seen.txt
sudo cp web_server.py /usr/share/nws_alerts

cp NWS-Notify.desktop ~/.config/autostart
