# coding: utf-8
import unittest

import sms

class SmsTest(unittest.TestCase):
    def testGetNumMessages(self):
        smsMsg = sms.Sms('hellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohello', '46708251358')
        self.assertEqual(1, smsMsg.getNumMessages())
        
        smsMsg = sms.Sms('hellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohello!', '46708251358')
        self.assertEqual(2, smsMsg.getNumMessages())
        
        smsMsg = sms.Sms('МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто ', '46708251358')
        self.assertEqual(1, smsMsg.getNumMessages())
        
        smsMsg = sms.Sms('МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто е', '46708251358')
        self.assertEqual(2, smsMsg.getNumMessages())
        

    def testPDU(self):
        smsMsg = sms.Sms('hellohello', '46708251358')
        self.assertEqual(True, smsMsg.is7Bit())
        messages = smsMsg.getPDU(False)
        self.assertEqual(1, len(messages))
        self.assertEqual('0001000B816407281553F800000AE8329BFD4697D9EC37', messages[0])
        
    def testPDUDeliveryReport(self):
        smsMsg = sms.Sms('hellohello', '46708251358')
        messages = smsMsg.getPDU(True)
        self.assertEqual(1, len(messages))
        self.assertEqual('0021000B816407281553F800000AE8329BFD4697D9EC37', messages[0])
        
    def testPDUInternationNr(self):
        smsMsg = sms.Sms('hellohello', '+46708251358')
        messages = smsMsg.getPDU(False)
        self.assertEqual(1, len(messages))
        self.assertEqual('0001000B916407281553F800000AE8329BFD4697D9EC37', messages[0])
        
    def testPDUUnicode(self):
        smsMsg = sms.Sms('Миха Шестоков', '0192292309')
        self.assertEqual(False, smsMsg.is7Bit())
        messages = smsMsg.getPDU(False)
        self.assertEqual(1, len(messages))
        self.assertEqual('0001000A81102992329000081A041C04380445043000200428043504410442043E043A043E0432', messages[0])
        
    def testPDUMultiPart(self):
        smsMsg = sms.Sms('01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789', '0192292309')
        messages = smsMsg.getPDU(False)
        self.assertEqual(2, len(messages))
        self.assertEqual('0041010A8110299232900000A00500034202016031D98C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E56031D98C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E56031D98C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D9783C564335ACD76C3E56031D98C56B3DD7039584C36A3D56C375C0E1693CD6835DB0D9783C56432', messages[0])
        self.assertEqual('0041020A81102992329000001805000342020266B49AED86CBC162B219AD66BBE17239', messages[1])
        
    def testPDUMultiPartUnicode(self):
        smsMsg = sms.Sms('МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто МихаШесто е', '0192292309')
        messages = smsMsg.getPDU(False)
        self.assertEqual(2, len(messages))
        self.assertEqual('0041010A81102992329000088C050003420201041C0438044504300428043504410442043E0020041C0438044504300428043504410442043E0020041C0438044504300428043504410442043E0020041C0438044504300428043504410442043E0020041C0438044504300428043504410442043E0020041C0438044504300428043504410442043E0020041C043804450430042804350441', messages[0])
        self.assertEqual('0041020A81102992329000080E0500034202020442043E00200435', messages[1])

