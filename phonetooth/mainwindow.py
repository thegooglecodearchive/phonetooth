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
import gobject
import gtk.glade
import os
import threading
import bluetooth

from phonetooth import contacts
from phonetooth import mobilephone
from phonetooth import contactsdialog
from phonetooth import preferencesdialog

class MainWindow:
    def __init__(self):
        try:
            from phonetooth import constants
            datadir = constants.datadir
        except:
            #fallback when running from repository
            datadir = 'ui'        
        
        self.__widgetTree           = gtk.glade.XML(os.path.join(datadir, 'phonetooth.glade'))
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
        
        self.__preferencesDialog = preferencesdialog.PreferencesDialog(self, self.__widgetTree)
        
        self.__contactsDialog = contactsdialog.ContactsDialog(self.__widgetTree, self.__contactlistStore, self.__preferencesDialog.btDevice)
        self.__contactsDialog.updateStoreFromContactList(contactList)
        
        self.__recipientBox.set_active(0)
        
        
        dic = {'onMainWindowDestroy'            : gtk.main_quit,
               'onSendFile'                     : self.__sendFile,
               'onManageContactsActivated'      : self.__contactsDialog.run,
               'onPreferencesActivated'         : self.__preferencesDialog.run,
               'onSendButtonClicked'            : self.__sendSMS,
               'onKeyPressedInMessage'          : self.__updateNrCharacters,
               'onAboutButtonClicked'           : self.__showAboutDialog}
        self.__widgetTree.signal_autoconnect(dic)
        
        gobject.threads_init()
        gtk.window_set_default_icon_from_file(os.path.join(datadir, 'phonetooth-small.svg'))
        
        self.__mainWindow.show()
        
    def btDeviceChanged(self, widget):
        self.__contactsDialog.btDevice = self.__preferencesDialog.btDevice
        
    def __updateContactStore(self, widget = 0):
        self.__contactlistStore.clear()
        
        contactNames = self.__contactListBeingEdited.keys()
        contactNames.sort()
        
        for contactName in contactNames:
            self.__contactlistStore.append((contactName, self.__contactListBeingEdited[contactName]))
            
    def __sendSMS(self, widget):
        threading.Thread(target = self.__sendSMSThread).start()
        
    def __sendFile(self, widget):
        chooser = gtk.FileChooserDialog(title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            threading.Thread(target = self.__sendFileThread, args = (chooser.get_filename(),)).start()
        chooser.destroy()

    def __sendSMSThread(self):
        gobject.idle_add(self.__setSensitive, False)
        textBuffer = self.__inputField.get_buffer()
        listStore = self.__recipientBox.get_model()
        
        message = textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter())
        phoneNr = listStore[self.__recipientBox.get_active()][1]
        
        try:
            phone = mobilephone.MobilePhone(self.__preferencesDialog.btDevice)
            phone.sendSMS(message, phoneNr)
            self.__pushStatusText('Message succesfully sent.')
        except Exception, e:
            self.__pushStatusText('Failed to send message: ' + str(e))
            
        gobject.idle_add(self.__setSensitive, True)
        
    def __sendFileThread(self, filename):
        gobject.idle_add(self.__setSensitive, False)
        
        try:
            self.__pushStatusText('Sending file...')
            phone = mobilephone.MobilePhone(self.__preferencesDialog.btDevice)
            phone.sendFile(filename)
            self.__pushStatusText('File succesfully sent.')
        except Exception, e:
            self.__pushStatusText('Failed to send file: ' + str(e))
            
        gobject.idle_add(self.__setSensitive, True)
            
    def __updateNrCharacters(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE:
            nrCharacters = self.__inputField.get_buffer().get_char_count()
            self.__charactersLabel.set_text('Characters: ' + str(nrCharacters))
            
            self.__sendButton.set_sensitive(nrCharacters != 0)
            
    def __showAboutDialog(self, widget):
        self.__aboutDialog.run()
        self.__aboutDialog.hide()
        
    def __pushStatusText(self, message):
        self.__statusBar.push(0, message)
    
    def __setSensitive(self, sensitive):
        if sensitive == True:
            self.__mainWindow.set_sensitive(True)
            self.__mainWindow.window.set_cursor(None)
        else:
            self.__mainWindow.set_sensitive(False)
            self.__mainWindow.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
