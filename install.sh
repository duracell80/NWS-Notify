sudo apt-get install wget espeak python3-pip

sudo pip3 install configparser
sudo pip3 install feedparser
sudo pip3 install numpy
sudo pip3 install pandas
sudo pip3 install pyqrcode
sudo pip3 install pypng
sudo pip3 install pyshorteners
sudo pip3 install notify-send.py


mkdir -p ~/.nws_alerts
sudo chmod a+x nws_watch.py
sudo chmod a+rw nws_seen.txt
sudo chmod a+x nws_alerts.sh
sudo chmod a+x nws_alerts.service
sudo chmod a+rw nws_data.xml
sudo chmod a+r config.ini

sudo mkdir -p /usr/share/nws_alerts
sudo cp nws_watch.py /usr/share/nws_alerts
sudo cp nws_alerts.sh /usr/share/nws_alerts
sudo cp nws_data.xml /tmp/nws_data.xml
#sudo cp nws_alerts.service /etc/systemd/system
sudo cp config.ini /usr/share/nws_alerts
cp config.ini ~/.nws_alerts
cp nws_seen.txt /tmp
sudo cp web_server.py /usr/share/nws_alerts
#sudo systemctl daemon-reload
#sudo systemctl restart nws_alerts
