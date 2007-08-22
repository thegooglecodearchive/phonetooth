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

