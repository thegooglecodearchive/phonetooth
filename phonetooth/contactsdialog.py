import gobject
import gtk
import gtk.glade
import threading

from phonetooth import contacts
from phonetooth import mobilephone

class ContactsDialog:
    def __init__(self, widgetTree, contactListStore, btDevice):
        self.__contactlistStore = contactListStore
        self.btDevice = btDevice
        
        self.__contactsDialog       = widgetTree.get_widget('manageContactsDialog')
        self.__contactsView         = widgetTree.get_widget('contactsView')
        
        dic = { 'onImportFromPhoneClicked'       : self.__importPhoneContacts,
                'onImportFromSimClicked'         : self.__importSimContacts,
                'onContactsViewKeyReleased'      : self.__contacsViewKeyReleased,
                'onNewClicked'                   : self.__addContactRow}
               
        widgetTree.signal_autoconnect(dic)
        
        nameRenderer = gtk.CellRendererText()
        nameRenderer.set_property('editable', True)
        nameRenderer.connect('edited', self.__contactEditedCb, 0)
        
        nrRenderer = gtk.CellRendererText()
        nrRenderer.set_property('editable', True)
        nrRenderer.connect('edited', self.__contactEditedCb, 1)
        
        self.__nameColumn  = gtk.TreeViewColumn("Name", nameRenderer, text = 0)
        self.__nrColumn    = gtk.TreeViewColumn("Phone number", nrRenderer, text = 1)
        
        self.__contactsView.set_model(self.__contactlistStore)
        self.__contactsView.append_column(self.__nameColumn)
        self.__contactsView.append_column(self.__nrColumn)
        
    def run(self, widget):
        contactsBackup = self.__createContactListFromStore()
        
        if  self.__contactsDialog.run() == 1:
            self.__createContactListFromStore().save()
        else:
            self.updateStoreFromContactList(contactsBackup)
                
        self.__contactsDialog.hide()
        
    def __createContactListFromStore(self):
        contactList = contacts.ContactList()
        iter = self.__contactlistStore.get_iter_first()
        
        while iter != None:
            name    = self.__contactlistStore.get_value(iter, 0)
            nr      = self.__contactlistStore.get_value(iter, 1)
            
            contactList.addContact(contacts.Contact(name, nr))
            iter = self.__contactlistStore.iter_next(iter)
            
        return contactList
        
    def updateStoreFromContactList(self, contactList):
        self.__contactlistStore.clear()
        
        contactNames = contactList.contacts.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.__contactlistStore.append((contactName, contactList.contacts[contactName]))
            
    def __importPhoneContacts(self, widget):
        self.__setSensitive(False)
        threading.Thread(target = self.__importContactsThread, args = ('PHONE',)).start()
        
    def __importSimContacts(self, widget):
        self.__setSensitive(False)
        threading.Thread(target = self.__importContactsThread, args = ('SIM',)).start()

    def __importContactsThread(self, location):
        try:
            phone = mobilephone.MobilePhone(self.btDevice)
            phoneContacts   = phone.getContacts(location)
            contactList     = self.__createContactListFromStore()
        
            for contact in phoneContacts:
                contactList.contacts[contact.name] = contact.phoneNumber
            
            self.updateStoreFromContactList(contactList)
        except Exception, e:
            gobject.idle_add(self.__error, str(e))
       
        gobject.idle_add(self.__setSensitive, True)
        
    def __contacsViewKeyReleased(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE and event.keyval == gtk.keysyms.Delete:
            (path, column) = self.__contactsView.get_cursor()
            if path != None:
                iter = self.__contactlistStore.iter_nth_child(None, path[0])
                nameToDelete = self.__contactlistStore.get_value(iter, 0)
                
                contactList = self.__createContactListFromStore()
                del contactList.contacts[nameToDelete]
                self.updateStoreFromContactList(contactList)

                self.__contactsView.set_cursor(path)
                
    def __contactEditedCb(self, cell, path, newText, column):
        iter        = self.__contactlistStore.iter_nth_child(None, int(path))
        currentName = self.__contactlistStore.get_value(iter, 0)
        contactList = self.__createContactListFromStore()
        
        if column == 0:
            del contactList.contacts[currentName]
            currentNr = self.__contactlistStore.get_value(iter, 1)
            contactList.contacts[newText] = currentNr
        else:
            contactList.contacts[currentName] = newText
            
        self.updateStoreFromContactList(contactList)
        self.__contactsView.set_cursor(path)
        
    def __addContactRow(self, widget):
        contactList = self.__createContactListFromStore()
        contactList.contacts[''] = ''
        
        self.updateStoreFromContactList(contactList)
        self.__contactsView.set_cursor(0, focus_column = self.__nameColumn, start_editing = True)
        
    def __error(self, message):
        errorDlg = gtk.MessageDialog(parent=self.__contactsDialog, type=gtk.MESSAGE_ERROR, message_format=message, buttons=gtk.BUTTONS_OK)
        errorDlg.run()
        errorDlg.destroy()
        self.__contactsDialog.set_sensitive(True)
        self.__contactsDialog.window.set_cursor(None)
        
    def __setSensitive(self, sensitive):
        if sensitive == True:
            self.__contactsDialog.set_sensitive(True)
            self.__contactsDialog.window.set_cursor(None)
        else:
            self.__contactsDialog.set_sensitive(False)
            self.__contactsDialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
