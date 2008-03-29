import os
import unittest

from contacts import Contact
from contacts import ContactList

class ContactsTest(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove('contactsTest.csv')
        except: pass
        
        
    def testSaveLoad(self):
        contactsList = ContactList()
        
        self.assertEqual({}, contactsList.contacts)
        contactsList.addContact(Contact('name1', "1234"))
        contactsList.addContact(Contact('name2', "2345"))
        contactsList.addContact(Contact('name3', "3456"))
        
        contactsList.save('contactsTest.csv')
        
        contactListLoaded = ContactList()
        contactListLoaded.load('contactsTest.csv')
        
        self.assertEqual(3, len(contactListLoaded.contacts))
        self.assertEqual('1234', contactListLoaded.contacts['name1'])
        self.assertEqual('2345', contactListLoaded.contacts['name2'])
        self.assertEqual('3456', contactListLoaded.contacts['name3'])
        
