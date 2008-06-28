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

import transferinfo

class FileTransfer(gobject.GObject):
    __gsignals__ =  { 
        "completed": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "error": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "progress": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT, gobject.TYPE_INT, gobject.TYPE_INT])
    }
    
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.__fileSizeInBytes = -1
        self.__bytesTransferred = 0
        self.__time = 0.0
        self.__speedHistory = []
        self.__mainLoop = None
        self.__transferInfo = transferinfo.TransferInfo()
        
    
    def __del__(self):
        if self.__mainLoop != None and self.__mainLoop.is_running:
            self.__mainLoop.quit()
        
  
    def transferFile(self, btAddress, filename):
        bus = dbus.SessionBus()
        self.__filename = filename
        
        mgrObject = bus.get_object('org.openobex', '/org/openobex')
        self.__dbusManager = dbus.Interface(mgrObject, 'org.openobex.Manager')
        
        sessionPath = self.__dbusManager.CreateBluetoothSession(btAddress, 'opp')
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
        
    
    def cancelTransfer(self):
        self.__disconnect()
        

    def __connectedCb(self):
        self.__dbusSession.SendFile(self.__filename)
        
    
    def __disconnectedCb(self):
        self.__dbusSession.Close()
        
    
    def __closedCb(self):
        self.__mainLoop.quit()
        
    
    def __disconnect(self):
        if self.__dbusSession.IsBusy():
            self.__dbusSession.Cancel()
        
        if self.__dbusSession.IsConnected():
            self.__dbusSession.Disconnect()
        
        
    def __errorOccurredCb(self, errorName, errorMessage):
        print 'Error occurred: %s: %s' % (errorName, errorMessage)
        self.emit("error")
        self.__disconnect()

        
    def __transferStartedCb(self, filename, localPath, fileSizeInBytes):
        self.__transferInfo.start(fileSizeInBytes)
        
    
    def __transferProgressCb(self, bytesTransferred):
        self.__transferInfo.update(bytesTransferred)
        self.emit("progress", self.__transferInfo.progress, self.__transferInfo.kbPersecond, self.__transferInfo.timeRemaining)
        
    
    def __transferCompletedCb(self):
        self.emit("completed")
        self.__disconnect()
    
