import gobject
import os

from filecollection import File
from filecollection import Directory

class PhoneBrowserStub(gobject.GObject):
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
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_INT])
    }
    
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.isConnected = False
        self.curDir = None
        self.lastCreatedDir = None
        self.lastFileCopied = None
        self.dirUp = False
    
    
    def connectToPhone(self, btAddress):
        self.isConnected = True
        
        
    def isConnected(self):
        return self.isConnected
        

    def disconnectFromPhone(self):
        self.isConnected = False
            
    
    def getDirectoryListing(self):
        return self.dirs, self.files
    
    
    def changeDirectory(self, dir):
        self.curDir = dir
        
        
    def createDirectory(self, dir):
        self.lastCreatedDir = dir
        
    
    def gotoRoot(self):
        self.curDir = '/'
        
    
    def directoryUp(self):
        self.dirUp = True
        
    
    def copyToLocal(self, remoteFilename, localDirectory):
        self.lastFileCopied = remoteFilename
                
    
    def copyToRemote(self, localFile):
        self.lastFileCopied = localFile
        
