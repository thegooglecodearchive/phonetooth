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
                
        self.__contactlistStore = gtk.ListStore(str, str)

        self.__recipientBox.set_model(self.__contactlistStore)
        cell = gtk.CellRendererText()
        self.__recipientBox.pack_start (cell, True)
        self.__recipientBox.add_attribute (cell, 'text', 1)
                        
        self.__contactList = contacts.ContactList()
        self.__contactList.load()
        
        self.__updateContactStore()
        self.__recipientBox.set_active(0)
        
        dic = {'on_mainWindow_destroy' : gtk.main_quit,
               'onManageContactsActivated' : self.__showManageContactsDialog,
               'onSendButtonClicked' : self.__sendSMS,
               'onImportFromPhoneClicked' : self.__importContacts}
               
        self.__widgetTree.signal_autoconnect(dic)
        self.__mainWindow.show()
        
    def __showManageContactsDialog(self, widget):
        contactsView = self.__widgetTree.get_widget('contactsView')
        contactsView.set_model(self.__contactlistStore)
        
        renderer    = gtk.CellRendererText()
        nameColumn  = gtk.TreeViewColumn("Name", renderer, text=0)
        nrColumn    = gtk.TreeViewColumn("Phone number", renderer, text=1)
        
        contactsView.append_column(nameColumn)
        contactsView.append_column(nrColumn)
        
        if  self.__manageContactsDialog.run() == 1:     
            self.__contactList.save()
                
        self.__manageContactsDialog.hide()
            
    def __updateContactStore(self, widget = 0):
        self.__contactlistStore.clear()
        
        for contactName in self.__contactList.contacts:
            self.__contactlistStore.append((contactName, self.__contactList.contacts[contactName]))

    def __updateContactsModel(self):
        self.__contactModel.clear()
        
        iter = None
        for contact in self.__contactList.contacts:
            iter = self.__contactModel.insert_after(None, iter, (contact.name, contact.phoneNumber))
    
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
        