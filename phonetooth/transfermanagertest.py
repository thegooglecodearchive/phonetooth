import os
import unittest

from transfermanager import TransferManager
from phonebrowserstub import PhoneBrowserStub
from filecollection import File
from filecollection import Directory

class TransferManagerTest(unittest.TestCase):
    transfersCompleted = False
    
    def transfersCompletedCb(self, sender = None):
        self.transfersCompleted = True
        
    def setup(self):
        self.transfersCompleted = False
        
    def tearDown(self):
        if os.path.exists('subdir'):
            os.removedirs('subdir')
        if os.path.exists('subdir1'):
            os.removedirs('subdir1')
        if os.path.exists('subdir2'):
            os.removedirs('subdir2')
       
    
    def testTransferToRemote(self):
        phoneBrowser = PhoneBrowserStub()
        
        transferMgr = TransferManager(phoneBrowser)
        transferMgr.connect('transferscompleted', self.transfersCompletedCb)
        
        fileCollection = Directory()
        fileCollection.addFile(File('file1.tst', 100))
        fileCollection.addFile(File('subdir/file2.tst', 200))
        fileCollection.addFile(File('subdir/file3.tst', 300))

        transferMgr.copyToRemote(fileCollection)
        
        self.assertEqual('file1.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertEqual('subdir/file2.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertEqual('subdir/file3.tst', phoneBrowser.lastFileCopied)
        
        phoneBrowser.emit('completed')
        self.assertTrue(self.transfersCompleted)
        
    def testTransferToLocal(self):
        phoneBrowser = PhoneBrowserStub()
        
        transferMgr = TransferManager(phoneBrowser)
        transferMgr.connect('transferscompleted', self.transfersCompletedCb)
        
        fileCollection = Directory('.')
        fileCollection.addFile(File('file1.tst', 100))
        
        dir = Directory('subdir')
        dir.parent = fileCollection
        dir.addFile(File('subfile1.tst', 200))
        dir.addFile(File('subfile2.tst', 300))

        fileCollection.addDirectory(dir)
        
        transferMgr.copyToLocal(fileCollection, '.')
        self.assertEqual('subdir', phoneBrowser.curDir)
        self.assertEqual('subfile1.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertEqual('subdir', phoneBrowser.curDir)
        self.assertEqual('subfile2.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertTrue(phoneBrowser.dirUp)
        self.assertEqual('file1.tst', phoneBrowser.lastFileCopied)
        
        phoneBrowser.emit('completed')
        self.assertTrue(self.transfersCompleted)
        
    
    def testTransferToLocalDirOnly(self):
        phoneBrowser = PhoneBrowserStub()
        
        transferMgr = TransferManager(phoneBrowser)
        transferMgr.connect('transferscompleted', self.transfersCompletedCb)
        
        fileCollection = Directory('.')
        
        dir1 = Directory('subdir1')
        dir1.parent = fileCollection
        dir1.addFile(File('sub1file1.tst', 200))
        dir1.addFile(File('sub1file2.tst', 300))
        
        dir2 = Directory('subdir2')
        dir2.parent = fileCollection
        dir2.addFile(File('sub2file1.tst', 200))
        dir2.addFile(File('sub2file2.tst', 300))

        fileCollection.addDirectory(dir1)
        fileCollection.addDirectory(dir2)
        
        transferMgr.copyToLocal(fileCollection, '.')
        self.assertEqual('subdir1', phoneBrowser.curDir)
        self.assertEqual('sub1file1.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        self.assertTrue(os.path.exists('subdir1'))
        self.assertTrue(os.path.isdir('subdir1'))
        
        phoneBrowser.emit('completed')
        self.assertEqual('subdir1', phoneBrowser.curDir)
        self.assertEqual('sub1file2.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertTrue(phoneBrowser.dirUp)
        self.assertEqual('subdir2', phoneBrowser.curDir)
        self.assertEqual('sub2file1.tst', phoneBrowser.lastFileCopied)
        self.assertTrue(os.path.exists('subdir2'))
        self.assertTrue(os.path.isdir('subdir2'))
        
        phoneBrowser.emit('completed')
        self.assertEqual('subdir2', phoneBrowser.curDir)
        self.assertEqual('sub2file2.tst', phoneBrowser.lastFileCopied)
        
        phoneBrowser.emit('completed')
        self.assertTrue(self.transfersCompleted)
        
        
    def testTransferToLocalFilesOnly(self):
        phoneBrowser = PhoneBrowserStub()
        
        transferMgr = TransferManager(phoneBrowser)
        transferMgr.connect('transferscompleted', self.transfersCompletedCb)
        
        fileCollection = Directory('.')
        fileCollection.addFile(File('file1.tst', 200))
        fileCollection.addFile(File('file2.tst', 300))

        transferMgr.copyToLocal(fileCollection, '.')
        self.assertEqual('file1.tst', phoneBrowser.lastFileCopied)
        self.assertFalse(self.transfersCompleted)
        
        phoneBrowser.emit('completed')
        self.assertEqual('file2.tst', phoneBrowser.lastFileCopied)
        
        phoneBrowser.emit('completed')
        self.assertTrue(self.transfersCompleted)
        
        