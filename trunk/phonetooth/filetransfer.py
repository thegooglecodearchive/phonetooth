import sys
import dbus
import dbus.glib
import gobject
import time
import gtk

class FileTransfer(gobject.GObject):
    __fileSizeInBytes = -1
    
    __gsignals__ =  { 
        "completed": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "error": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "progress": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT])
    }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
  
    def transferFile(self, btAddress, filename):
        bus = dbus.SessionBus()
        self.__filename = filename
        
        mgrObject = bus.get_object('org.openobex', '/org/openobex')
        self.__dbusManager = dbus.Interface(mgrObject, 'org.openobex.Manager')
        
        sessionPath = self.__dbusManager.CreateBluetoothSession(btAddress, 'opp')
        sessionObject = bus.get_object('org.openobex', sessionPath)
        self.__dbusSession = dbus.Interface(sessionObject, 'org.openobex.Session')
        
        self.__dbusSession.connect_to_signal('Connected', self.connectedCb)
        self.__dbusSession.connect_to_signal('Disconnected', self.disconnectedCb)
        self.__dbusSession.connect_to_signal('ErrorOccurred', self.errorOccurredCb)
        self.__dbusSession.connect_to_signal('TransferProgress', self.transferProgressCb)
        self.__dbusSession.connect_to_signal('TransferStarted', self.transferStartedCb)
        self.__dbusSession.connect_to_signal('TransferCompleted', self.transferCompletedCb)
        
        self.__main_loop = gobject.MainLoop()
        self.__main_loop.run()
        

    def connectedCb(self):
        self.__dbusSession.SendFile(self.__filename)
        
    
    def disconnectedCb(self):
        print 'Disconnected'
        self.__dbusSession.Close()
        self.__main_loop.quit()
        
    
    def disconnect(self):
        if self.__dbusSession.IsBusy():
            self.__dbusSession.Cancel()
        
        if self.__dbusSession.IsConnected():
            self.__dbusSession.Disconnect()
        
        
    def errorOccurredCb(self, errorName, errorMessage):
        print 'Error occurred: %s: %s' % (errorName, errorMessage)
        self.emit("error")
        self.disconnect()

        
    def transferStartedCb(self, filename, localPath, fileSizeInBytes):
        self.__fileSizeInBytes = fileSizeInBytes
        
    
    def transferProgressCb(self, bytesTransferred):
        if self.__fileSizeInBytes > 0:
            self.emit("progress", bytesTransferred / float(self.__fileSizeInBytes))
    
    
    def transferCompletedCb(self):
        self.emit("completed")
        self.disconnect()
    
    
    def cancelTransfer(self):
        self.disconnect()
        
