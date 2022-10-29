#!/usr/bin/env python3
import array, os, time

import gi.repository.GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

def notifications(bus, message):
    c = 0; msg = []
    for arg in message.get_args_list(): 
        if "dbus" not in str(arg) and str(arg) != "0" and str(arg) != "-1" and str(arg) != "" and int(len(str(arg))) > 6 :
            msg.append(str(arg))
            c+=1
            
    dat = str(int(time.time()))
    out = dat + "::" + msg[0].lower() + "::" + msg[1] + "::" + msg[2]
    
    print(out)
    os.system("echo " + out + " >> /home/lee/.cache/alerts_history.txt")
    
DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
bus.add_message_filter(notifications)

mainloop = gi.repository.GLib.MainLoop()
mainloop.run()