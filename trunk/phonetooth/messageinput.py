import gtk
import gobject

from phonetooth import sms

from gettext import gettext as _

class MessageInput(gobject.GObject):
    __gsignals__ = { 
        'sendpossible': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_BOOLEAN])
    }

    def __init__(self, widgetTree):
        gobject.GObject.__init__(self)
        
        self.__inputField           = widgetTree.get_widget('textView')
        self.__charactersLabel      = widgetTree.get_widget('charactersLabel')
        self.__messageCountLabel    = widgetTree.get_widget('messageCountLabel')
        self.__encodingLabel        = widgetTree.get_widget('encodingLabel')
        self.__recipientBox         = widgetTree.get_widget('recipientBox')
        self.__sendButton           = widgetTree.get_widget('sendButton')
        self.__deliveryReportCheck  = widgetTree.get_widget('deliveryReportCheck')
        
        cell = gtk.CellRendererText()
        self.__recipientBox.pack_start (cell, False)
        self.__recipientBox.add_attribute (cell, 'text', 1)
        
        dic = {'onKeyreleased'                  : self.__onKeyPressed,
               'onPaste'                        : self.__onPaste,
               'onDrop'                         : self.__onDrop
        }
        widgetTree.signal_autoconnect(dic)
        
        
    def setDataModel(self, dataModel):
        self.__recipientBox.set_model(dataModel)
        
        
    def __onKeyPressed(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE:
            self.__updateInfo()


    def __onPaste(self, widget):
        self.__updateInfo()
        
        
    def __onDrop(self, widget, drag_context, x, y, selection_data, info, timestamp):
        self.__updateInfo(len(selection_data.get_text()))
        
    
    def __updateInfo(self, dropSize = 0):
        smsMsg = self.generateSMS()
        nrCharacters = smsMsg.getMessageLength()
        self.__charactersLabel.set_text(_('Characters: ') + str(nrCharacters))
        self.__sendButton.set_sensitive(nrCharacters != 0)
        self.__messageCountLabel.set_text(_('Messages: ') + str(smsMsg.getNumMessages()))

        if smsMsg.is7Bit():
            self.__encodingLabel.set_text(_('Encoding: ') + 'GSM 7-bit')
        else:
            self.__encodingLabel.set_text(_('Encoding: ') + 'UCS2')
            
        self.emit("sendpossible", nrCharacters != 0)
            

    def generateSMS(self):
        textBuffer = self.__inputField.get_buffer()
        listStore = self.__recipientBox.get_model()
        
        smsMsg = sms.Sms()
        smsMsg.setMessage(textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter()))
        if self.__recipientBox.get_active() > 0:
            smsMsg.recipient = listStore[self.__recipientBox.get_active()][1]
        smsMsg.statusReport = self.__deliveryReportCheck.get_active()
        return smsMsg
