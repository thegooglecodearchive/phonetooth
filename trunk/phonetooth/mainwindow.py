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

from gettext import gettext as _

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
        self.__messageCountLabel    = self.__widgetTree.get_widget('messageCountLabel')
        self.__encodingLabel        = self.__widgetTree.get_widget('encodingLabel')
        self.__sendButton           = self.__widgetTree.get_widget('sendButton')
        self.__aboutDialog          = self.__widgetTree.get_widget('aboutDialog')
        self.__statusBar            = self.__widgetTree.get_widget('statusBar')
        self.__sendMenuItem         = self.__widgetTree.get_widget('sendMenuitem')
        self.__deliveryReportCheck  = self.__widgetTree.get_widget('deliveryReportCheck')
        self.__storeMessageCheck    = self.__widgetTree.get_widget('storeMessageCheck')
        self.__sendFileDialog       = self.__widgetTree.get_widget('sendFileDialog')
        self.__transferProgressBar  = self.__widgetTree.get_widget('transferProgress')
        self.__transferFileLabel    = self.__widgetTree.get_widget('transferFileLabel')
        self.__transferFileLabelText = self.__transferFileLabel.get_text()
        
        self.__sms = sms.Sms()
        
        self.__aboutDialog.set_name('PhoneTooth')
        self.__sendFileDialog.set_transient_for(self.__mainWindow)
        self.__sendButton.set_sensitive(False)
                
        self.__prefs = preferences.Preferences()
        self.__prefs.load()
        self.__preferencesDialog = preferencesdialog.PreferencesDialog(self.__widgetTree, self.__prefs)        
        
        self.__contactsDialog = contactsdialog.ContactsDialog(self.__widgetTree, self.__prefs)
        self.__recipientBox.set_model(self.__contactsDialog.contactlistStore)
        
        self.__fileTransfer = filetransfer.FileTransfer()
        self.__fileTransfer.connect("progress", self.transferProgressCb)
        self.__fileTransfer.connect("completed", self.transferCompletedCb)
        self.__fileTransfer.connect("error", self.transferErrorCb)
        
        cell = gtk.CellRendererText()
        self.__recipientBox.pack_start (cell, False)
        self.__recipientBox.add_attribute (cell, 'text', 1)
        
        self.__checkSendFileButtonSensitivity()
        
        dic = {'onMainWindowDestroy'            : gtk.main_quit,
               'onSendFile'                     : self.__sendFile,
               'onManageContactsActivated'      : self.__contactsDialog.run,
               'onPreferencesActivated'         : self.__preferencesDialog.run,
               'onSendButtonClicked'            : self.__sendSMS,
               'onKeyreleased'                  : self.__onKeyPressed,
               'onPaste'                        : self.__onPaste,
               'onDrop'                         : self.__onDrop,
               'onAboutButtonClicked'           : self.__showAboutDialog,
               'onPreferencesChanged'           : self.__preferencesChanged
        }
        self.__widgetTree.signal_autoconnect(dic)
        
        gobject.threads_init()
        gtk.window_set_default_icon_from_file(os.path.join(datadir, 'phonetooth-small.svg'))
        
        self.__mainWindow.show()
        
   
    def __sendSMS(self, widget):
        threading.Thread(target = self.__sendSMSThread).start()
        
    
    def __sendFile(self, widget):
        self.__setSensitive(False)
        chooser = gtk.FileChooserDialog(title = None, parent = self.__mainWindow, action = gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
            
            try:
                self.__transferProgressBar.set_fraction(0.0)
                self.__transferProgressBar.set_text('0 %')
                self.__transferFileLabel.set_text(self.__transferFileLabelText + os.path.basename(filename) + ':')
                self.__pushStatusText(_('Sending file...'))
                threading.Thread(target = self.__sendFileThread, args = (filename,)).start()
                if self.__sendFileDialog.run() == gtk.RESPONSE_CANCEL:
                    self.__fileTransfer.cancelTransfer()
                    self.__pushStatusText(_('File transfer cancelled.'))
                else:
                    self.__pushStatusText(_('File succesfully sent.'))
            except Exception, e:
                gobject.idle_add(self.__pushStatusText, _('Failed to send file: ') + str(e))
            self.__sendFileDialog.hide()
        else:
            chooser.destroy()
            
        self.__setSensitive(True)
        

    def __sendFileThread(self, filename):
        self.__fileTransfer.transferFile(self.__prefs.btDevice.address, filename)
        
    
    def transferProgressCb(self, sender, progress):
        gobject.idle_add(self.__transferProgressBar.set_fraction, progress)
        gobject.idle_add(self.__transferProgressBar.set_text, str(int(progress * 100)) + ' %')
        
    
    def transferCompletedCb(self, data = None):
        print 'transfer complete recieved'
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)
        
    
    def transferErrorCb(self, data = None):
        print 'transfer error recieved'
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)

    
    def __sendSMSThread(self):
        if self.__recipientBox.get_active() == -1:
            gobject.idle_add(self.__pushStatusText, _('No recipient selected'))
            return
        
        gobject.idle_add(self.__setSensitive, False)
        textBuffer = self.__inputField.get_buffer()
        listStore = self.__recipientBox.get_model()
        
        self.__sms.setMessage(textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter()))
        self.__sms.recipient = listStore[self.__recipientBox.get_active()][1]

        try:
            phone = mobilephonefactory.createPhone(self.__prefs)
            phone.connect()
            phone.sendSMS(self.__sms, self.__deliveryReportCheck.get_active())
            if self.__storeMessageCheck.get_active():
                phone.storeSMS(self.__sms)
            gobject.idle_add(self.__pushStatusText, _('Message succesfully sent'))
        except Exception, e:
            gobject.idle_add(self.__pushStatusText, _('Failed to send message: ') + str(e))
            
        gobject.idle_add(self.__setSensitive, True)
        
        
    def __onKeyPressed(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE:
            self.__updateInfo()


    def __onPaste(self, widget):
        self.__updateInfo()
        
        
    def __onDrop(self, widget, drag_context, x, y, selection_data, info, timestamp):
        self.__updateInfo(len(selection_data.get_text()))
        
    
    def __updateInfo(self, dropSize = 0):
        textBuffer = self.__inputField.get_buffer()
        smsMsg = sms.Sms(textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter()))
        
        nrCharacters = self.__inputField.get_buffer().get_char_count() + dropSize
        self.__charactersLabel.set_text(_('Characters: ') + str(nrCharacters))
        self.__sendButton.set_sensitive(nrCharacters != 0)
        
        
        self.__messageCountLabel.set_text(_('Messages: ') + str(smsMsg.getNumMessages()))
        
        if smsMsg.is7Bit():
            self.__encodingLabel.set_text(_('Encoding: ') + 'GSM 7-bit')
        else:
            self.__encodingLabel.set_text(_('Encoding: ') + 'UCS2')


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
        if self.__prefs.connectionMethod == 'bluetooth' and self.__prefs.btDevice != None and self.__prefs.btDevice.obexPort != 0:
            self.__sendMenuItem.set_sensitive(True)
        else:
            self.__sendMenuItem.set_sensitive(False)
    
    def __preferencesChanged(self, widget):
        self.__checkSendFileButtonSensitivity()
