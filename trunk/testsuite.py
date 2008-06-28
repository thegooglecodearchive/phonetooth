#!/usr/bin/env python
import unittest

from phonetooth.mobilephonetest import MobilePhoneTest
from phonetooth.bluetoothconnectiontest import BluetoothConnectionTest
from phonetooth.preferencestest import PreferencesTest
from phonetooth.contactstest import ContactsTest
from phonetooth.bit7alphabettest import Bit7AlphabetTest
from phonetooth.smstest import SmsTest
from phonetooth.phonebrowsertest import PhoneBrowserTest
from phonetooth.transferinfotest import TransferInfoTest
from phonetooth.transfermanagertest import TransferManagerTest
from phonetooth.filecollectiontest import FileCollectionTest

allTests = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(MobilePhoneTest),
    unittest.TestLoader().loadTestsFromTestCase(BluetoothConnectionTest),
    unittest.TestLoader().loadTestsFromTestCase(PreferencesTest),
    unittest.TestLoader().loadTestsFromTestCase(ContactsTest),
    unittest.TestLoader().loadTestsFromTestCase(Bit7AlphabetTest),
    unittest.TestLoader().loadTestsFromTestCase(SmsTest),
    unittest.TestLoader().loadTestsFromTestCase(PhoneBrowserTest),
    unittest.TestLoader().loadTestsFromTestCase(TransferInfoTest),
    unittest.TestLoader().loadTestsFromTestCase(TransferManagerTest),
    unittest.TestLoader().loadTestsFromTestCase(FileCollectionTest)
])

unittest.TextTestRunner(verbosity=2).run(allTests)
