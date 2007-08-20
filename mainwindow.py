import gtk
import gtk.glade

import contacts
import mobilephone

class MainWindow:
    def __init__(self):
        self.__widgetTree           = gtk.glade.XML('phonetooth.glade')
        self.__mainWindow           = self.__widgetTree.get_widget('mainWindow')
        self.__recipientBox         = self.__widgetTree.get_widget('recipientBox')
        self.__manageContactsDialog = self.__widgetTree.get_widget('manageContactsDialog')
        self.__inputField           = self.__widgetTree.get_widget('textView')
        self.__contactsView         = self.__widgetTree.get_widget('contactsView')
                
        self.__contactlistStore = gtk.ListStore(str, str)

        self.__contactsView.set_model(self.__contactlistStore)
        
        renderer    = gtk.CellRendererText()
        renderer.editable = True
        
        nameColumn  = gtk.TreeViewColumn("Name", renderer, text = 0)
        nrColumn    = gtk.TreeViewColumn("Phone number", renderer, text = 1)
        
        self.__recipientBox.set_model(self.__contactlistStore)
        self.__contactsView.append_column(nameColumn)
        self.__contactsView.append_column(nrColumn)
        
        cell = gtk.CellRendererText()
        self.__recipientBox.pack_start (cell, False)
        self.__recipientBox.add_attribute (cell, 'text', 1)
                        
        self.__contactList = contacts.ContactList()
        self.__contactList.load()
        self.__updateContactStore()
        self.__recipientBox.set_active(0)
        
        dic = {'onMainWindowDestroy'            : gtk.main_quit,
               'onManageContactsActivated'      : self.__showManageContactsDialog,
               'onSendButtonClicked'            : self.__sendSMS,
               'onImportFromPhoneClicked'       : self.__importContacts,
               'onContactsViewKeyReleased'      : self.__contacsViewKeyReleased}
               
        self.__widgetTree.signal_autoconnect(dic)
        self.__mainWindow.show()
        
    def __showManageContactsDialog(self, widget):
        if  self.__manageContactsDialog.run() == 1:     
            self.__contactList.save()
                
        self.__manageContactsDialog.hide()
            
    def __updateContactStore(self, widget = 0):
        self.__contactlistStore.clear()
        
        contactNames = self.__contactList.contacts.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.__contactlistStore.append((contactName, self.__contactList.contacts[contactName]))

    def __sendSMS(self, widget):
        textBuffer = self.__inputField.get_buffer()
        listStore = self.__recipientBox.get_model()
        
        message = textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter())
        phoneNr = listStore[self.__recipientBox.get_active()][1]
        
        #phone = mobilephone.MobilePhone(mobilephone.BluetoothDevice("00:16:DB:67:D3:DA", 5))
        #phone.sendSMS(message, phoneNr)
        
    def __importContacts(self, widget):
        phone = mobilephone.MobilePhone(mobilephone.BluetoothDevice("00:16:DB:67:D3:DA", 5, "Serial device"))
        contacts = phone.getContacts()
        
        for contact in contacts:
            self.__contactList.addContact(contact)
            
        self.__updateContactStore()
        
    def __contacsViewKeyReleased(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE and event.keyval == 65535:
            (path, column) = self.__contactsView.get_cursor()
            iter = self.__contactlistStore.iter_nth_child(None, path[0])
            nameToDelete = self.__contactlistStore.get_value(iter, 0)
            del self.__contactList.contacts[nameToDelete]
            
            self.__updateContactStore()
            self.__contactsView.set_cursor(path)
        