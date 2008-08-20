import unittest

from filecollection import File
from filecollection import Directory

class FileCollectionTest(unittest.TestCase):
    def testGetSize(self):
        dir = Directory('subdir')
        dir.addFile(File('subfile1.tst', 200))
        dir.addFile(File('subfile2.tst', 300))
        
        fileCollection = Directory()
        fileCollection.addFile(File('file1.tst', 100))
        fileCollection.addDirectory(dir)
        
        self.assertEqual(600, fileCollection.getSize())
        
        