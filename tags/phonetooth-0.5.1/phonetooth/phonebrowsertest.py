import os
import unittest

from phonebrowser import PhoneBrowser

class PhoneBrowserTest(unittest.TestCase):
    def testParseDirectoryListing(self):
        listing =   '''<?xml version="1.0"?>
                    <!DOCTYPE folder-listing SYSTEM "obex-folder-listing.dtd">
                    <folder-listing version="1.0">
                        <folder name="Photos" modified="20040927172336Z"/>
                        <folder name="DownLoaded Images" modified="20040927172336Z"/>
                        <file name="picture.jpg" size="125487"/>
                    </folder-listing>'''
                    
        browser = PhoneBrowser()
        dirs, files = browser.parseDirectoryListing(listing)
                    
        self.assertEqual(2, len(dirs))
        self.assertEqual('Photos', dirs[0])
        self.assertEqual('DownLoaded Images', dirs[1])
        
        self.assertEqual(1, len(files))
        self.assertEqual('picture.jpg', files[0].name)
        self.assertEqual(125487, files[0].size)
        
