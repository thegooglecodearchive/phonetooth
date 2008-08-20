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

import sys
import dbus
import dbus.glib
import gobject
import gtk
import os

import transferinfo
import phonebrowser
import filetransferdialog

from filecollection import File
from filecollection import Directory

from gettext import gettext as _

class FileTransfer:
    def __init__(self, widgetTree, parent):
        self.__phoneBrowser = phonebrowser.PhoneBrowser()
        self.__fileName = None
        self.__parent = parent
        
        self.__statusBar = widgetTree.get_widget('statusBar')
        
        self.__transferDialog = filetransferdialog.FileTransferDialog(widgetTree, parent)
        
        self.__phoneBrowser.connect('connected',    self.__connectedCb)
        self.__phoneBrowser.connect('completed',    self.__transferCompletedCb)
        self.__phoneBrowser.connect('error',        self.__errorCb)
        self.__phoneBrowser.connect('progress',     self.__transferDialog.progress)
        
    
    def transferFile(self, btAddress):
        chooser = gtk.FileChooserDialog(title = None, parent = self.__parent, action = gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.__filename = chooser.get_filename()
            chooser.destroy()
            
            self.__transferDialog.start(os.path.getsize(self.__filename))
            self.__transferDialog.nextFile(None, File(self.__filename, os.path.getsize(self.__filename)))
            self.__phoneBrowser.connectToPhone(btAddress)
            response = self.__transferDialog.run()
            if response == gtk.RESPONSE_CANCEL:
                self.__statusBar.push(0, _('File transfer cancelled.'))
            elif response == 1:
                self.__statusBar.push(0, _('File transfer failed.'))
            else:
                self.__statusBar.push(0, _('File transfer succeeded.'))
        else:
            chooser.destroy()
        
    
    def __connectedCb(self, sender = None):
        self.__phoneBrowser.copyToRemote(self.__filename)
        
    
    def __transferCompletedCb(self, sender = None):
        self.__transferDialog.close()
        self.__phoneBrowser.disconnectFromPhone()
        
    
    def __errorCb(self, sender, errorMsg):
        #self.__transferDialog.close()
        gobject.idle_add(self.__statusBar.push, 0, errorMsg)
        
        
