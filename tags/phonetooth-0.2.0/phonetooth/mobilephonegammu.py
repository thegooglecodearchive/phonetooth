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

try:
    import gammu
except ImportError, e:
    print str(e)

from phonetooth import contacts

class MobilePhoneGammu:
    def __init__(self):
        self.__gammuStateMachine = gammu.StateMachine()
        self.__gammuStateMachine.ReadConfig()
        self.__gammuStateMachine.Init()


    def __del__(self):
        self.__gammuStateMachine.Terminate()
        
    
    def getManufacturer(self):
        return self.__gammuStateMachine.GetManufacturer()
        
        
    def getModel(self):
        return self.__gammuStateMachine.GetModel()
        
        
    def getSerialNumber(self):
        return self.__gammuStateMachine.GetIMEI()
        

    def getBatteryStatus(self):
        return self.__gammuStateMachine.GetBatteryCharge()
        
       
    def sendSMS(self, message, recipient):
        smsData = {'Text': message, 'SMSC': {'Location': 1}, 'Number': recipient}
        self.__gammuStateMachine.SendSMS(smsData)
        
            
    def getContacts(self, location):
        if location == 'SIM':
            type = 'SM'
        elif location == 'PHONE':
            type = 'ME'
        else:
            raise Exception, 'Invalid contact location specified'
            
        contactList = []
        
        status = self.__gammuStateMachine.GetMemoryStatus(Type = type)
        remain = status['Used']
        
        start = True
        while remain > 0:
            if start:
                entry = self.__gammuStateMachine.GetNextMemory(Start = True, Type = type)
                start = False
            else:
                entry = self.__gammuStateMachine.GetNextMemory(Location = entry['Location'], Type = type)
            
            remain = remain - 1
            
            contact = contacts.Contact('', '')
            for v in entry['Entries']:
                if v['Type'] == 'Number_General':
                    contact.phoneNumber = v['Value']
                elif v['Type'] == 'Text_Name':
                    contact.name = v['Value']
                
            if len(contact.name) > 0 and len(contact.phoneNumber) > 0:
                contactList.append(contact)

        return contactList


    def sendFile(self, filename):
        client = obexftp.client(obexftp.BLUETOOTH)
        client.connect(self.__address, 9)
        client.put_file(filename)
        client.disconnect()
        client.delete
        
