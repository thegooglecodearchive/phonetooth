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
        

    def load(self, filename = None):
        if filename == None:
            filename = self.__getContactsLocation()
        
        self.contacts = {}
        try:
            file = open(filename)
            for line in file.readlines():
                splitted = line.split(',')
                if len(splitted) == 2 and len(splitted[0]) > 0 and len(splitted[1]) > 0:
                    self.contacts[splitted[0].strip()] = splitted[1].strip()
        except Exception, e:
            print str(e)
            self.contacts = {}


    def save(self, filename = None):
        if filename == None:
            filename = self.__getContactsLocation()
        
        try:
            file = open(filename, 'w')
            for name, nr in self.contacts.items():
                file.write(name + ', ' + nr + '\n')
            file.close()
        except:
            pass


    def __str__(self):
        contactString = ""
        for contact in self.contacts:
            contactString += contact + " - " + self.contacts[contact] + "\n"
            
        return contactString
        

    def __getContactsLocation(self):
        configDir = os.path.join(os.path.expanduser('~'), '.config/phonetooth')
        
        if not os.path.isdir(configDir):
            os.makedirs(configDir)
            
        return os.path.join(configDir, 'contacts.csv')
