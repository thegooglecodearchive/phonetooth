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

import bit7alphabet
import math

class Sms:
    def __init__(self, message = '', recipient = ''):
        self.recipient = recipient
        self.statusReport = False
        
        self.__msgLength = 0
        self.__is7Bit = True
        self.__characters7BitPart = 153
        self.__charactersUnicodePart = 67
        
        self.setMessage(message)

    
    def is7Bit(self):
        return self.__is7Bit

    
    def __checkIs7Bit(self):
        self.__is7Bit = bit7alphabet.is7bitString(self.__message)
        
        
    def getMessage(self):
        return self.__message
    
    
    def getMessageLength(self):
        return self.__msgLength
    
    
    def setMessage(self, message):
        self.__message = unicode(message, 'utf-8')
        self.__checkIs7Bit()
        self.__msgLength = len(self.__message)
        
        
    def getNumMessages(self):
        if self.__is7Bit:
            if self.__msgLength <= 160:
                return 1
            else:
                return int(math.ceil(self.__msgLength / float(self.__characters7BitPart)))
        else:
            if self.__msgLength <= 70:
                return 1
            else:
                return int(math.ceil(self.__msgLength / float(self.__charactersUnicodePart)))
            
    
    def getPDU(self):
        if (self.__is7Bit and self.__msgLength <= 160) or (not self.__is7Bit and self.__msgLength <= 70):
            return [self.__createSinglePartPDU()]
        elif self.__is7Bit:
            return self.__createMultiPartPDU7Bit()
        else:
            return self.__createMultiPartPDUUnicode()
            
    def __createSinglePartPDU(self):
        pduMsg = []
        pduMsg.append(self.__createPDUHeader())
        
        if self.__is7Bit:
            msg7Bit = bit7alphabet.convert7BitToOctet(self.__message)
            pduMsg.append(self.__byteToString(self.__msgLength))
            pduMsg.append(self.__bytesToString(msg7Bit))
        else:
            pduMsg.append(self.__byteToString(self.__msgLength * 2))
            pduMsg.append(self.__unicodeCharsToString(self.__message))
            
        return ''.join(pduMsg)
            
            
    def __createMultiPartPDU7Bit(self):
        charactersPerPart   = self.__characters7BitPart
        charactersLeft      = self.__msgLength
        parts               = self.getNumMessages()
       
        pduMessages = []
        for i in range(0, parts):
            pduMsg = []
            finalPart = charactersLeft <= charactersPerPart
            
            startIndex = i * charactersPerPart
            if finalPart:
                endIndex = startIndex + charactersLeft
            else:
                endIndex = startIndex + charactersPerPart
            udh = self.__createUDHHeader(i+1, parts)
            
            #prepend 7 @ (0x00 in 7bit) characters to the message to have correcrt 7-bit padding after udh
            data = bit7alphabet.convert7BitToOctet('@@@@@@@' + self.__message[startIndex:endIndex])
            
            #overwrite the prepended zeros with udh header
            for index in range(0, len(udh)):
                data[index] = udh[index]

            pduMsg.append(self.__createPDUHeader(i + 1))
            pduMsg.append(self.__byteToString((endIndex - startIndex) + 7)) #dataLength in septets
            pduMsg.append(self.__bytesToString(data))

            pduMessages.append(''.join(pduMsg))
            charactersLeft -= charactersPerPart
            
        return pduMessages
            
    def __createMultiPartPDUUnicode(self):
        data = self.__message
        parts = self.getNumMessages()
        partLength = self.__charactersUnicodePart
            
        charactersLeft = len(data)
        pduMessages = []
        for i in range(0, parts):
            pduMsg = []
            pduMsg.append(self.__createPDUHeader(i + 1))
            
            udh = self.__createUDHHeader(i+1, parts)
            
            finalPart = charactersLeft <= partLength
            startIndex = i * self.__charactersUnicodePart
            if finalPart:
                endIndex = startIndex + charactersLeft
            else:
                endIndex = startIndex +  self.__charactersUnicodePart
            pduMsg.append(self.__byteToString((endIndex - startIndex) * 2 + len(udh)))
            pduMsg.append(self.__bytesToString(udh))
            pduMsg.append(self.__unicodeCharsToString(self.__message[startIndex:endIndex]))
            pduMessages.append(''.join(pduMsg))
            charactersLeft -= partLength
            
        return pduMessages


    def __createPDUHeader(self, partNr = 0):
        #PDU Message Header
        #01         SMS-Submit
        #00         Message reference (Set by phone)
        #length     Message Length
        #81 or 91   Address type 81(national) 91 (international)
        #phone nr
        #00         Protocol
        #00         Data coding scheme (7bit default alphabet = 0x00, UCS2 = 0x08)
        pduHeader = []
        
        smsSubmit = 0x01
        if self.__is7Bit and self.__msgLength > 160:
            smsSubmit = smsSubmit | 0x40
        if not self.__is7Bit and self.__msgLength > 70:
            smsSubmit = smsSubmit | 0x40
        if self.statusReport and partNr == 0:
            smsSubmit = smsSubmit | 0x20
            
        recipient = self.recipient
        international = False
        if recipient[0] == '+':
            recipient = recipient[1:]
            international = True
            
        pduHeader.append('00')
        pduHeader.append(self.__byteToString(smsSubmit))
        pduHeader.append(self.__byteToString(partNr))
        pduHeader.append(self.__byteToString(len(recipient)))
        if international:
            pduHeader.append('91')
        else:
            pduHeader.append('81')
        pduHeader.append(self.__phoneNrToOctet(recipient))
        pduHeader.append('00')
        if self.__is7Bit:
            pduHeader.append('00')
        else:
            pduHeader.append('08')
        
        return ''.join(pduHeader)
        
        
    def __createUDHHeader(self, partNr, nrParts):
        return [0x05, 0x00, 0x03, 0x42, nrParts, partNr]
        
    
    def __phoneNrToOctet(self, phoneNr):
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


    def __bytesToString(self, bytes):
        string = []
        for byte in bytes:
            string.append(self.__byteToString(byte))
            
        return ''.join(string)
    
    
    def __byteToString(self, byte):
        return '%2.2X' % byte


    def __unicodeCharsToString(self, chars):
        string = []
        for char in chars:
            string.append(self.__unicodeCharToString(char))
            
        return ''.join(string)


    def __unicodeCharToString(self, char):
        return '%4.4X' % ord(char)

