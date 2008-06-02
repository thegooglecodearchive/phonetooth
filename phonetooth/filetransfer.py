import sys
import dbus
import dbus.glib
import gobject
import time

class FileTransfer(gobject.GObject):
    __fileSizeInBytes = -1
    __bytesTransferred = 0
    __time = 0.0
    __speedHistory = []
    __mainLoop = None
    
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
        self.disconnect()

        
    def __transferStartedCb(self, filename, localPath, fileSizeInBytes):
        self.__fileSizeInBytes = fileSizeInBytes
        self.__transferHistory = []
        
    
    def __transferProgressCb(self, bytesTransferred):
        curTime = time.time()

        if self.__fileSizeInBytes <= 0:
            self.__time = curTime
            return

        timeDelta = curTime - self.__time
        if timeDelta > 0.0:
            bytesPersecond = ((bytesTransferred - self.__bytesTransferred) / timeDelta)
            
            if len(self.__speedHistory) == 20:
                self.__speedHistory.pop(0)
            self.__speedHistory.append(int(bytesPersecond))
        
        kbPersecond = self.__getAverageSpeed() / 1024.0
        kbLeft = (self.__fileSizeInBytes - bytesTransferred) / 1024.0
        if kbPersecond > 0:
            timeRemaining = int(kbLeft / kbPersecond)
        else:
            timeRemaining = -1

        self.emit("progress", bytesTransferred / float(self.__fileSizeInBytes), int(kbPersecond), timeRemaining)
        self.__bytesTransferred = bytesTransferred
        self.__time = curTime
        
    
    def __getAverageSpeed(self):
        historyLength = len(self.__speedHistory)
        
        if historyLength == 0:
            return 0
        
        totalTransfer = 0
        for transfer in self.__speedHistory:
            totalTransfer += transfer
            
        return totalTransfer / historyLength
    
    def __transferCompletedCb(self):
        self.emit("completed")
        self.__disconnect()
    
