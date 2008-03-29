# coding: utf-8

import os
import unittest

import bit7alphabet

class Bit7AlphabetTest(unittest.TestCase):
    def testIs7bitString(self):
        bit7Alphabet = unicode('X$(,048<ΨΩ€DΠHΣLΦPbT2\\dhflΘpΛtΞxΓΔ|#\'+/37;?CGKOS"W[_czgk&osw{Éàü!%)-159=AEIMQUY]aeimquy}BFJNRVZ^¤¥§¡£jnrv¿~@\f\r\n', 'utf-8')
        self.assertEqual(True, bit7alphabet.is7bitString(bit7Alphabet))
        self.assertEqual(False, bit7alphabet.is7bitString(unicode('Миха Шестоков', 'utf-8')))
        
