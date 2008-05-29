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

class MergeContactsDialog:
    def __init__(self, widgetTree, parent = None):
        self.__mergeContactsDialog  = widgetTree.get_widget('mergeContactsDialog')
        self.__collisionView        = widgetTree.get_widget('collisionView')
        
        self.collisionlistStore = gtk.ListStore(str, bool, str, bool, str)
        
        nameRenderer = gtk.CellRendererText()
        nameRenderer.set_property('editable', False)
        
        nrRenderer = gtk.CellRendererText()
        nrRenderer.set_property('editable', False)
        
        checkRenderer = gtk.CellRendererToggle()
        checkRenderer.set_property('activatable', True)
        checkRenderer.connect('toggled', self.__numberToggledCb)
        
        self.__nameColumn   = gtk.TreeViewColumn(_("Name"), nameRenderer, text = 0)
        self.__nrColumn1    = gtk.TreeViewColumn(_("Existing number"), nrRenderer, text = 2)
        self.__nrColumn2    = gtk.TreeViewColumn(_("Imported number"), nrRenderer, text = 4)
        self.__checkColumn1 = gtk.TreeViewColumn(None, checkRenderer, active = 1)
        self.__checkColumn2 = gtk.TreeViewColumn(None, checkRenderer, active = 3)
        
        self.__collisionView.set_model(self.collisionlistStore)
        self.__collisionView.append_column(self.__nameColumn)
        self.__collisionView.append_column(self.__checkColumn1)
        self.__collisionView.append_column(self.__nrColumn1)
        self.__collisionView.append_column(self.__checkColumn2)
        self.__collisionView.append_column(self.__nrColumn2)
        
        self.__mergeContactsDialog.set_transient_for(parent)
        
        dic = {
            'onOverwriteToggled'     : self.__overwriteModeToggled,
            'onSkipModeToggled'      : self.__skipModeSkipToggled
        }
        widgetTree.signal_autoconnect(dic)
        

    def run(self, collisions):
        resolvedCollisions = None
        self.__updateListStore(collisions)
        if  self.__mergeContactsDialog.run() == 1:
            resolvedCollisions = self.__getResolvedContacts()
        self.__mergeContactsDialog.hide()

        return resolvedCollisions
        

    def __updateListStore(self, collisions):
        self.collisionlistStore.clear()
        
        for collision in collisions:
            self.collisionlistStore.append((collision.name, False, collision.phoneNumber1, False, collision.phoneNumber2))

        self.__applySkipMode()
            
    
    def __numberToggledCb(self, cellrenderer, path):
        iter            = self.collisionlistStore.iter_nth_child(None, int(path))
        number1Enabled  = self.collisionlistStore.get_value(iter, 1)
        
        self.collisionlistStore.set_value(iter, 1, not number1Enabled)
        self.collisionlistStore.set_value(iter, 3, number1Enabled)


    def __applyOverwriteMode(self):
        iter = self.collisionlistStore.get_iter_first()
        
        while iter != None:
            self.collisionlistStore.set_value(iter, 1, False)
            self.collisionlistStore.set_value(iter, 3, True)
            iter = self.collisionlistStore.iter_next(iter)


    def __applySkipMode(self):
        iter = self.collisionlistStore.get_iter_first()
        
        while iter != None:
            self.collisionlistStore.set_value(iter, 1, True)
            self.collisionlistStore.set_value(iter, 3, False)
            iter = self.collisionlistStore.iter_next(iter)


    def __overwriteModeToggled(self, togglebutton):
        if togglebutton.get_active():
            self.__applyOverwriteMode()
        

    def __skipModeSkipToggled(self, togglebutton):
        if togglebutton.get_active():
            self.__applySkipMode()


    def __getResolvedContacts(self):
        resolvedContacts = contacts.ContactList()
        iter = self.collisionlistStore.get_iter_first()
        
        while iter != None:
            name = self.collisionlistStore.get_value(iter, 0)
            if self.collisionlistStore.get_value(iter, 1) == True:
                phoneNumber = self.collisionlistStore.get_value(iter, 2)
            else:
                phoneNumber = self.collisionlistStore.get_value(iter, 4)
            resolvedContacts.addContact(contacts.Contact(name, phoneNumber))
            iter = self.collisionlistStore.iter_next(iter)

        return resolvedContacts
