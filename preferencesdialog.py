import gtk
import gtk.glade

import mobilephone
import threading

class PreferencesDialog:
    def __init__(self, widgetTree):
        self.__preferencesDialog    = widgetTree.get_widget('preferencesDialog')
        self.__deviceSelecterBox    = widgetTree.get_widget('deviceSelecter')
        self.__okButton             = widgetTree.get_widget('prefOkButton')
        self.__cancelButton         = widgetTree.get_widget('prefCancelButton')
        self.__scanButton         = widgetTree.get_widget('scanButton')
        
        self.__contactlistStore = gtk.ListStore(str)
        self.__deviceSelecterBox.set_model(self.__contactlistStore)
        
        cell = gtk.CellRendererText()
        self.__deviceSelecterBox.pack_start(cell, False)
        
        dic = {'onScanButtonClicked' : self.__scanForDevices}
        widgetTree.signal_autoconnect(dic)
        
        gtk.gdk.threads_init()
        
    def run(self, widget):
        if  self.__preferencesDialog.run() == 1:
            print 'Pref ok'
        else:
            print 'Pref cancel'
            
        self.__preferencesDialog.hide()
    
    def __scanForDevices(self, widget):
        self.__preferencesDialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.__contactlistStore.clear()
        self.__enableButtons(False)
        threading.Thread(target = self.__discoverThread).start()
        
    def __discoverThread(self):
        discoverer = mobilephone.BluetoothDiscovery()
        self.__setDevices(discoverer.findSerialDevices())
        
    def __setDevices(self, devices):
        print 'set devices'
        for device in devices:
            self.__contactlistStore.append([device.name])
        
        self.__deviceSelecterBox.set_active(0)
        self.__preferencesDialog.window.set_cursor(None)
        self.__enableButtons(True)
        
    def __enableButtons(self, enable):
        self.__okButton.set_sensitive(enable)
        self.__cancelButton.set_sensitive(enable)
        self.__scanButton.set_sensitive(enable)
