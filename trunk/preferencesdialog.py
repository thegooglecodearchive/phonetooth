import gtk
import gtk.glade

import mobilephone

class PreferencesDialog:
    def __init__(self, widgetTree):
        self.__preferencesDialog = widgetTree.get_widget('preferencesDialog')
                
        dic = {'onScanButtonClicked' : self.__scanForDevices}
        widgetTree.signal_autoconnect(dic)
        
    def run(self, widget):
        if  self.__preferencesDialog.run() == 1:
            print 'Pref ok'
        else:
            print 'Pref cancel'
            
        self.__preferencesDialog.hide()
    
    def __scanForDevices(self, widget):
        print 'Scan for devices'
