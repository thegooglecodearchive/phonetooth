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

import threading
import gtk
import gobject

from gettext import gettext as _

class SendMessageDialog:
    __stopSending = False
    __sendMessageLabelText = None
    
    def __init__(self, widgetTree, parent = None):
        self.__sendmessageDialog        = widgetTree.get_widget('sendMessageDialog')
        self.__transferMessageProgress  = widgetTree.get_widget('transferMessageProgress')
        self.__recipientLabel           = widgetTree.get_widget('recipientLabel')
        self.__sendMessageLabel         = widgetTree.get_widget('sendMessageLabel')
        self.__sendImage                = widgetTree.get_widget('sendImage')
        
        self.__sendMessageLabelText = self.__sendMessageLabel.get_text()
        self.__sendmessageDialog.set_transient_for(parent)
        
    def run(self, phone, contacts, sms):
        self.__stopSending = False
        sendThread = threading.Thread(target = self.__sendMessagesThread, args=(phone, contacts, sms))
        sendThread.start()

        self.__sendMessageLabel.set_text(self.__sendMessageLabelText)
        if self.__sendmessageDialog.run() == gtk.RESPONSE_CANCEL:
            self.__sendMessageLabel.set_text(_('Waiting for current message transfer to finish...'))
            
            self.__stopSending = True
            sendThread.join(10.0)
            
        self.__sendmessageDialog.hide()
        

    def __sendMessagesThread(self, phone, contacts, sms):
        gobject.idle_add(self.__transferMessageProgress.set_fraction, 0.0)
        gobject.idle_add(self.__recipientLabel.set_text, '')
        gobject.idle_add(self.__sendImage.set_from_stock, gtk.STOCK_CONNECT, 4)
        gobject.idle_add(self.__sendMessageLabel.set_text, _('Connecting to phone...'))
        
        phone.connect()
        
        gobject.idle_add(self.__sendImage.set_from_stock, gtk.STOCK_FILE, 4)
        gobject.idle_add(self.__sendMessageLabel.set_text,self.__sendMessageLabelText)
        
        numContacts = len(contacts.contacts)
        messagesSent = 0.0
        for contact, phoneNumber in contacts.contacts.iteritems():
            if self.__stopSending == True:
                break
            
            gobject.idle_add(self.__recipientLabel.set_text, contact)
            sms.recipient = phoneNumber
            phone.sendSMS(sms)
            messagesSent += 1.0
            gobject.idle_add(self.__transferMessageProgress.set_fraction, messagesSent / numContacts)
            
        gobject.idle_add(self.__sendmessageDialog.response, gtk.RESPONSE_CLOSE)
            