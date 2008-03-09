#    Copyright (C) 2008 Dirk Vanden Boer <dirk.vdb@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import gtk
import gtk.glade
import threading
import copy
import pickle
import os

from phonetooth import mobilephone
from phonetooth import bluetoothdiscovery

class PreferencesDialog:
    def __init__(self, parent, widgetTree):
        self.__parent = parent
        self.__preferencesDialog    = widgetTree.get_widget('preferencesDialog')
        self.__deviceSelecterBox    = widgetTree.get_widget('deviceSelecter')
        
        self.__deviceListStore = gtk.ListStore(str, str, str)
        self.__deviceSelecterBox.set_model(self.__deviceListStore)
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        self.__deviceSelecterBox.add_attribute (cell, 'text', 1)
                
        dic = { 'onScanButtonClicked'   : self.__scanForDevices,
                'onDeviceChanged'       : self.__parent.btDeviceChanged}
        widgetTree.signal_autoconnect(dic)
        
        
        self.btDevice = None
        self.__deviceList = {}
        self.__loadCurrentDevice()
        
        if self.btDevice != None:
            self.__setDevices([self.btDevice])
        
    def run(self, widget):
        oldDevice = copy.copy(self.btDevice)
        
        if  self.__preferencesDialog.run() == 1:
            activeItem = self.__deviceSelecterBox.get_active()
            if activeItem != -1:
                deviceAddress = self.__deviceListStore[activeItem][2]
                self.btDevice = self.__deviceList[deviceAddress]
                self.__saveCurrentDevice()
        else:
            self.__deviceListStore.clear()
            self.btDevice = oldDevice
            if self.btDevice != None:
                self.__setDevices([self.btDevice])
            
        self.__preferencesDialog.hide()
    
    def __scanForDevices(self, widget):
        self.__preferencesDialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.__deviceListStore.clear()
        self.__enableButtons(False)
        threading.Thread(target = self.__discoverThread).start()
        
    def __discoverThread(self):
        discoverer = bluetoothdiscovery.BluetoothDiscovery()
        self.__setDevices(discoverer.findSerialDevices())
        
    def __setDevices(self, devices):
        self.__deviceList.clear()
        for device in devices:
            self.__deviceListStore.append((device.deviceName, device.serviceName, device.address))
            self.__deviceList[device.address] = device
        
        self.__deviceSelecterBox.set_active(0)
        if self.__preferencesDialog.window != None:
            self.__preferencesDialog.window.set_cursor(None)
        self.__enableButtons(True)
        
    def __enableButtons(self, enable):
        self.__preferencesDialog.set_sensitive(enable)

    def __saveCurrentDevice(self):
        appDir = os.path.expanduser('~') + '/.phonetooth/'
        
        if not os.path.isdir(appDir):
            os.mkdir(appDir)
            
        file = open(appDir + 'device', 'wb')
        pickle.dump(self.btDevice, file)
        
    def __loadCurrentDevice(self):
        try:
            file = open(os.path.expanduser('~') + '/.phonetooth/device', 'rb')
            self.btDevice = pickle.load(file)
        except:
            self.btDevice = None
