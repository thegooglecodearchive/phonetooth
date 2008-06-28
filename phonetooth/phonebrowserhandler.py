#    Copyright (C) 2008 Dirk Vanden Boer <dirk.vdb@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import gtk
import threading
import gobject
import mimetypes
import urlparse
import urllib
import time

import phonebrowser
import transfermanager

from filecollection import File
from filecollection import Directory

from gettext import gettext as _

class PhoneBrowserHandler(gobject.GObject):
    __gsignals__ =  {
        "disconnected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
    }
    
    def __init__(self, widgetTree, parent):
        gobject.GObject.__init__(self)
        
        self.__ignoreEvents = False
        
        self.__iconView             = widgetTree.get_widget('iconView')
        self.__deleteButton         = widgetTree.get_widget('deleteToolButton')
        self.__navigationBox        = widgetTree.get_widget('navigationBox')
        self.__activeNavButton      = widgetTree.get_widget('rootNavButton')
        self.__inputDialog          = widgetTree.get_widget('inputDialog')
        self.__inputLabel           = widgetTree.get_widget('inputLabel')
        self.__inputEntry           = widgetTree.get_widget('inputEntry')
        self.__statusBar            = widgetTree.get_widget('statusBar')
        self.__sendFileDialog       = widgetTree.get_widget('sendFileDialog')
        self.__transferProgressBar  = widgetTree.get_widget('transferProgress')
        self.__filenameLabel        = widgetTree.get_widget('filenameLabel')
        self.__parent = parent
        
        self.__treeModel = gtk.ListStore(str, gtk.gdk.Pixbuf, bool, int)
        
        self.__iconTheme    = gtk.icon_theme_get_default()
        self.__dirImage     = self.__iconTheme.load_icon('folder', 36, gtk.ICON_LOOKUP_FORCE_SVG)
        self.__fileImage    = self.__iconTheme.load_icon('misc', 36, gtk.ICON_LOOKUP_FORCE_SVG)

        self.__phoneBrowser = phonebrowser.PhoneBrowser()
        self.__phoneBrowser.connect('connected', self.__connectedCb)
        self.__phoneBrowser.connect('disconnected', self.__disconnectedCb)
        self.__phoneBrowser.connect('started', self.__transferStartedCb)
        self.__phoneBrowser.connect('error', self.__errorCb)
        
        self.__transferManager = transfermanager.TransferManager(self.__phoneBrowser)
        self.__transferManager.connect('transferscompleted', self.__transferCompletedCb)
        self.__transferManager.connect('progress', self.__transferProgressCb)
        
        self.__iconView.set_model(self.__treeModel)
        self.__iconView.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('XdndDirectSave0', gtk.TARGET_OTHER_APP, 0)], gtk.gdk.ACTION_COPY)
        self.__iconView.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('text/uri-list', 0, 100)], gtk.gdk.ACTION_COPY)
        
        
        dic = {'onIconActivated'            : self.__iconActivated,
               'onDeleteFileClicked'        : self.__deleteFile,
               'onSelectionChanged'         : self.__selectionChanged,
               'onRootButtonClicked'        : self.__naviGationButtonClick,
               'onCreateDir'                : self.__createDir,
               'onDragBegin'                : self.__onDragBegin,
               'onDragDataGet'              : self.__dragDataGet,
               'onDragDataReceived'         : self.__dragDataReceived,
               'onIconViewDragDrop'         : self.__onDrop,
               'onIconViewKeyReleased'      : self.__iconViewKeyReleased
        }
        widgetTree.signal_autoconnect(dic)
        mimetypes.init()


    def __del__(self):
        self.disconnectFromPhone()
        

    def connectToPhone(self, btAddress):
        self.__resetNavigationBar()
        self.__phoneBrowser.connectToPhone(btAddress)
        
    
    def isConnected(self):
        return self.__phoneBrowser.isConnected()
    
    
    def disconnectFromPhone(self):
        self.__treeModel.clear()
        self.__phoneBrowser.disconnectFromPhone()
        
        
    def __connectedCb(self, data):
        self.__showCurrentDir()
        
    
    def __disconnectedCb(self, data):
        self.emit('disconnected')
        
    
    def __iconActivated(self, widget, path):
        iter = self.__treeModel.iter_nth_child(None, int(path[0]))
        item = self.__treeModel.get_value(iter, 0)
        isDir = self.__treeModel.get_value(iter, 2)
        
        if isDir == True:
            self.__cleanNavigationBar()
            
            newButton = gtk.ToggleButton(item)
            newButton.set_border_width(3)
            newButton.connect('toggled', self.__naviGationButtonClick)
            self.__navigationBox.pack_start(newButton, expand = False, fill = False)
            
            newButton.set_active(True)
            self.__navigationBox.set_homogeneous(False)
            self.__navigationBox.show_all()
        else:
            chooser = gtk.FileChooserDialog(title = 'Choose directory', parent = self.__parent, action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            if chooser.run() == gtk.RESPONSE_OK:
                dir = chooser.get_filename()
                chooser.destroy()
                fileCollection = Directory()
                fileCollection.addFile(File(item, self.__treeModel.get_value(iter, 3)))
                self.__transferFilesToLocal(fileCollection, dir)
            else:
                chooser.destroy()
                
                
    def __transferFilesToLocal(self, directory, destinationPath):
        self.__transferManager.copyToLocal(directory, destinationPath)
        self.__showTransferDialog()
        
    
    def __transferFilesToRemote(self, directory):
        self.__transferManager.copyToRemote(directory)
        self.__showTransferDialog()
        
        
    def __showTransferDialog(self):
        self.__transferProgressBar.set_fraction(0.0)
        self.__transferProgressBar.set_text('')
        self.__filenameLabel.set_text('')
        
        response = self.__sendFileDialog.run()
        if response == gtk.RESPONSE_CANCEL:
            self.__phoneBrowser.cancel()
            self.__statusBar.push(0, _('File transfer cancelled.'))
        elif response == 1:
            self.__statusBar.push(0, _('File transfer failed') + '.')
        else:
            self.__statusBar.push(0, _('File succesfully recieved.'))
        self.__sendFileDialog.hide()

            
    def __deleteFile(self, widget = None):
        items = self.__iconView.get_selected_items()
        for item in items:
            iter = self.__treeModel.get_iter(item)
            path = self.__treeModel.get_value(iter, 0)
            
            try:
                self.__phoneBrowser.deleteFile(path)
                self.__showCurrentDir()
            except:
                self.__statusBar.push(0, _('Failed to delete item' + ': ' + path))
        
    
    def __showCurrentDir(self):
        self.__treeModel.clear()
        
        dirs, files = self.__phoneBrowser.getDirectoryListing()
        dirs.sort()
        files.sort()
        
        for dir in dirs:
            self.__treeModel.append((dir, self.__dirImage, True, 0))
        for file in files:
            mime = mimetypes.guess_type(file.name)[0]
            mime = mime.replace('/', '-')
            try:
                pixbuf = self.__iconTheme.load_icon(mime, 36, gtk.ICON_LOOKUP_FORCE_SVG)
            except:
                try:
                    pos = mime.find('-')
                    if pos > 0:
                        pixbuf = self.__iconTheme.load_icon(mime[:pos], 36, gtk.ICON_LOOKUP_FORCE_SVG)
                    else:
                        pixbuf = self.__fileImage
                except:
                    pixbuf = self.__fileImage
            self.__treeModel.append((file.name, pixbuf, False, file.size))
            
        self.__iconView.grab_focus()    
        
    
    def __selectionChanged(self, widget):
        self.__deleteButton.set_sensitive(len(widget.get_selected_items()) != 0)
        
        totalSize = 0
        items = self.__iconView.get_selected_items()
        for item in items:
            iter = self.__treeModel.get_iter(item)
            isDir = self.__treeModel.get_value(iter, 2)
            
            if not isDir:
                totalSize += self.__treeModel.get_value(iter, 3)
        
        self.__statusBar.push(0, '%d %s (%d kb)' % (len(items), _('items selected'), totalSize / 1024))
        
        
    def __disableAllNavigation(self):
        for child in self.__navigationBox.get_children():
            child.set_active(False)
        
            
    def __naviGationButtonClick(self, button):
        if self.__ignoreEvents or button.get_label() == self.__activeNavButton.get_label():
            return

        self.__ignoreEvents = True
        self.__disableAllNavigation()

        button.set_active(True)
        self.__activeNavButton = button
        self.__changeToNewPath(button.get_label())
        self.__showCurrentDir()
            
        self.__ignoreEvents = False
        
    
    def __createDir(self, widget):
        dir = self.__askDirectoryName()
        if dir == None:
            return
        
        try:
            self.__phoneBrowser.createDirectory(dir)
            self.__showCurrentDir()
        except Exception, e:
            self.__statusBar.push(0, _('Create directory not allowed'))
                
                
    def __resetNavigationBar(self):
        self.__activeNavButton = self.__navigationBox.get_children()[0]
        self.__cleanNavigationBar()
        self.__activeNavButton.set_active(True)
                
    
    def __cleanNavigationBar(self):
        curDir = self.__activeNavButton.get_label()
        tooDeep = False
        for child in self.__navigationBox.get_children():
            if tooDeep:
                self.__navigationBox.remove(child)
            
            if child.get_label() == curDir:
                tooDeep = True
        
        
    def __changeToNewPath(self, finalDir):
        self.__phoneBrowser.gotoRoot()
        
        if finalDir == '/':
            return            
            
        for child in self.__navigationBox.get_children():
            dir = child.get_label()
            if dir == '/':
                continue
            
            self.__phoneBrowser.changeDirectory(dir)
            if finalDir == dir:
                break
            
        self.__showCurrentDir()
        
    
    def __askDirectoryName(self):
        text = _('Enter directory name')
        self.__inputDialog.set_title(text)
        self.__inputLabel.set_text(text + ':')
        self.__inputEntry.set_text('')
        
        dir = None
        if self.__inputDialog.run() == gtk.RESPONSE_OK:
            dir = self.__inputEntry.get_text()
            print dir
        
        self.__inputDialog.hide()
        return dir
    
    
    def __transferStartedCb(self, sender, filename):
        gobject.idle_add(self.__filenameLabel.set_text, os.path.basename(filename))
        
    
    def __transferProgressCb(self, sender = None):
        transferInfo = self.__transferManager.transferInfo
        gobject.idle_add(self.__transferProgressBar.set_fraction, transferInfo.progress)
        statusString = str(transferInfo.kbPersecond) + ' kb/s  '

        if transferInfo.timeRemaining != -1:
            if transferInfo.timeRemaining >= 60:
                statusString += '(' + str(transferInfo.timeRemaining / 60 + 1) + _(' minutes remaining') + ')'
            else:
                statusString += '(' + str(transferInfo.timeRemaining / 10 * 10 + 10) + _(' seconds remaining') + ')'
        
        gobject.idle_add(self.__transferProgressBar.set_text, statusString)
        
    
    def __transferCompletedCb(self, sender = None):
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)
        self.__showCurrentDir()
        
    
    def __errorCb(self, sender, message):
        self.__statusBar.push(0, _('Error occured: ') + message)
        gobject.idle_add(self.__sendFileDialog.response, 1)
        
    
    def __onDragBegin(self, widget, dragContext):
        iter = self.__treeModel.get_iter(self.__iconView.get_selected_items()[0])
        filename = self.__treeModel.get_value(iter, 0)
        dragContext.source_window.property_change(gtk.gdk.atom_intern('XdndDirectSave0'), 'text/plain', 8, gtk.gdk.PROP_MODE_REPLACE, filename)
        
    
    def __dragDataGet(self, widget, dragContext, selectionData, info, timestamp):
        property = dragContext.source_window.property_get(gtk.gdk.atom_intern('XdndDirectSave0'), 'text/plain', pdelete = False)
        if property[0] != 'text/plain' or property[1] != 8:
            return
        
        destinationPath = urllib.unquote(urlparse.urlparse(property[2]).path)
        fileCollection = Directory()

        items = self.__iconView.get_selected_items()
        for item in items:
            iter = self.__treeModel.get_iter(item)
            name = self.__treeModel.get_value(iter, 0)
            isDir = self.__treeModel.get_value(iter, 2)
            
            directory = Directory()
            if not isDir:
                fileSize = self.__treeModel.get_value(iter, 3)
                fileCollection.addFile(File(name, fileSize))
            else:
                dir = self.__transferManager.buildDirectoryStructure(name)
                dir.parent = fileCollection
                fileCollection.addDirectory(dir)
                
        print 'dest: ' + os.path.dirname(destinationPath)
        selectionData.set('text/plain', 8, 'S')
        self.__transferFilesToLocal(fileCollection, os.path.dirname(destinationPath))
        dragContext.source_window.property_delete(gtk.gdk.atom_intern('XdndDirectSave0'))
          
    
    def __dragDataReceived(self, widget, dragContext, x, y, selectionData, info, timestamp):
        directory = Directory()
        for url in selectionData.data.split('\r\n'):
            if len(url) > 0:
                filePath = urllib.unquote(urlparse.urlparse(url).path)
                if os.path.isdir(filePath):
                    for root, dirs, files in os.walk(filePath):
                        for file in files:
                            filePath = os.path.join(root, file)
                            directory.addFile(File(filePath, os.path.getsize(filePath)))
                else:
                    directory.addFile(File(filePath, os.path.getsize(filePath)))
                
        dragContext.drop_finish(True, 0L)
        self.__transferFilesToRemote(directory)            
        
    
    def __onDrop(self, widget, dragContext, x, y, timestamp):
        dragContext.drop_reply(True, 0L)
        
        
    def __iconViewKeyReleased(self, widget, event):
        if event.type == gtk.gdk.KEY_RELEASE and event.keyval == gtk.keysyms.Delete:
            self.__deleteFile()
