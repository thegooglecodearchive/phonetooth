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
        

    def testFindCollisions(self):
        contactList1 = ContactList();
        contactList1.addContact(Contact('name1', "1234"))
        contactList1.addContact(Contact('name2', "2345"))
        contactList1.addContact(Contact('name3', "3456"))
        
        contactList2 = ContactList();
        
        self.assertEqual(0, len(contactList1.findCollisions(contactList2)))
        
        contactList2.addContact(Contact('name1', "6789"))
        contactList2.addContact(Contact('name2', "2345"))
        contactList2.addContact(Contact('name4', "1234"))
        
        collisions = contactList1.findCollisions(contactList2)
        self.assertEqual(1, len(collisions))
        self.assertEqual("name1", collisions[0].name)
        self.assertEqual("1234", collisions[0].phoneNumber1)
        self.assertEqual("6789", collisions[0].phoneNumber2)

    def testMergeLists(self):
        contactList1 = ContactList();
        contactList1.addContact(Contact('name1', "1234"))
        contactList1.addContact(Contact('name2', "2345"))
        contactList1.addContact(Contact('name3', "3456"))

        contactList2 = ContactList();
        contactList2.addContact(Contact('name1', "6789"))
        contactList2.addContact(Contact('name2', "6789"))
        contactList2.addContact(Contact('name3', "6789"))

        contactList1.mergeContacts(contactList2)
        self.assertEqual(3, len(contactList1.contacts))
        self.assertEqual('1234', contactList1.contacts['name1'])
        self.assertEqual('2345', contactList1.contacts['name2'])
        self.assertEqual('3456', contactList1.contacts['name3'])

        contactList2.addContact(Contact('name4', "6789"))

        contactList1.mergeContacts(contactList2)
        self.assertEqual(4, len(contactList1.contacts))
        self.assertEqual('1234', contactList1.contacts['name1'])
        self.assertEqual('2345', contactList1.contacts['name2'])
        self.assertEqual('3456', contactList1.contacts['name3'])
        self.assertEqual('6789', contactList1.contacts['name4'])


    def testMergeListsWithCollisionsResolving(self):
        contactList1 = ContactList();
        contactList1.addContact(Contact('name1', "1234"))
        contactList1.addContact(Contact('name2', "2345"))
        contactList1.addContact(Contact('name3', "3456"))

        contactList2 = ContactList();
        contactList2.addContact(Contact('name1', "6789"))
        contactList2.addContact(Contact('name2', "6789"))
        contactList2.addContact(Contact('name3', "6789"))

        resolvedCollisions = ContactList();
        resolvedCollisions.addContact(Contact('name1', "1234"))
        resolvedCollisions.addContact(Contact('name2', "6789"))
        resolvedCollisions.addContact(Contact('name3', "6789"))

        contactList1.mergeContacts(contactList2, resolvedCollisions)
        self.assertEqual(3, len(contactList1.contacts))
        self.assertEqual('1234', contactList1.contacts['name1'])
        self.assertEqual('6789', contactList1.contacts['name2'])
        self.assertEqual('6789', contactList1.contacts['name3'])
