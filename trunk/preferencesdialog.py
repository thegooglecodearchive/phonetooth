import gtk
import gtk.glade

import mobilephone
import threading
import copy
import pickle
import os

class PreferencesDialog:
    def __init__(self, widgetTree):
        self.__preferencesDialog    = widgetTree.get_widget('preferencesDialog')
        self.__deviceSelecterBox    = widgetTree.get_widget('deviceSelecter')
        
        self.__deviceListStore = gtk.ListStore(str, str)
        self.__deviceSelecterBox.set_model(self.__deviceListStore)
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        self.__deviceSelecterBox.add_attribute (cell, 'text', 1)
                
        dic = {'onScanButtonClicked' : self.__scanForDevices}
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
                deviceAddress = self.__deviceListStore[activeItem][1]
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
        discoverer = mobilephone.BluetoothDiscovery()
        self.__setDevices(discoverer.findSerialDevices())
        
    def __setDevices(self, devices):
        self.__deviceList.clear()
        for device in devices:
            self.__deviceListStore.append((device.name, device.address))
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