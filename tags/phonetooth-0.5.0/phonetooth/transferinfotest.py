import os
import unittest

from transferinfo import TransferInfo

class TransferInfoTest(unittest.TestCase):
    def testTransferInfo(self):
        info = TransferInfo()
        
        info.start(10000)
        self.assertEqual(0.0, info.progress)
        self.assertEqual(0, info.kbPersecond)
        self.assertEqual(-1, info.timeRemaining)
        
        info.startNextFile(2000)
        info.update(1000)
        info.update(2000)
        self.assertAlmostEqual(0.2, info.progress)
        self.assertTrue(info.kbPersecond > 0)
        timeRemaining = info.timeRemaining
        
        info.startNextFile(8000)
        info.update(4000)
        self.assertAlmostEqual(0.6, info.progress)
        self.assertTrue(info.kbPersecond > 0)
        timeRemaining = info.timeRemaining
        
        info.update(8000)
        self.assertAlmostEqual(1.0, info.progress)