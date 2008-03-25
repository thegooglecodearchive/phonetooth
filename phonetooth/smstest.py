# coding: utf-8
import unittest

import sms

class SmsTest(unittest.TestCase):
    def testPDU(self):
        smsMsg = sms.Sms('hellohello', '46708251358')
        self.assertEqual(True, smsMsg.is7Bit())
        self.assertEqual('0001000B816407281553F800000AE8329BFD4697D9EC37', smsMsg.getPDU(False))
        
    def testPDUDeliveryReport(self):
        smsMsg = sms.Sms('hellohello', '46708251358')
        self.assertEqual('0021000B816407281553F800000AE8329BFD4697D9EC37', smsMsg.getPDU(True))
        
    def testPDUInternationNr(self):
        smsMsg = sms.Sms('hellohello', '+46708251358')
        self.assertEqual('0001000B916407281553F800000AE8329BFD4697D9EC37', smsMsg.getPDU(False))
        
    def testPDUUnicode(self):
        smsMsg = sms.Sms('Миха Шестоков', '0192292309')
        self.assertEqual(False, smsMsg.is7Bit())
        self.assertEqual('0001000A81102992329000081A041C04380445043000200428043504410442043E043A043E0432', smsMsg.getPDU(False))

