#!/usr/bin/env python
import unittest

from phonetooth.mobilephonetest import MobilePhoneTest
from phonetooth.bluetoothconnectiontest import BluetoothConnectionTest
from phonetooth.preferencestest import PreferencesTest
from phonetooth.contactstest import ContactsTest
from phonetooth.bit7alphabettest import Bit7AlphabetTest
from phonetooth.smstest import SmsTest

allTests = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(MobilePhoneTest),
    unittest.TestLoader().loadTestsFromTestCase(BluetoothConnectionTest),
    unittest.TestLoader().loadTestsFromTestCase(PreferencesTest),
    unittest.TestLoader().loadTestsFromTestCase(ContactsTest),
    unittest.TestLoader().loadTestsFromTestCase(Bit7AlphabetTest),
    unittest.TestLoader().loadTestsFromTestCase(SmsTest)
])

unittest.TextTestRunner(verbosity=2).run(allTests)
