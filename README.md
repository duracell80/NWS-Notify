# NWS-Notify
Scripts to check the National Weather Service RSS Alert Feed for your state and publish found alerts from your county to the Linux Mint Notification panel. Also uses speaker-test to generate a sine wave and espeak to voice the found text.

## Install
```
$ cd ~/ && mkdir git && cd git
$ git clone https://github.com/duracell80/NWS-Notify.git && cd NWS-Notify
$ chmod u+x *.sh
$ ./install.sh
```

## Run in user Crontab
Edit your crontab. There is a 15 minute auto backoff to protect the NWS servers.
```
$ crontab -e
```

Add an entry to run every 5 minutes
```
*/5  * * * * python3 /usr/share/nws_alerts/nws_watch.py
```

Save the file then restart cron                       
```
$ sudo service cron restart
```

## Run as a Service
Running service as root may case sound notification to fail

