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

import os
import gtk
import threading
import gobject

from phonetooth import filetransfer
from gettext import gettext as _

class FileTransferDialog:
    def __init__(self, widgetTree, parent):
        self.__sendFileDialog       = widgetTree.get_widget('sendFileDialog')
        self.__transferProgressBar  = widgetTree.get_widget('transferProgress')
        self.__filenameLabel        = widgetTree.get_widget('filenameLabel')
        self.__statusBar            = widgetTree.get_widget('statusBar')
        self.__parent = parent
        
        self.__sendFileDialog.set_transient_for(parent)
                
        self.__fileTransfer = filetransfer.FileTransfer()
        self.__fileTransfer.connect("progress", self.transferProgressCb)
        self.__fileTransfer.connect("completed", self.transferCompletedCb)
        self.__fileTransfer.connect("error", self.transferErrorCb)
        

    def run(self, btDevice):
        chooser = gtk.FileChooserDialog(title = None, parent = self.__parent, action = gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
            
            try:
                self.__transferProgressBar.set_fraction(0.0)
                self.__transferProgressBar.set_text('')
                self.__filenameLabel.set_text(os.path.basename(filename))
                self.__pushStatusText(_('Sending file...'))
                threading.Thread(target = self.__sendFileThread, args = (filename, btDevice)).start()
                response = self.__sendFileDialog.run()
                if response == gtk.RESPONSE_CANCEL:
                    self.__fileTransfer.cancelTransfer()
                    self.__pushStatusText(_('File transfer cancelled.'))
                elif response == 1:
                    self.__pushStatusText(_('File transfer failed') + '.')
                else:
                    self.__pushStatusText(_('File succesfully sent.'))
            except Exception, e:
                gobject.idle_add(self.__pushStatusText, _('File transfer failed') + ':' + str(e))
            self.__sendFileDialog.hide()
        else:
            chooser.destroy()
            

    def __sendFileThread(self, filename, btDevice):
        try:
            self.__fileTransfer.transferFile(btDevice.address, filename)
        except Exception, e:
            self.transferErrorCb()
        
    
    def transferProgressCb(self, sender, progress, speed, timeRemaining):
        gobject.idle_add(self.__transferProgressBar.set_fraction, progress)
        
        statusString = str(speed) + ' kb/s  '
        if timeRemaining != -1:
            if timeRemaining >= 60:
                statusString += '(' + str(timeRemaining / 60 + 1) + _(' minutes remaining') + ')'
            else:
                statusString += '(' + str(timeRemaining / 10 * 10 + 10) + _(' seconds remaining') + ')'
        
        gobject.idle_add(self.__transferProgressBar.set_text, statusString)
        
    
    def transferCompletedCb(self, data = None):
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)
        
    
    def transferErrorCb(self, data = None):
        print 'transfer error recieved'
        gobject.idle_add(self.__sendFileDialog.response, 1)

    
    def __pushStatusText(self, message):
        self.__statusBar.push(0, message)
