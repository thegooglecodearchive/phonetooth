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
import obexftp
import bit7alphabet

from phonetooth import contacts

class MobilePhone:
    def __init__(self, device):
        if device == None:
            self.__sock = None
            raise Exception, 'No device configured in preferences'
                
        self.__address = device.address
        try:
            self.__sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.__sock.connect((device.address, device.port))
            self.__sendATCommand('ATE0')
        except bluetooth.BluetoothError, e:
            raise Exception, 'Failed to connect to device: ' + str(e)
            
        
    def __del__(self):
        if self.__sock != None:
            self.__sock.close()
            
        
    def getManufacturer(self):
        return self.__sendATCommand('AT+CGMI')
        
        
    def getModel(self):
        return self.__sendATCommand('AT+CGMM')
        
        
    def getSerialNumber(self):
        return self.__sendATCommand('AT+CGSN')
        

    def getBatteryStatus(self):
        return self.__sendATCommand('AT+CBC')
        
       
    def powerOff(self):
        return self.__sendATCommand('AT+CPOF')
        
        
    def sendSMS(self, message, recipient):
        supportedModes = self.__getSupportedSMSModes()
        if '1' in supportedModes:
             self.sendSMSTextMode(message, recipient)
        elif '0' in supportedModes:
            elf.sendSMSPDUMode(message, recipient)
        else:
            raise Exception, 'Sending SMS not supported by phone'
 
 
    def sendSMSTextMode(self, message, recipient):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=1') # text mode
        
        # send message information and wait for prompt
        messageCommand = 'AT+CMGS="' + recipient + '"\r'
        self.__sock.sendall(messageCommand)
        reply = self.__sock.recv(len(messageCommand) + 4, socket.MSG_WAITALL) # read message + '\r\n> '

        if reply[-2:] == '> ':
            self.__sendATCommand(message + chr(26), False) # message + CTRL+Z
        else:
            raise Exception, 'Failed to send message'
            
 
    def sendSMSPDUMode(self, message, recipient):
        self.__sendATCommand('ATZ')
        self.__sendATCommand('AT+CMGF=0') # PDU mode
        
        if recipient[0] == '+':
            addressType = '91'
            recipientLen = len(recipient) - 1
        else:
            addressType = '81'
            recipientLen = len(recipient)
            
        #PDU Message
        #11         SMS-Submit
        #00         Message reference (Set by phone)
        #length     Message Length
        #81 or 91   Address type 81(national) 91 (international)
        #phone nr
        #00         Protocol
        #00         Data coding scheme (7bit default alphabet)
        #length     User data length
        #user data
        
        pduMsg = '000100' + self.__byteToString(recipientLen)
        pduMsg += addressType + self.__phoneNrToOctet(recipient)
        pduMsg += '0000' + self.__byteToString(len(message))
        msg7Bit = bit7alphabet.convert7BitToOctet(message)
        for byte in msg7Bit:
            pduMsg += self.__byteToString(byte)
        
        # send message information and wait for prompt
        messageCommand = 'AT+CMGS=' + str(len(pduMsg) / 2 - 1) + '\r'
        self.__sock.sendall(messageCommand)
        reply = self.__sock.recv(len(messageCommand) + 4, socket.MSG_WAITALL) # read message + '\r\n> '

        if reply[-2:] == '> ':
            self.__sendATCommand(pduMsg + chr(26), False) # message + CTRL+Z
        else:
            raise Exception, 'Failed to send message'
            
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
        client = obexftp.client(obexftp.BLUETOOTH)
        client.connect(self.__address, 9)
        client.put_file(filename)
        client.disconnect()
        client.delete
        
        
    def __sendATCommand(self, atCommand, lineBreak = True):
        command = atCommand
        if lineBreak:
            command += '\r'
        self.__sock.sendall(command)
         
        reply = ""
        while not (reply.endswith('OK\r\n') or reply.endswith('ERROR\r\n')):
            reply += self.__sock.recv(1024)
            
        if reply.endswith('OK\r\n'):
            end = reply.rfind('\r\nOK\r\n')
            return reply[2:end]
        else:
            raise Exception, 'AT Command: ' + atCommand[:-1] + ' not supported by phone'
            
            
    def __parseMemorySlots(self, reply):
        #+CPBR:(1-100),40,14,0
        begin   = reply.find('-') + 1
        end     = reply.rfind(')')
        
        return reply[begin:end]
        
        
    def __getSupportedSMSModes(self):
        response = self.__sendATCommand('AT+CMGF=?')
        start = response.find('(')
        end = response.rfind(')')
        
        return response.strip(',')
        
        
    def __phoneNrToOctet(self, phoneNr):
        if phoneNr[0] == '+':
            phoneNr = phoneNr[1:]
            
        result = ''
        i = 0
        while (i + 1) < len(phoneNr):
            result += phoneNr[i + 1]
            result += phoneNr[i]
            i += 2
            
        if len(phoneNr) % 2 != 0:
            result += 'F'
            result += phoneNr[len(phoneNr) - 1]
            
        return result
        
        
    def __byteToString(self, byte):
        return '%2.2X' % byte

