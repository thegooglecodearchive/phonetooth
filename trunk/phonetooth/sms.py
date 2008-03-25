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

from gettext import gettext as _

class Sms:
    def __init__(self, message = '', recipient = ''):
        self.message = message
        self.recipient = recipient

    
    def is7Bit(self):
        return bit7alphabet.is7bitString(unicode(self.message, 'utf-8'))

    
    def getPDUMessage(self, statusReport):
        recipient = self.recipient
        if recipient[0] == '+':
            recipient = recipient[1:]
            addressType = '91'
        else:
            addressType = '81'
            
        pduMsg = []
            
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
        
        pduMsg.append('00')
        pduMsg.append('21' if statusReport else '01')
        pduMsg.append('00')
        pduMsg.append(self.__byteToString(len(recipient)))
        pduMsg.append(addressType)
        pduMsg.append(self.__phoneNrToOctet(recipient))
        pduMsg.append('00')
        
        if self.is7Bit():
            msg7Bit = bit7alphabet.convert7BitToOctet(self.message)
            pduMsg.append('00')
            pduMsg.append(self.__byteToString(len(self.message)))
            for byte in msg7Bit:
                pduMsg.append(self.__byteToString(byte))
        else:
            unicodeMsg = unicode(self.message, 'utf-8')
            pduMsg.append('08')
            pduMsg.append(self.__byteToString(len(unicodeMsg) * 2))
            for char in unicodeMsg:
                pduMsg.append(self.__unicodeCharToString(char))
               
        return ''.join(pduMsg)
        
    
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


    def __byteToString(self, byte):
        return '%2.2X' % byte


    def __unicodeCharToString(self, char):
        return '%4.4X' % ord(char)

