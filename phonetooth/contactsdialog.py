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

import gobject
import gtk
import gtk.glade
import threading

from phonetooth import contacts
from phonetooth import mobilephone
from phonetooth import mobilephonegammu
from phonetooth import mobilephonefactory
from phonetooth import mergecontactsdialog

from gettext import gettext as _

class ContactsDialog:
    contactList = contacts.ContactList()
    
    def __init__(self, widgetTree, prefs, parent = None):
        self.contactList.load()
        
        self.contactlistStore = gtk.ListStore(str, str)
        self.__updateStoreFromContactList()
       
        self.__prefs = prefs
        
        self.__contactsDialog       = widgetTree.get_widget('manageContactsDialog')
        self.__contactsView         = widgetTree.get_widget('contactsView')
        
        self.__contactsDialog.set_transient_for(parent)
        
        self.__mergeContactsDialog = mergecontactsdialog.MergeContactsDialog(widgetTree, parent = self.__contactsDialog)
        
        dic = { 'onImportFromPhoneClicked'       : self.__importPhoneContacts,
                'onImportFromSimClicked'         : self.__importSimContacts,
                'onContactsViewKeyReleased'      : self.__contacsViewKeyReleased,
                'onNewClicked'                   : self.__addContactRow,
                'onExportContacts'               : self.__exportContacts,
                'onImportContacts'               : self.__importContacts
        }
               
        widgetTree.signal_autoconnect(dic)
        
        nameRenderer = gtk.CellRendererText()
        nameRenderer.set_property('editable', True)
        nameRenderer.connect('edited', self.__contactEditedCb, 0)
        
        nrRenderer = gtk.CellRendererText()
        nrRenderer.set_property('editable', True)
        nrRenderer.connect('edited', self.__contactEditedCb, 1)
        
        self.__nameColumn  = gtk.TreeViewColumn(_("Name"), nameRenderer, text = 0)
        self.__nrColumn    = gtk.TreeViewColumn(_("Phone number"), nrRenderer, text = 1)
        
        self.__contactsView.set_model(self.contactlistStore)
        self.__contactsView.append_column(self.__nameColumn)
        self.__contactsView.append_column(self.__nrColumn)
        
        
    def run(self, widget):
        if  self.__contactsDialog.run() == 1:
            self.__updateContactListFromStore()
            self.contactList.save()
        else:
            self.contactList.load()
            self.__updateStoreFromContactList()
        self.__contactsDialog.hide()
        

    def __updateContactListFromStore(self):
        self.contactList = contacts.ContactList()
        iter = self.contactlistStore.get_iter_first()
        
        while iter != None:
            name    = self.contactlistStore.get_value(iter, 0)
            nr      = self.contactlistStore.get_value(iter, 1)
            
            self.contactList.addContact(contacts.Contact(name, nr))
            iter = self.contactlistStore.iter_next(iter)
        
    
    def __updateStoreFromContactList(self):
        self.contactlistStore.clear()
        
        contactNames = self.contactList.contacts.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.contactlistStore.append((contactName, self.contactList.contacts[contactName]))
            
    
    def __importPhoneContacts(self, widget):
        self.__setSensitive(False)
        threading.Thread(target = self.__importContactsFromPhoneThread, args = ('PHONE',)).start()
        
    
    def __importSimContacts(self, widget):
        self.__setSensitive(False)
        threading.Thread(target = self.__importContactsFromPhoneThread, args = ('SIM',)).start()

    
    def __importContactsFromPhoneThread(self, location):
        try:
            phone = mobilephonefactory.createPhone(self.__prefs)
            phone.connect()

            phoneContacts   = phone.getContacts(location)
            for contact in phoneContacts:
                self.contactList.contacts[contact.name] = contact.phoneNumber
            
            gtk.gdk.threads_enter()
            self.__updateStoreFromContactList()
            gtk.gdk.threads_leave()
        except Exception, e:
            gtk.gdk.threads_enter()
            self.__error(str(e))
            gtk.gdk.threads_leave()
        finally:
            gobject.idle_add(self.__setSensitive, True)
        
        
    def __exportContacts(self, widget):
        chooser = gtk.FileChooserDialog(title = None, action = gtk.FILE_CHOOSER_ACTION_SAVE,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                    
        filter = gtk.FileFilter()
        filter.add_pattern("*.csv")
        chooser.set_filter(filter)
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            if not filename.endswith('.csv'):
                filename += '.csv'
            self.contactList.save(filename)
        chooser.hide()
        
        
    def __importContacts(self, widget):
        chooser = gtk.FileChooserDialog(title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
                    
        filter = gtk.FileFilter()
        filter.add_pattern("*.csv")
        chooser.set_filter(filter)
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            chooser.hide()
            importedList = contacts.ContactList()
            importedList.load(chooser.get_filename())
            
            collisions = self.contactList.findCollisions(importedList)
            if len(collisions) > 0:
                resolvedCollisions = self.__mergeContactsDialog.run(collisions)

                if resolvedCollisions != None:
                    self.contactList.mergeContacts(importedList, resolvedCollisions)
            else:
                self.contactList.mergeContacts(importedList)
            
        self.__updateStoreFromContactList()
        chooser.destroy()
        

    def __contacsViewKeyReleased(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE and event.keyval == gtk.keysyms.Delete:
            (path, column) = self.__contactsView.get_cursor()
            if path != None:
                iter = self.contactlistStore.iter_nth_child(None, path[0])
                nameToDelete = self.contactlistStore.get_value(iter, 0)
                del self.contactList.contacts[nameToDelete]
                self.__updateStoreFromContactList()
                self.__contactsView.set_cursor(path)
                

    def __contactEditedCb(self, cell, path, newText, column):
        iter        = self.contactlistStore.iter_nth_child(None, int(path))
        currentName = self.contactlistStore.get_value(iter, 0)
        self.__updateContactListFromStore()
        
        if column == 0:
            del self.contactList.contacts[currentName]
            currentNr = self.contactlistStore.get_value(iter, 1)
            self.contactList.contacts[newText] = currentNr
        else:
            self.contactList.contacts[currentName] = newText
            
        self.__updateStoreFromContactList()
        self.__contactsView.set_cursor(path)
        

    def __addContactRow(self, widget):
        self.contactList.contacts[''] = ''
        self.__updateStoreFromContactList()
        self.__contactsView.set_cursor(0, focus_column = self.__nameColumn, start_editing = True)
        

    def __error(self, message):
        errorDlg = gtk.MessageDialog(parent=self.__contactsDialog, type=gtk.MESSAGE_ERROR, message_format=message, buttons=gtk.BUTTONS_OK)
        errorDlg.set_title(_('Error'))
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
