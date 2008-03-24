# coding: utf-8

import unittest
import mobilephone

class BluetoothConnectionStub:
    def __init__(self):
        self.replies = []
        self.recieves = []
        
    def connect(self):
        pass
            
    def disconnect(self):
        pass

    def send(self, data):
        self.recieves.append(data)

    def recv(self, size = 0, wait = False):
        if size != 0 and size != len(self.replies[0]):
            raise Exception('Expected recieve size ' + str(len(self.replies[0])) + ' does not match ' + str(size))
        
        response = self.replies[0]
        del self.replies[0]
        return response

class MobilePhoneTest(unittest.TestCase):
    mobilePhone = None
    connection = None
    
    def setUp(self):
        self.connection = BluetoothConnectionStub()
        self.mobilePhone = mobilephone.MobilePhone(self.connection)
        
    def tearDown(self):
        del self.connection
        self.connection = None
        del self.mobilePhone
        self.mobilePhone = None
        
    def assertSent(self, data):
        self.assertEqual(data, self.connection.recieves[0])
        del self.connection.recieves[0]

    def testConnect(self):
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('("GSM")\r\nOK\r\n')
        
        self.mobilePhone.connect()
        
        self.assertSent('ATE0\r')
        self.assertSent('AT+CSCS=?\r')
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testConnectUtf8Supported(self):
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('("GSM","UTF-8")\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.connect()
        
        self.assertSent('ATE0\r')
        self.assertSent('AT+CSCS=?\r')
        self.assertSent('AT+CSCS="UTF-8"\r')
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))

    def testGetManufacturer(self):
        self.connection.replies.append('\r\nManufacturer\r\nOK\r\n')
        self.assertEqual('Manufacturer', self.mobilePhone.getManufacturer())
        self.assertSent('AT+CGMI\r')
        self.assertEqual(0, len(self.connection.recieves))
        
    def testGetModel(self):
        self.connection.replies.append('\r\nModel\r\nOK\r\n')
        self.assertEqual('Model', self.mobilePhone.getModel())
        self.assertSent('AT+CGMM\r')
        self.assertEqual(0, len(self.connection.recieves))

    def testGetSerialNumber(self):
        self.connection.replies.append('\r\n000-123456-000\r\nOK\r\n')
        self.assertEqual('000-123456-000', self.mobilePhone.getSerialNumber())
        self.assertSent('AT+CGSN\r')
        self.assertEqual(0, len(self.connection.recieves))

    def testGetBatteryStatus(self):
        self.connection.replies.append('\r\n0,80\r\nOK\r\n')
        self.assertEqual(80, self.mobilePhone.getBatteryStatus())
        self.assertSent('AT+CBC\r')
        self.assertEqual(0, len(self.connection.recieves))
        
    def testSendSMSTextMode(self):
        self.connection.replies.append('\r\n(1)\r\nOK\r\n') #phone supports text and pdu, so text will be chosen
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('AT+CMGS="+320497123456"\r\r\n> ')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.sendSMS('Message\r\nNext line', '+320497123456')
        
        self.assertSent('AT+CMGF=?\r')
        self.assertSent('ATZ\r')
        self.assertSent('AT+CMGF=1\r')
        self.assertSent('AT+CMGS="+320497123456"\r')
        self.assertSent('Message\r\nNext line' + chr(26))
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testSendSMSPDUMode(self):
        self.connection.replies.append('\r\n(0,1)\r\nOK\r\n') #phone supports only pdu, so pdu will be chosen
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('AT+CMGS=22\r\r\n> ')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.sendSMS('hellohello', '46708251358')
        
        self.assertSent('AT+CMGF=?\r')
        self.assertSent('ATZ\r')
        self.assertSent('AT+CMGF=0\r')
        self.assertSent('AT+CMGS=22\r')
        self.assertSent('0001000B816407281553F800000AE8329BFD4697D9EC37' + chr(26))
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testSendSMSPDUModeStatusReport(self):
        self.connection.replies.append('\r\n(0)\r\nOK\r\n') #phone supports only pdu, so pdu will be chosen
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('AT+CMGS=22\r\r\n> ')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.sendSMS('hellohello', '46708251358', statusReport=True)
        
        self.assertSent('AT+CMGF=?\r')
        self.assertSent('ATZ\r')
        self.assertSent('AT+CMGF=0\r')
        self.assertSent('AT+CMGS=22\r')
        self.assertSent('0021000B816407281553F800000AE8329BFD4697D9EC37' + chr(26))
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testSendSMSPDUModeUnicode(self):
        self.connection.replies.append('\r\n(0)\r\nOK\r\n') #phone supports only pdu, so pdu will be chosen
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('AT+CMGS=38\r\r\n> ')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.sendSMS('Миха Шестоков', '0192292309')
        
        self.assertSent('AT+CMGF=?\r')
        self.assertSent('ATZ\r')
        self.assertSent('AT+CMGF=0\r')
        self.assertSent('AT+CMGS=38\r')
        self.assertSent('0001000A81102992329000081A041C04380445043000200428043504410442043E043A043E0432' + chr(26))
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testSendSMSPDUModeInternational(self):
        self.connection.replies.append('\r\n(0)\r\nOK\r\n') #phone supports only pdu, so pdu will be chosen
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('AT+CMGS=22\r\r\n> ')
        self.connection.replies.append('\r\nOK\r\n')
        
        self.mobilePhone.sendSMS('hellohello', '+46708251358')
        
        self.assertSent('AT+CMGF=?\r')
        self.assertSent('ATZ\r')
        self.assertSent('AT+CMGF=0\r')
        self.assertSent('AT+CMGS=22\r')
        self.assertSent('0001000B916407281553F800000AE8329BFD4697D9EC37' + chr(26))
        self.assertEqual(0, len(self.connection.recieves))
        self.assertEqual(0, len(self.connection.replies))
        
    def testGetContactsFromSIM(self):
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\n+CPBR:(1-100),40,14,0\r\nOK\r\n')
        self.connection.replies.append('+CPBR: 1,"1234",129,"Name 1",0\r\n'
                                       '+CPBR: 2,"2345",129,"Name 2",0\r\n'
                                       '+CPBR: 3,"3456",129,"Name 3",0\r\nOK\r\n')
        
        contacts = self.mobilePhone.getContacts('SIM')
        
        self.assertSent('AT+CPBS="SM"\r')
        self.assertSent('AT+CPBR=?\r')
        self.assertSent('AT+CPBR=1,100\r')
        
        self.assertEqual("1234", contacts[0].phoneNumber)
        self.assertEqual("Name 1", contacts[0].name)
        self.assertEqual("2345", contacts[1].phoneNumber)
        self.assertEqual("Name 2", contacts[1].name)
        self.assertEqual("3456", contacts[2].phoneNumber)
        self.assertEqual("Name 3", contacts[2].name)
        
    def testGetContactsFromPhone(self):
        self.connection.replies.append('\r\nOK\r\n')
        self.connection.replies.append('\r\n+CPBR:(1-100),40,14,0\r\nOK\r\n')
        self.connection.replies.append('+CPBR: 1,"1234",129,"Name 1",0\r\n'
                                       '+CPBR: 2,"2345",129,"Name 2",0\r\n'
                                       '+CPBR: 3,"3456",129,"Name 3",0\r\nOK\r\n')
        
        contacts = self.mobilePhone.getContacts('PHONE')
        
        self.assertSent('AT+CPBS="ME"\r')
        self.assertSent('AT+CPBR=?\r')
        self.assertSent('AT+CPBR=1,100\r')
        
        self.assertEqual("1234", contacts[0].phoneNumber)
        self.assertEqual("Name 1", contacts[0].name)
        self.assertEqual("2345", contacts[1].phoneNumber)
        self.assertEqual("Name 2", contacts[1].name)
        self.assertEqual("3456", contacts[2].phoneNumber)
        self.assertEqual("Name 3", contacts[2].name)
