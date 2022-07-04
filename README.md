# NWS-Notify
Scripts to check the National Weather Service RSS Alert Feed for your state and publish found alerts from your county to the Linux Mint Notification panel. Also uses speaker-test to generate a sine wave and espeak to voice the found text.

## Install
```
cd ~/ && mkdir git && cd git
git clone https://github.com/duracell80/NWS-Notify.git && cd NWS-Notify
chmod u+x *.sh
./install.sh
```

## Run as a Service
Copy the service file to ...
