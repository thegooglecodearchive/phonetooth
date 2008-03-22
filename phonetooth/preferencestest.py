import os
import unittest

from preferences import Preferences
from bluetoothdiscovery import BluetoothDevice

class PreferencesTest(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove('prefstest.conf')
        except: pass
        
        
    def testSaveLoad(self):
        prefs = Preferences('prefstest.conf')
        
        self.assertEqual(None, prefs.btDevice)
        self.assertEqual(prefs.backend, 'phonetooth')
        
        prefs.btDevice = BluetoothDevice('00:00:00:00', 42, 'deviceName', 'serviceName')
        prefs.backend = 'backend'
        
        prefs.save()
        
        prefsLoaded = Preferences('prefstest.conf')
        prefsLoaded.load()
        
        self.assertNotEqual(None, prefsLoaded.btDevice, "Device has not been loaded")
        self.assertEqual('00:00:00:00', prefsLoaded.btDevice.address)
        self.assertEqual(42, prefsLoaded.btDevice.port)
        self.assertEqual('deviceName', prefsLoaded.btDevice.deviceName)
        self.assertEqual('serviceName', prefsLoaded.btDevice.serviceName)
        self.assertEqual('backend', prefsLoaded.backend)
