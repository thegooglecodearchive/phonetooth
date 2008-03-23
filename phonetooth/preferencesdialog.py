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

from phonetooth import mobilephone
from phonetooth import preferences
from phonetooth import bluetoothdiscovery


from gettext import gettext as _

class PreferencesDialog:
    def __init__(self, widgetTree, prefs):
        self.__preferencesDialog    = widgetTree.get_widget('preferencesDialog')
        self.__deviceSelecterBox    = widgetTree.get_widget('deviceSelecter')
        self.__customDeviceEntry    = widgetTree.get_widget('customDeviceEntry')
        self.__gammuIndexSpinBox    = widgetTree.get_widget('configIndexSpinButton')
        self.__btRadio              = widgetTree.get_widget('bluetoothRadio')
        self.__customDeviceRadio    = widgetTree.get_widget('customDeviceRadio')
        self.__gammuRadio           = widgetTree.get_widget('gammuRadio')
        
        self.__deviceListStore = gtk.ListStore(str, str, str)
        self.__deviceSelecterBox.set_model(self.__deviceListStore)
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        
        self.__gammuAvailable = False
        
        try:
            import gammu
            self.__gammuAvailable = True
        except:
            print 'python-gammu not found'
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        self.__deviceSelecterBox.add_attribute (cell, 'text', 1)
                
        dic = { 'onScanButtonClicked'   : self.__scanForDevices }
        widgetTree.signal_autoconnect(dic)
        
        self.__prefs = prefs
        self.__applyPreferences()
        
    
    def run(self, widget):
        if  self.__preferencesDialog.run() == 1:
            activeItem = self.__deviceSelecterBox.get_active()
            if activeItem != -1:
                deviceAddress = self.__deviceListStore[activeItem][2]
                serviceName = self.__deviceListStore[activeItem][1]
                self.__prefs.btDevice = self.__getDevice(deviceAddress, serviceName)

            self.__prefs.customDevice = self.__customDeviceEntry.get_text()
            self.__prefs.gammuIndex = int(self.__gammuIndexSpinBox.get_value())
                
            if self.__btRadio.get_active() == True:
                self.__prefs.connectionMethod = 'bluetooth'
            elif self.__customDeviceRadio.get_active() == True:
                self.__prefs.connectionMethod = 'customDevice'
            else:
                self.__prefs.connectionMethod = 'gammu'
                
            self.__prefs.save()
        else:
            self.__prefs.load()
            self.__applyPreferences()
            
        self.__preferencesDialog.hide()
    
    
    def __scanForDevices(self, widget):
        self.__preferencesDialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.__deviceListStore.clear()
        self.__enableButtons(False)
        threading.Thread(target = self.__discoverThread).start()
        
    
    def __discoverThread(self):
        discoverer = bluetoothdiscovery.BluetoothDiscovery()
        self.__setDevices(discoverer.findSerialDevices())
        
    
    def __applyPreferences(self):
        self.__deviceListStore.clear()
        if self.__prefs.btDevice != None:
            self.__setDevices([self.__prefs.btDevice])
            
        if self.__prefs.connectionMethod == 'bluetooth':
            self.__btRadio.set_active(True)
        elif self.__prefs.connectionMethod == 'customDevice':
            self.__customDeviceRadio.set_active(True)
        elif self.__prefs.connectionMethod == 'gammu':
            self.__gammuRadio.set_active(True)
        else:
            print 'Invalid connection method in preferences'
            self.__btRadio.set_active(True)
        
        self.__customDeviceEntry.set_text(self.__prefs.customDevice)
        self.__gammuIndexSpinBox.set_value(self.__prefs.gammuIndex)
            

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
                
        raise Exception, _('Device not found')
        
    
    def __enableButtons(self, enable):
        self.__preferencesDialog.set_sensitive(enable)
