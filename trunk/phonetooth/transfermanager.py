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
import gobject

import transferinfo
import phonebrowser

from filecollection import File
from filecollection import Directory

class TransferManager(gobject.GObject):
    __gsignals__ =  {
        "transferscompleted": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "progress": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_INT]),
        "filetransferstarted": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT])
    }
    
    def __init__(self, phoneBrowser):
        gobject.GObject.__init__(self)

        self.__phoneBrowser = phoneBrowser
        self.__phoneBrowser.connect('progress', self.__transferProgressCb)
        self.__phoneBrowser.connect('completed', self.__transferCompletedCb)
        
        self.__copyFromPhoneToLocal = True
        self.__localDirectory = None
        self.__transferQueue = []
        self.__currentTransferDir = None
        self.__currentPath = None
        
    
    def __del__(self):
        self.__phoneBrowser.disconnect('progress')
        self.__phoneBrowser.disconnect('completed')
    
    
    def buildDirectoryStructure(self, directoryName = '.', parent = None):
        directory = Directory()
        directory.parent = parent
        directory.name = directoryName
        
        if directoryName != '.':
            self.__phoneBrowser.changeDirectory(directoryName)
        
        dirs, files = self.__phoneBrowser.getDirectoryListing()
        for file in files:
            directory.addFile(file)
        for dir in dirs:
            directory.addDirectory(self.buildFileCollectionFromDir(dir, directory))
        
        if directoryName != '.':
            self.__phoneBrowser.directoryUp()
        
        return directory
        
    
    def copyToLocal(self, remoteDirectory, localDirectory):
        self.__copyFromPhoneToLocal = True
        self.__localDirectory = localDirectory
        self.__transferQueue = remoteDirectory
        self.__currentTransferDir = remoteDirectory
        self.__currentTransferPath = localDirectory
        
        self.__transferNextFileInQueue()
                
    
    def copyToRemote(self, localDirectory):
        self.__copyFromPhoneToLocal = False
        self.__transferQueue = localDirectory
        self.__currentTransferDir = localDirectory
        
        self.__transferNextFileInQueue()
        
        
    def __transferNextFileInQueue(self):
        if (len(self.__currentTransferDir.directories) > 0):
            self.__currentTransferDir = self.__currentTransferDir.directories[0]
            self.__phoneBrowser.changeDirectory(self.__currentTransferDir.name)
            self.__currentTransferPath = os.path.join(self.__currentTransferPath, self.__currentTransferDir.name)
            if not os.path.exists(self.__currentTransferPath):
                os.mkdir(self.__currentTransferPath)
            self.__transferNextFileInQueue()
        else:
            if (len(self.__currentTransferDir.files) > 0):
                fileInfo = self.__currentTransferDir.files.pop(0)
                
                self.emit("filetransferstarted", fileInfo)
                if self.__copyFromPhoneToLocal == True:
                    self.__phoneBrowser.copyToLocal(fileInfo.name, self.__currentTransferPath)
                else:
                    self.__phoneBrowser.copyToRemote(fileInfo.name)
            else:
                self.__currentTransferDir = self.__currentTransferDir.parent
                if self.__currentTransferDir != None:
                    self.__currentTransferDir.directories.pop(0)
                    self.__phoneBrowser.directoryUp()
                    self.__currentTransferPath = os.path.normpath(os.path.join(self.__currentTransferPath, '..'))
                    self.__transferNextFileInQueue()
                else:
                    self.emit('transferscompleted')
                    
                    
    def __transferProgressCb(self, sender, bytesTransferred):
        self.emit('progress', bytesTransferred)
        
        
    def __transferCompletedCb(self, sender = None):
        self.__transferNextFileInQueue()
