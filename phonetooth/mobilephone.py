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

try:
    import obexftp
except ImportError:
    print 'Obexftp not found: File transfer will not be possible'

class MobilePhone:
    def __init__(self, connection, obexPort = 0):
        self.__connection = connection
        self.__obexPort = obexPort
        
    
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


    def sendSMS(self, sms, statusReport = False):
        supportedModes = self.__getSupportedSMSModes()
        if '0' in supportedModes:
            self.__sendSMSPDUMode(sms, statusReport)
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
            self.__sendATCommand(sms.message + chr(26), False) # message + CTRL+Z
        else:
            raise Exception, _('Failed to send message')

 
    def __sendSMSPDUMode(self, sms, statusReport):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=0') # PDU mode
        
        pduMsg = sms.getPDUMessage(statusReport)
        
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


    def sendFile(self, filename):
        if self.__obexPort == 0:
            raise Exception('Current device does not support sending files')
        client = obexftp.client(obexftp.BLUETOOTH)
        client.connect(self.__connection.address, self.__obexPort)
        client.put_file(filename)
        client.disconnect()
        client.delete
        
        
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
