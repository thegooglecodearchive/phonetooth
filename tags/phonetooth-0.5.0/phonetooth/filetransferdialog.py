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

import phonebrowserhandler
import filetransferdialog
import transferinfo

from filecollection import File
from filecollection import Directory

from gettext import gettext as _

class FileTransferDialog:
    def __init__(self, widgetTree, parent):
        self.__parent = parent
        self.__transferInfo = transferinfo.TransferInfo()
        
        self.__sendFileDialog       = widgetTree.get_widget('sendFileDialog')
        self.__transferProgressBar  = widgetTree.get_widget('transferProgress')
        self.__filenameLabel        = widgetTree.get_widget('filenameLabel')
        self.__statusBar            = widgetTree.get_widget('statusBar')
        
        self.__sendFileDialog.set_transient_for(parent)
                
        
    def __del__(self):
        self.__phoneBrowser.disconnectFromPhone()
        
    
    def run(self):
        self.__transferProgressBar.set_fraction(0.0)
        self.__transferProgressBar.set_text('')
        
        response = self.__sendFileDialog.run()
        self.__sendFileDialog.hide()
        return response
        
        
    def cancel(self):
        gobject.idle_add(self.__sendFileDialog.response, 1)
        
    
    def close(self):
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)
        
    
    def start(self, totalSize):
        self.__transferInfo.start(totalSize)
        
    
    def nextFile(self, sender, file):
        self.__filenameLabel.set_text(file.name)
        self.__transferInfo.startNextFile(file.size)
        

    def progress(self, sender, bytesTransferred):
        self.__transferInfo.update(bytesTransferred)
        
        gobject.idle_add(self.__transferProgressBar.set_fraction, self.__transferInfo.progress)
        statusString = str(self.__transferInfo.kbPersecond) + ' kb/s  '

        if self.__transferInfo.timeRemaining != -1:
            if self.__transferInfo.timeRemaining >= 60:
                statusString += '(' + str(self.__transferInfo.timeRemaining / 60 + 1) + _(' minutes remaining') + ')'
            else:
                statusString += '(' + str(self.__transferInfo.timeRemaining / 10 * 10 + 10) + _(' seconds remaining') + ')'
        
        gobject.idle_add(self.__transferProgressBar.set_text, statusString)
        
