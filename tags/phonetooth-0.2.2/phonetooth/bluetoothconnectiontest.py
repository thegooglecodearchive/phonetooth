import unittest
from bluetoothconnection import BluetoothConnection
from bluetoothconnection import BluetoothConnectionException

class BluetoothConnectionTest(unittest.TestCase):
    def testRaiseOnSendWithoutConnect(self):
        conn = BluetoothConnection('address', 1)
        self.assertRaises(BluetoothConnectionException, conn.send, 'data')
        
    def testRaiseOnRecvWithoutConnect(self):
        conn = BluetoothConnection('address', 1)
        self.assertRaises(BluetoothConnectionException, conn.recv, 'data')

