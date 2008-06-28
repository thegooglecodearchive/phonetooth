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

import time

class TransferInfo:
    def __init__(self):
        self.__totalSizeInBytes = -1
        self.__currentFileSizeInBytes = -1
        self.__bytesTransferredTotal = 0
        self.__bytesTransferredCurrentFile = 0
        self.__time = 0.0
        self.__speedHistory = []
        
        self.progress = 0.0
        self.kbPersecond = 0
        self.timeRemaining = -1
    
    
    def start(self, totalSizeInBytes):
        if totalSizeInBytes != 0:
            self.__totalSizeInBytes = totalSizeInBytes
        self.__transferHistory = []
        
        
    def startNextFile(self, fileSize):
        if self.__currentFileSizeInBytes != -1:
            self.__bytesTransferredTotal += self.__currentFileSizeInBytes
        self.__bytesTransferredCurrentFile = 0 
        self.__currentFileSizeInBytes = fileSize
        
    
    def update(self, bytesTransferred):
        curTime = time.time()

        if self.__totalSizeInBytes <= 0:
            self.__time = curTime
            return

        timeDelta = curTime - self.__time
        if timeDelta > 0.0 and self.__bytesTransferredCurrentFile > 0:
            bytesPersecond = ((bytesTransferred - self.__bytesTransferredCurrentFile) / timeDelta)
            
            if len(self.__speedHistory) == 20:
                self.__speedHistory.pop(0)
            self.__speedHistory.append(int(bytesPersecond))
        
        kbPersecond = self.__getAverageSpeed() / 1024.0
        kbLeft = (self.__totalSizeInBytes - bytesTransferred) / 1024.0
        if kbPersecond > 0:
            self.timeRemaining = int(kbLeft / kbPersecond)
        else:
            self.timeRemaining = -1

        self.__bytesTransferredCurrentFile = bytesTransferred
        self.progress = (self.__bytesTransferredTotal + bytesTransferred) / float(self.__totalSizeInBytes)
        self.progress = min(1.0, self.progress)
        self.kbPersecond = int(kbPersecond)
        self.__time = curTime

    
    def __getAverageSpeed(self):
        historyLength = len(self.__speedHistory)
        
        if historyLength == 0:
            return 0
        
        totalTransfer = 0
        for transfer in self.__speedHistory:
            totalTransfer += transfer
            
        return totalTransfer / historyLength
