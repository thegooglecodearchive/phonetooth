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

from gettext import gettext as _

class SelectContactsDialog:
    def __init__(self, widgetTree, parent = None):
        self.__contactListStore = gtk.ListStore(bool, str, str)
        
        self.__contactsDialog       = widgetTree.get_widget('contactSelectionDialog')
        self.__contactsView         = widgetTree.get_widget('contactSelectionView')
        self.__okButton             = widgetTree.get_widget('contactOkButton')
        
        self.__contactsDialog.set_transient_for(parent)
        
        checkRenderer = gtk.CellRendererToggle()
        checkRenderer.set_property('activatable', True)
        checkRenderer.connect('toggled', self.__contactToggledCb)
        
        textRenderer = gtk.CellRendererText()
        textRenderer.set_property('editable', False)
        
        self.__checkColumn = gtk.TreeViewColumn(None, checkRenderer, active = 0)
        self.__nameColumn  = gtk.TreeViewColumn(_("Name"), textRenderer, text = 1)
        self.__nrColumn    = gtk.TreeViewColumn(_("Phone number"), textRenderer, text = 2)
        
        self.__contactsView.set_model(self.__contactListStore)
        self.__contactsView.append_column(self.__checkColumn)
        self.__contactsView.append_column(self.__nameColumn)
        self.__contactsView.append_column(self.__nrColumn)
        
        
    def run(self):
        contactList = contacts.ContactList()
        contactList.load()
        self.__updateStoreFromContactList(contactList)
        
        selectedContacts = None
        
        if  self.__contactsDialog.run() == gtk.RESPONSE_OK:
            selectedContacts = self.__getContactListFromStore()
        
        self.__contactsDialog.hide()
        return selectedContacts
        

    def __getContactListFromStore(self):
        contactList = contacts.ContactList()
        iter = self.__contactListStore.get_iter_first()
        
        while iter != None:
            if self.__contactListStore.get_value(iter, 0) == True:
                name    = self.__contactListStore.get_value(iter, 1)
                nr      = self.__contactListStore.get_value(iter, 2)
            
                contactList.addContact(contacts.Contact(name, nr))
            iter = self.__contactListStore.iter_next(iter)
            
        return contactList
        
    
    def __updateStoreFromContactList(self, contactList):
        self.__contactListStore.clear()
        
        contactNames = contactList.contacts.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.__contactListStore.append((False, contactName, contactList.contacts[contactName]))
            
    
    def __contactToggledCb(self, cellrenderer, path):
        iter            = self.__contactListStore.iter_nth_child(None, int(path))
        checked         = self.__contactListStore.get_value(iter, 0)
        
        self.__contactListStore.set_value(iter, 0, not checked)
        self.__checkOkButtonSensitivity()
        
    
    def __checkOkButtonSensitivity(self):
        iter = self.__contactListStore.get_iter_first()
        
        sensitive = False
        while iter != None:
            if self.__contactListStore.get_value(iter, 0) == True:
                sensitive = True
                break
                
            iter = self.__contactListStore.iter_next(iter)
            
        self.__okButton.set_sensitive(sensitive)
