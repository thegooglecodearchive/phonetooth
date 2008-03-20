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

import os
import pickle

class Contact:
    def __init__(self, name, phoneNumber):
        self.name = name
        self.phoneNumber = phoneNumber
        
    def __str__(self):
        return self.name + " - " + self.phoneNumber

class ContactList:
    def __init__(self):
        self.contacts = {}
                
    def addContact(self, contact):
        self.contacts[contact.name] = contact.phoneNumber
        
    def save(self):
        appDir = os.path.expanduser('~') + '/.phonetooth/'
        
        if not os.path.isdir(appDir):
            os.mkdir(appDir)
            
        file = open(appDir + 'contacts', 'wb')
        pickle.dump(self.contacts, file)
        
    def load(self):
        try:
            file = open(os.path.expanduser('~') + '/.phonetooth/contacts', 'rb')
            self.contacts = pickle.load(file)
        except:
            self.contacts = {}
            
    def __str__(self):
        contactString = ""
        for contact in self.contacts:
            contactString += contact + " - " + self.contacts[contact] + "\n"
            
        return contactString

