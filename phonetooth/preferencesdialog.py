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
import os
import ConfigParser

from phonetooth import mobilephone
from phonetooth import bluetoothdiscovery

class PreferencesDialog:
    def __init__(self, parent, widgetTree):
        self.__parent = parent
        self.__preferencesDialog    = widgetTree.get_widget('preferencesDialog')
        self.__deviceSelecterBox    = widgetTree.get_widget('deviceSelecter')
        self.__backendSelecterBox   = widgetTree.get_widget('backendSelecter')
        
        self.__deviceListStore = gtk.ListStore(str, str, str)
        self.__deviceSelecterBox.set_model(self.__deviceListStore)
        
        self.__backendListStore = gtk.ListStore(str)
        self.__backendSelecterBox.set_model(self.__backendListStore)
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        self.__backendListStore.append(('Phonetooth',))
        
        self.__gammuAvailable = False
        
        try:
            import gammu
            self.__gammuAvailable = True
            self.__backendListStore.append(('Gammu',))
        except:
            print 'python-gammu not found'
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        self.__deviceSelecterBox.add_attribute (cell, 'text', 1)
                
        dic = { 'onScanButtonClicked'   : self.__scanForDevices,
                'onDeviceChanged'       : self.__parent.btDeviceChanged}
        widgetTree.signal_autoconnect(dic)
        
        
        self.backend = 'phonetooth'
        self.btDevice = None
        self.__deviceList = []
        self.__loadPreferences()
        
        if self.btDevice != None:
            self.__setDevices([self.btDevice])
        
    def run(self, widget):
        oldDevice = copy.copy(self.btDevice)
        oldBackend = self.__backendSelecterBox.get_active()
        
        if  self.__preferencesDialog.run() == 1:
            activeItem = self.__deviceSelecterBox.get_active()
            if activeItem != -1:
                deviceAddress = self.__deviceListStore[activeItem][2]
                serviceName = self.__deviceListStore[activeItem][1]
                self.btDevice = self.__getDevice(deviceAddress, serviceName)
                
            if self.__backendSelecterBox.get_active() == 1:
                self.backend = 'gammu'
            else:
                self.backend = 'phonetooth'
                
            self.__savePreferences()
        else:
            self.__deviceListStore.clear()
            self.btDevice = oldDevice
            if self.btDevice != None:
                self.__setDevices([self.btDevice])
            self.__backendSelecterBox.set_active(oldBackend)
            
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
        self.__deviceList = devices
        for device in self.__deviceList:
            self.__deviceListStore.append((device.deviceName, device.serviceName, device.address))
        
        self.__deviceSelecterBox.set_active(0)
        if self.__preferencesDialog.window != None:
            self.__preferencesDialog.window.set_cursor(None)
        self.__enableButtons(True)
        
    
    def __getDevice(self, deviceAddress, serviceName):
        for device in self.__deviceList:
            if device.address == deviceAddress and device.serviceName == serviceName:
                return device
                
        raise Exception, 'Device not found'
        
    
    def __enableButtons(self, enable):
        self.__preferencesDialog.set_sensitive(enable)

    
    def __savePreferences(self):
        appDir = os.path.expanduser('~/.phonetooth')
        
        if not os.path.isdir(appDir):
            os.mkdir(appDir)
        
        config = ConfigParser.ConfigParser()
        config.add_section('preferences')
        
        config.set('preferences', 'backend', self.backend)
        
        if self.btDevice != None:
            config.set('preferences', 'address', self.btDevice.address)
            config.set('preferences', 'port', str(self.btDevice.port))
            config.set('preferences', 'deviceName', self.btDevice.deviceName)
            config.set('preferences', 'serviceName', self.btDevice.serviceName)
        
        preferenceFile = os.path.join(appDir, 'config')
        config.write(open(preferenceFile, 'w'))
        
    
    def __loadPreferences(self):
        try:
            preferenceFile = os.path.join(os.path.expanduser('~/.phonetooth'), 'config')
            config = ConfigParser.ConfigParser()
            openedFiles = config.read(preferenceFile)
            
            if len(openedFiles) == 0:
                raise Exception, 'No config file found'
                
            try:
                self.btDevice = bluetoothdiscovery.BluetoothDevice(
                config.get('preferences', 'address'),
                int(config.get('preferences', 'port')),
                config.get('preferences', 'deviceName'),
                config.get('preferences', 'serviceName'))
            except:
                self.btDevice == None
                
            self.backend = config.get('preferences', 'backend')
            if self.backend == 'phonetooth':
                self.__backendSelecterBox.set_active(0)
            elif self.backend == 'gammu' and self.__gammuAvailable == True:
                self.__backendSelecterBox.set_active(1)
            else:
                self.backend = 'phonetooth'
                self.__backendSelecterBox.set_active(0)

        except Exception, e:
            print 'Load config failed: ' + str(e) + ' (reverting to defaults)'
            self.btDevice = None
            self.__backendSelecterBox.set_active(0)
