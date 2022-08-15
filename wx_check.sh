#!/usr/bin/env bash

touch /tmp/nws-nonus_seen.txt

notify-send --urgency=low --category=im.received --icon=help-info-symbolic "NWS Notify - Checking For Weather Alerts" "Your weather alert feeds are now being checked, standby for alerts if any ..."

$HOME/.local/share/nws_alerts/nws_watch.py