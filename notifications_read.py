#!/usr/bin/env python3
import array
import gi.repository.GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

global notification_list
notification_list = ""

def notifications(bus, message):
    # do your magic
    for arg in message.get_args_list(): 
        if "dbus" not in str(arg) and str(arg) != "0" and str(arg) != "-1" and str(arg) != "" and int(len(str(arg))) > 6 :
            print(str(arg).replace("notify-send", "Notifcation"))
            
DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
bus.add_message_filter(notifications)

mainloop = gi.repository.GLib.MainLoop()
mainloop.run()