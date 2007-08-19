#!/usr/bin/env python
import time
import sys
import socket
import bluetooth

import gtk
import gtk.glade

import mainwindow
import mobilephone

def main():
    #try:
        #discoverer = mobilephone.BluetoothDiscovery()
        #devices = discoverer.findSerialDevices()
        
        #device = mobilephone.BluetoothDevice("00:16:DB:67:D3:DA", 5, "Serial device")
        #phone = mobilephone.MobilePhone(device)
        #print phone.getManufacturer()
        #phone.getContacts()
        
        mainWindow = mainwindow.MainWindow()
        gtk.main()
        
    #except Exception, e:
    #   print e

if __name__ == "__main__":
    main()



