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
    __fileSizeInBytes = -1
    __bytesTransferred = 0
    __time = 0.0
    __speedHistory = []
    
    progress = 0.0
    kbPersecond = 0
    timeRemaining = 0
    
    def overwriteSize(self, size):
        self.__fileSizeInBytes = size
    
    
    def start(self, fileSizeInBytes):
        if fileSizeInBytes != 0:
            self.__fileSizeInBytes = fileSizeInBytes
        self.__transferHistory = []
        
    
    def update(self, bytesTransferred):
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
            self.timeRemaining = int(kbLeft / kbPersecond)
        else:
            self.timeRemaining = -1

        self.progress = bytesTransferred / float(self.__fileSizeInBytes)
        self.kbPersecond = int(kbPersecond)
        
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
