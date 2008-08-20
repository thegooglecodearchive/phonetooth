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

import socket
import bluetooth
import bit7alphabet

from phonetooth import contacts
from gettext import gettext as _


class MobilePhone:
    def __init__(self, connection):
        self.__connection = connection
        
    
    def __del__(self):
        self.disconnect()
        

    def connect(self):
        self.__connection.connect()
        self.__sendATCommand('ATE0')

        #use UTF-8 where possible
        characterSets = self.__getSupportedCharacterSets()
        if '"UTF-8"' in characterSets:
            self.__setCharacterSet('"UTF-8"')

    
    def disconnect(self):
        self.__connection.disconnect()

    
    def getManufacturer(self):
        return self.__sendATCommand('AT+CGMI')


    def getModel(self):
        return self.__sendATCommand('AT+CGMM')


    def getSerialNumber(self):
        return self.__sendATCommand('AT+CGSN')


    def getBatteryStatus(self):
        response = self.__sendATCommand('AT+CBC')
        return int(response.split(',')[1])
        
    
    def storeSMS(self, sms):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=0') # store PDU mode in sent messages
        self.selectWriteStorage('PHONE')
        
        for pduMsg in sms.getPDU(False):
            # send message information and wait for prompt
            messageCommand = 'AT+CMGW=' + str(len(pduMsg) / 2 - 1) + ',3\r'
            self.__connection.send(messageCommand)
            reply = self.__connection.recv(len(messageCommand) + 4, wait=True) # read message + '\r\n> '

            if reply[-2:] == '> ':
                response = self.__sendATCommand(pduMsg + chr(26), False) # message + CTRL+Z
            else:
                raise Exception, _('Failed to store message')
                
            location = response[response.find(':') + 1:]
    

    def sendSMS(self, sms):
        supportedModes = self.__getSupportedSMSModes()
        if '0' in supportedModes:
            self.__sendSMSPDUMode(sms)
        elif '1' in supportedModes:
            self.__sendSMSTextMode(sms)
        else:
            raise Exception, _('Sending SMS not supported by phone')
 
 
    def __sendSMSTextMode(self, sms):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=1') # text mode
        
        # send message information and wait for prompt
        messageCommand = 'AT+CMGS="' + sms.recipient + '"\r'
        self.__connection.send(messageCommand)
        reply = self.__connection.recv(len(messageCommand) + 4, wait=True) # read message + '\r\n> '

        if reply[-2:] == '> ':
            self.__sendATCommand(sms.getMessage() + chr(26), False) # message + CTRL+Z
        else:
            raise Exception, _('Failed to send message')

 
    def __sendSMSPDUMode(self, sms):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=0') # PDU mode
        
        for pduMsg in sms.getPDU():
            # send message information and wait for prompt
            messageCommand = 'AT+CMGS=' + str(len(pduMsg) / 2 - 1) + '\r'
            self.__connection.send(messageCommand)
            reply = self.__connection.recv(len(messageCommand) + 4, wait=True) # read message + '\r\n> '

            if reply[-2:] == '> ':
                self.__sendATCommand(pduMsg + chr(26), False) # message + CTRL+Z
            else:
                raise Exception, _('Failed to send message')


    def getContacts(self, location):
        if location == 'SIM':
            self.__sendATCommand('AT+CPBS="SM"')
        elif location == 'PHONE':
            self.__sendATCommand('AT+CPBS="ME"')
        else:
            raise Exception, 'Invalid contact location specified'
            
        reply = self.__sendATCommand('AT+CPBR=?')
        memorySlots = self.__parseMemorySlots(reply)
        reply = self.__sendATCommand('AT+CPBR=1,' + memorySlots)
        rawContacts = reply.strip().split('\r\n')
        
        contactList = []
        for contact in rawContacts:
            fields = contact.split(',')
            contactList.append(contacts.Contact(fields[3][1:-1], fields[1][1:-1]))
        
        return contactList
    
    def storeContact(self, name, phoneNr):
        if phoneNr[0] == '+':
            type = '",145,"'
        else:
            type = '",129,"'
        
        self.__sendATCommand('AT+CPBW=,"' + phoneNr + type + name + '"')
        

    def selectReadStorage(self, location):
        currentStorageInfo = self.getCurrentStorageInfo()
        readStorage, writeStorage, recieveStorage = self.getSupportedStorage()
                
        if location == 'SIM' and '"SM"' in readStorage:
            location = '"SM"'
        elif location == 'PHONE' and '"ME"' in readStorage:
            location = '"ME"'
        else:
            raise Exception('Failed to select read storage')
            
            
        self.__sendATCommand('AT+CPMS=%s,%s,%s' % (location, currentStorageInfo[2], currentStorageInfo[4]));
        
    
    def selectWriteStorage(self, location):
        currentStorageInfo = self.getCurrentStorageInfo()
        readStorage, writeStorage, recieveStorage = self.getSupportedStorage()
                
        if location == 'SIM' and '"SM"' in writeStorage:
            location = '"SM"'
        elif location == 'PHONE' and '"ME"' in writeStorage:
            location = '"ME"'
        else:
            raise Exception('Failed to select write storage')
            
            
        self.__sendATCommand('AT+CPMS=%s,%s,%s' % (currentStorageInfo[0], location, currentStorageInfo[4]));
    
    
    def getSupportedStorage(self):
        supportedStorage = self.__sendATCommand('AT+CPMS=?')
        
        readStorage, supportedStorage     = self.__parseSupportedStorage(supportedStorage)
        writeStorage, supportedStorage    = self.__parseSupportedStorage(supportedStorage)
        recieveStorage, supportedStorage  = self.__parseSupportedStorage(supportedStorage)
        
        return readStorage, writeStorage, recieveStorage
        
    
    def getCurrentStorageInfo(self):
        #+CPMS:"SM",3,10,"SM",3,10,"SM",3,10
        currentStorage = self.__sendATCommand('AT+CPMS?')
        storageInfo = []
        
        type, free, currentStorage = self.__parseStorageInfo(currentStorage)
        storageInfo.extend([type, free])
        type, free, currentStorage = self.__parseStorageInfo(currentStorage)
        storageInfo.extend([type, free])
        type, free, currentStorage = self.__parseStorageInfo(currentStorage + '"') #extra quote helps parsing
        storageInfo.extend([type, free])
        
        return storageInfo
    
    
    def __parseStorageInfo(self, info):
        index = info.find('"')
        storageType = info[index:index + 4]
        
        info = info[index + 5:]
        index = info.find('"')
        storageDetails = info[:index].split(',')
        storageFree = int(storageDetails[1]) - int(storageDetails[0])
        
        return storageType, storageFree, info[index:]
    
    
    def __parseSupportedStorage(self, storage):
        start = storage.find('(')
        end = storage.find(')')
        
        readStorage = []
        if start != -1 and end != -1:
            readStorage = storage[start + 1:end].split(',')
        
        storage = storage[end + 1:]
        return readStorage, storage
    

    def __sendATCommand(self, atCommand, lineBreak = True):
        command = atCommand
        if lineBreak:
            command += '\r'
        self.__connection.send(command)
         
        reply = ''
        while not (reply.endswith('OK\r\n') or reply.endswith('ERROR\r\n')):
            reply += self.__connection.recv()
            
        if reply.endswith('OK\r\n'):
            end = reply.rfind('\r\nOK\r\n')
            return reply[2:end]
        else:
            raise Exception, _('AT Command not supported by phone: ') + atCommand[:-1]
            
            
    def __parseMemorySlots(self, reply):
        #+CPBR:(1-100),40,14,0
        begin   = reply.find('-') + 1
        end     = reply.rfind(')')
        return reply[begin:end]


    def __setCharacterSet(self, characterSet):
        self.__sendATCommand('AT+CSCS=' + characterSet)
        
    
    def __getSupportedCharacterSets(self):
        response = self.__sendATCommand('AT+CSCS=?')
        return self.__parseCommaseperatedList(response)


    def __getSupportedSMSModes(self):
        response = self.__sendATCommand('AT+CMGF=?')
        return self.__parseCommaseperatedList(response)

    
    def __parseCommaseperatedList(self, list):
        start = list.find('(') + 1
        end = list.rfind(')')
        return list[start:end].split(',')
