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

from phonetooth import contacts
from phonetooth import mobilephone
from phonetooth import mobilephonegammu
from phonetooth import mobilephonefactory
from phonetooth import contactsdialog
from phonetooth import preferences
from phonetooth import preferencesdialog
from phonetooth import sms
from phonetooth import filetransfer
from phonetooth import selectcontactsdialog
from phonetooth import sendmessagedialog
from phonetooth import messageinput
from phonetooth import phonebrowserhandler

from gettext import gettext as _

class MainWindow:
    def __init__(self):
        try:
            from phonetooth import constants
            datadir = constants.datadir
        except:
            #fallback when running from repository
            datadir = 'ui'
            
        self.__waitingForQuit = False
        
        self.__widgetTree           = gtk.glade.XML(os.path.join(datadir, 'phonetooth.glade'))
        self.__mainWindow           = self.__widgetTree.get_widget('mainWindow')
        self.__sendButton           = self.__widgetTree.get_widget('sendButton')
        self.__aboutDialog          = self.__widgetTree.get_widget('aboutDialog')
        self.__statusBar            = self.__widgetTree.get_widget('statusBar')
        self.__sendFileMenuItem     = self.__widgetTree.get_widget('sendFileMenuitem')
        self.__sendMessageMenuitem  = self.__widgetTree.get_widget('sendMessageMenuitem')
        self.__storeMessageCheck    = self.__widgetTree.get_widget('storeMessageCheck')
        self.__notebook             = self.__widgetTree.get_widget('mainNotebook')
        
        self.__aboutDialog.set_name('PhoneTooth')
        self.__sendButton.set_sensitive(False)
                
        self.__prefs = preferences.Preferences()
        self.__prefs.load()
        self.__preferencesDialog = preferencesdialog.PreferencesDialog(self.__widgetTree, self.__prefs, parent = self.__mainWindow)
        
        self.__contactsDialog = contactsdialog.ContactsDialog(self.__widgetTree, self.__prefs, parent = self.__mainWindow)
        
        self.__messageInput = messageinput.MessageInput(self.__widgetTree)
        self.__messageInput.setDataModel(self.__contactsDialog.contactlistStore)
        self.__messageInput.connect('sendpossible', self.__sendPossibleCb)
        
        self.__phoneBrowser = phonebrowserhandler.PhoneBrowserHandler(self.__widgetTree, parent = self.__mainWindow)
        self.__phoneBrowser.connect('disconnected', self.__phoneDisconnectedCb)
        
        self.__contactSelectionDialog = selectcontactsdialog.SelectContactsDialog(self.__widgetTree, self.__mainWindow)
        self.__sendMessageDialog = sendmessagedialog.SendMessageDialog(self.__widgetTree, self.__mainWindow)
        
        self.__checkSendFileButtonSensitivity()
        
        dic = {'onMainWindowDestroy'            : self.__quit,
               'onSendFile'                     : self.__sendFile,
               'onManageContactsActivated'      : self.__contactsDialog.run,
               'onPreferencesActivated'         : self.__preferencesDialog.run,
               'onSendButtonClicked'            : self.__sendSMS,
               'onAboutButtonClicked'           : self.__showAboutDialog,
               'onPreferencesChanged'           : self.__preferencesChanged,
               'onSendToMultiple'               : self.__sendToMultiple,
               'onSwitchPage'                   : self.__switchPage,
               'keyPressed'                     : self.__keyPressed
        }
        self.__widgetTree.signal_autoconnect(dic)
        
        gtk.window_set_default_icon_from_file(os.path.join(datadir, 'phonetooth-small.svg'))
        
        self.__mainWindow.show()
        
   
    def __switchPage(self, widget, page, index):
        if index == 1:
            if self.__prefs.btDevice == None:
                self.__pushStatusText(_('No bluetooth device configured in preferences'))
            else:
                self.__phoneBrowser.connectToPhone(self.__prefs.btDevice.address)
        else:
            self.__phoneBrowser.disconnectFromPhone()
    
    
    def __sendSMS(self, widget):
        threading.Thread(target = self.__sendSMSThread).start()
        
    
    def __sendToMultiple(self, widget):
        selectedContacts = self.__contactSelectionDialog.run()
        
        if selectedContacts != None:
            smsMsg = self.__messageInput.getMessage()
            phone = mobilephonefactory.createPhone(self.__prefs)
            self.__sendMessageDialog.run(phone, selectedContacts, smsMsg)
         
    
    def __sendFile(self, widget):
        self.__setSensitive(False)
        fileTransfer = filetransfer.FileTransfer(self.__widgetTree, self.__mainWindow)
        fileTransfer.transferFile(self.__prefs.btDevice.address)
        self.__setSensitive(True)
        

    def __sendSMSThread(self):
        smsMsg = self.__messageInput.generateSMS()
        
        if len(smsMsg.recipient) == 0:
            gobject.idle_add(self.__pushStatusText, _('No recipient selected'))
            return
        
        gobject.idle_add(self.__setSensitive, False)

        try:
            phone = mobilephonefactory.createPhone(self.__prefs)
            phone.connect()
            phone.sendSMS(smsMsg)
            if self.__storeMessageCheck.get_active():
                phone.storeSMS(sms)
            gobject.idle_add(self.__pushStatusText, _('Message successfully sent'))
        except Exception, e:
            gobject.idle_add(self.__pushStatusText, _('Failed to send message: ') + str(e))
            
        gobject.idle_add(self.__setSensitive, True)
        
        
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
            
    
    def __checkSendFileButtonSensitivity(self):
        if self.__prefs.connectionMethod == 'bluetooth' and self.__prefs.btDevice != None:
            self.__sendFileMenuItem.set_sensitive(True)
        else:
            self.__sendFileMenuItem.set_sensitive(False)
    
    
    def __preferencesChanged(self, widget):
        self.__checkSendFileButtonSensitivity()
        
    
    def __sendPossibleCb(self, sender, sendPossible):
        self.__sendMessageMenuitem.set_sensitive(sendPossible)
        
    
    def __phoneDisconnectedCb(self, data = None):         
        if self.__waitingForQuit == True:
            gtk.main_quit()
        
    
    def __quit(self, widget):
        if self.__phoneBrowser.isConnected():
            self.__phoneBrowser.disconnectFromPhone()
            self.__waitingForQuit = True
        else:
            gtk.main_quit()
            
            
    def __keyPressed(self, widget, event):
        if event.type == gtk.gdk.KEY_PRESS and event.keyval == gtk.keysyms.Tab and event.state & gtk.gdk.CONTROL_MASK:
            self.__nextTab()
            
    
    def __nextTab(self):
        if self.__notebook.get_current_page() == self.__notebook.get_n_pages() - 1:
            self.__notebook.set_current_page(0)
        else:
            self.__notebook.next_page()        
        
        self.__mainWindow.set_focus_child(self.__notebook)
 
