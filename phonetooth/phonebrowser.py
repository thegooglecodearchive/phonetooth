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

import dbus
import dbus.glib
import threading
import gobject
import transferinfo
import os

from xml.dom.minidom import parseString

class File:
    name = None
    size = None
    
    def __init__(self, name, size):
        self.name = name
        self.size = size
        
    
    def  __lt__(self, other):
        return self.name < other.name


class PhoneBrowser(gobject.GObject):
    __dbusSession = None
    __mainLoop = None
    __copyFromPhoneToLocal = True
    __localDirectory = None
    __transferQueue = []
    transferInfo = transferinfo.TransferInfo()
    
    __gsignals__ =  {
        "connected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []), 
        "disconnected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "started": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING]),
        "completed": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "error": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING]),
        "progress": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
    }
    
    
    def __init__(self):
        gobject.GObject.__init__(self)
    
    
    def __del__(self):
        if self.__mainLoop != None and self.__mainLoop.is_running:
            self.__mainLoop.quit()
        
    
    def connectToPhone(self, btAddress):
        threading.Thread(target = self.__run, args = (btAddress,)).start()
        
        
    def isConnected(self):
        if self.__dbusSession == None:
            return False
        
        return self.__dbusSession.IsConnected()
        

    def disconnectFromPhone(self):
        if self.__dbusSession == None:
            return
        
        if self.__dbusSession.IsBusy():
            self.__dbusSession.Cancel()
        
        if self.__dbusSession.IsConnected():
            self.__dbusSession.Disconnect()
            
    
    def __run(self, btAddress):
        try:
            bus = dbus.SessionBus()
            
            self.__mgrObject = bus.get_object('org.openobex', '/org/openobex')
            self.__dbusManager = dbus.Interface(self.__mgrObject, 'org.openobex.Manager')
            
            sessionPath = self.__dbusManager.CreateBluetoothSession(btAddress, 'ftp')
            sessionObject = bus.get_object('org.openobex', sessionPath)
            self.__dbusSession = dbus.Interface(sessionObject, 'org.openobex.Session')
            
            self.__dbusSession.connect_to_signal('Connected', self.__connectedCb)
            self.__dbusSession.connect_to_signal('Disconnected', self.__disconnectedCb)
            self.__dbusSession.connect_to_signal('Closed', self.__closedCb)
            self.__dbusSession.connect_to_signal('ErrorOccurred', self.__errorOccurredCb)
            self.__dbusSession.connect_to_signal('TransferProgress', self.__transferProgressCb)
            self.__dbusSession.connect_to_signal('TransferStarted', self.__transferStartedCb)
            self.__dbusSession.connect_to_signal('TransferCompleted', self.__transferCompletedCb)
            
            self.__mainLoop = gobject.MainLoop()
            self.__mainLoop.run()
        except Exception, e:
            self.emit('error', e.message)
        
    
    def __connectedCb(self):
        self.emit('connected')
        
    
    def __disconnectedCb(self):
        self.__dbusSession.Close()
        
    
    def __closedCb(self):
        if self.__mainLoop != None:
            self.__mainLoop.quit()
        self.emit('disconnected')
        self.__dbusSession = None
        
    
    def __errorOccurredCb(self, errorName, errorMessage):
        print 'Error occurred: %s: %s' % (errorName, errorMessage)
        self.disconnectFromPhone()
        self.emit('error', errorMessage)
        
    
    def getDirectoryListing(self):
        if self.__dbusSession != None:
            return self.parseDirectoryListing(self.__dbusSession.RetrieveFolderListing())
        else:
            return []
    
    
    def changeDirectory(self, dir):
        if self.__dbusSession != None:
            self.__dbusSession.ChangeCurrentFolder(dir)
        
        
    def createDirectory(self, dir):
        if self.__dbusSession != None:
            self.__dbusSession.CreateFolder(dir)
        
    
    def gotoRoot(self):
        if self.__dbusSession != None:
            self.__dbusSession.ChangeCurrentFolderToRoot()
        
    
    def directoryUp(self):
        if self.__dbusSession != None:
            self.__dbusSession.ChangeCurrentFolderBackward()
        
    
    def copyToLocal(self, remoteFileInfos, localDirectory):
        self.__copyFromPhoneToLocal = True
        self.__localDirectory = localDirectory
        self.__transferQueue = remoteFileInfos
        
        self.transferInfo.start(self.__getTransferQueueSizeInBytes())
        self.__transferNextFileInQueue()
                
    
    def copyToRemote(self, localFileInfos):
        self.__copyFromPhoneToLocal = False
        self.__transferQueue = localFileInfos
        
        self.transferInfo.start(self.__getTransferQueueSizeInBytes())
        self.__transferNextFileInQueue()
        
        
    def __transferNextFileInQueue(self):
        if len(self.__transferQueue) == 0:
            self.emit('completed')
        else:
            fileInfo = self.__transferQueue.pop(0)
            if self.__dbusSession != None:
                self.transferInfo.startNextFile(fileInfo[1])
                if self.__copyFromPhoneToLocal == True:
                    self.__dbusSession.CopyRemoteFile(fileInfo[0], self.__localDirectory)
                else:
                    self.__dbusSession.SendFile(fileInfo[0])

    
    def deleteFile(self, remotePath):
        if self.__dbusSession != None:
            self.__dbusSession.DeleteRemoteFile(remotePath)
        
    
    def cancel(self):
        if self.__dbusSession != None:
            self.__dbusSession.Cancel()

    
    def parseDirectoryListing(self, obexListing):
        dirs = []
        files = []
        
        obexListing = obexListing.replace('&', '&amp;')
        obexListing = obexListing.replace('\'', '&apos;')

        dom = parseString(obexListing)
        for dir in dom.getElementsByTagName('folder'):
            dirs.append(dir.getAttribute('name'))
        for file in dom.getElementsByTagName('file'):
            files.append(File(file.getAttribute('name'), int(file.getAttribute('size'))))

        dom.unlink()
        return dirs, files
    
    
    def __transferStartedCb(self, filename, localPath, fileSizeInBytes):
        self.emit('started', localPath)
        
    
    def __transferProgressCb(self, bytesTransferred):
        self.transferInfo.update(bytesTransferred)
        self.emit('progress')
        
    
    def __transferCompletedCb(self):
        self.__transferNextFileInQueue()
        
        
    def __getTransferQueueSizeInBytes(self):
        totalSize = 0
        
        for fileInfo in self.__transferQueue:
            totalSize += fileInfo[1]
            
        print str(totalSize)
        
        return totalSize

