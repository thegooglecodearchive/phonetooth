import gtk
import gobject
import gtk.glade
import os
import threading
import bluetooth

from phonetooth import contacts
from phonetooth import mobilephone
from phonetooth import contactsdialog
from phonetooth import preferencesdialog
from phonetooth import constants

class MainWindow:
    def __init__(self):
        self.__widgetTree           = gtk.glade.XML(os.path.join(constants.datadir, 'phonetooth.glade'))
        self.__mainWindow           = self.__widgetTree.get_widget('mainWindow')
        self.__recipientBox         = self.__widgetTree.get_widget('recipientBox')
        self.__inputField           = self.__widgetTree.get_widget('textView')
        self.__charactersLabel      = self.__widgetTree.get_widget('charactersLabel')
        self.__sendButton           = self.__widgetTree.get_widget('sendButton')
        self.__aboutDialog          = self.__widgetTree.get_widget('aboutDialog')
        self.__statusBar            = self.__widgetTree.get_widget('statusBar')
        
        self.__aboutDialog.set_name('PhoneTooth')
        self.__sendButton.set_sensitive(False)
                
        self.__contactlistStore = gtk.ListStore(str, str)
        self.__recipientBox.set_model(self.__contactlistStore)
        
        cell = gtk.CellRendererText()
        self.__recipientBox.pack_start (cell, False)
        self.__recipientBox.add_attribute (cell, 'text', 1)
        
        contactList = contacts.ContactList()
        contactList.load()        
        
        self.__contactsDialog = contactsdialog.ContactsDialog(self.__widgetTree, self.__contactlistStore)
        self.__contactsDialog.updateStoreFromContactList(contactList)
        
        self.__preferencesDialog = preferencesdialog.PreferencesDialog(self.__widgetTree)
        
        self.__recipientBox.set_active(0)
        
        
        dic = {'onMainWindowDestroy'            : gtk.main_quit,
               'onManageContactsActivated'      : self.__contactsDialog.run,
               'onPreferencesActivated'         : self.__preferencesDialog.run,
               'onSendButtonClicked'            : self.__sendSMS,
               'onKeyPressedInMessage'          : self.__updateNrCharacters,
               'onAboutButtonClicked'           : self.__showAboutDialog}
        self.__widgetTree.signal_autoconnect(dic)
        
        gtk.gdk.threads_init()
        gtk.window_set_default_icon_from_file(os.path.join(constants.datadir, 'phonetooth-small.svg'))
        
        self.__mainWindow.show()
        
    def __updateContactStore(self, widget = 0):
        self.__contactlistStore.clear()
        
        contactNames = self.__contactListBeingEdited.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.__contactlistStore.append((contactName, self.__contactListBeingEdited[contactName]))
            
    def __sendSMS(self, widget):
        self.__mainWindow.set_sensitive(False)
        self.__mainWindow.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        threading.Thread(target = self.__sendSMSThread).start()

    def __sendSMSThread(self):
        textBuffer = self.__inputField.get_buffer()
        listStore = self.__recipientBox.get_model()
        
        message = textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter())
        phoneNr = listStore[self.__recipientBox.get_active()][1]
        
        try:
            if self.__preferencesDialog.btDevice != None:
                phone = mobilephone.MobilePhone(self.__preferencesDialog.btDevice)
                phone.sendSMS(message, phoneNr)
                self.__pushStatusText('Message succesfully sent.')
            else:
                self.__pushStatusText('You need to configure a device first. Check the preferences.')
        except Exception, e:
            self.__pushStatusText('Failed to send message: ' + str(e))
            
        self.__mainWindow.set_sensitive(True)
        self.__mainWindow.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
            
    def __updateNrCharacters(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE:
            nrCharacters = self.__inputField.get_buffer().get_char_count()
            self.__charactersLabel.set_text('Characters: ' + str(nrCharacters))
            
            self.__sendButton.set_sensitive(nrCharacters != 0)
            
    def __showAboutDialog(self, widget, dummy):
        self.__aboutDialog.run()
        self.__aboutDialog.hide()
        
    def __pushStatusText(self, message):
        self.__statusBar.push(0, message)
    