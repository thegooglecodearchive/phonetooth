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

import phonebrowser

from gettext import gettext as _

class PhoneBrowserHandler(gobject.GObject):
    __ignoreEvents = False
    
    __gsignals__ =  {
        "disconnected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
    }
    
    def __init__(self, widgetTree, parent):
        gobject.GObject.__init__(self)
        
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
        
        iconTheme = gtk.icon_theme_get_default()
        self.__dirImage = iconTheme.load_icon('folder', 36, gtk.ICON_LOOKUP_FORCE_SVG)
        self.__fileImage = iconTheme.load_icon('misc', 36, gtk.ICON_LOOKUP_FORCE_SVG)

        self.__phoneBrowser = phonebrowser.PhoneBrowser()
        self.__phoneBrowser.connect('connected', self.__connectedCb)
        self.__phoneBrowser.connect('disconnected', self.__disconnectedCb)
        self.__phoneBrowser.connect('started', self.__transferStartedCb)
        self.__phoneBrowser.connect('progress', self.__transferProgressCb)
        self.__phoneBrowser.connect('completed', self.__transferCompletedCb)
        self.__phoneBrowser.connect('error', self.__errorCb)
        
        self.__iconView.set_model(self.__treeModel)
        
        dic = {'onIconActivated'            : self.__iconActivated,
               'onDeleteFileClicked'        : self.__deleteFile,
               'onSelectionChanged'         : self.__selectionChanged,
               'onRootButtonClicked'        : self.__naviGationButtonClick,
               'onCreateDir'                : self.__createDir
        }
        widgetTree.signal_autoconnect(dic)
        

    def __del__(self):
        self.disconnectFromPhone()
        

    def connectToPhone(self, btAddress):
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
                
                self.__transferProgressBar.set_fraction(0.0)
                self.__transferProgressBar.set_text('')
                self.__filenameLabel.set_text(os.path.basename(item))
                self.__phoneBrowser.copyToLocal(item, os.path.join(dir, item))
                
                #workaround, transferstart signal gives 0 as file size
                self.__phoneBrowser.transferInfo.overwriteSize(self.__treeModel.get_value(iter, 3))
                
                response = self.__sendFileDialog.run()
                if response == gtk.RESPONSE_CANCEL:
                    self.__phoneBrowser.cancel()
                    self.__statusBar.push(0, _('File transfer cancelled.'))
                elif response == 1:
                    self.__statusBar.push(0, _('File transfer failed') + '.')
                else:
                    self.__statusBar.push(0, _('File succesfully recieved.'))
                self.__sendFileDialog.hide()
            else:
                chooser.destroy()
            
    
    def __deleteFile(self, widget):
        items = self.__iconView.get_selected_items()
        if len(items) == 1:
            iter = self.__treeModel.iter_nth_child(None, int(items[0][0]))
            path = self.__treeModel.get_value(iter, 0)
             
            try:
                self.__phoneBrowser.deleteFile(path)
                self.__showCurrentDir()
            except:
                self.__statusBar.push(0, _('Failed to delete item'))
    
    
    def __showCurrentDir(self):
        self.__treeModel.clear()
        
        dirs, files = self.__phoneBrowser.getDirectoryListing()
        dirs.sort()
        files.sort()
        
        for dir in dirs:
            self.__treeModel.append((dir, self.__dirImage, True, 0))
        for file in files:
            self.__treeModel.append((file.name, self.__fileImage, False, file.size))
            
        self.__iconView.grab_focus()    
        
    
    def __selectionChanged(self, widget):
        self.__deleteButton.set_sensitive(len(widget.get_selected_items()) != 0)
        
        
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
        if dir != None:
            try:
                self.__phoneBrowser.createDirectory(dir)
                self.__showCurrentDir()
            except Exception, e:
                self.__statusBar.push(0, _('Create directory not allowed'))
        
    
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
    
    
    def __transferStartedCb(self, sender = None):
        gobject.idle_add(self.__transferProgressBar.set_fraction, 0.0)
        
    
    def __transferProgressCb(self, sender = None):
        gobject.idle_add(self.__transferProgressBar.set_fraction, self.__phoneBrowser.transferInfo.progress)
        statusString = str(self.__phoneBrowser.transferInfo.kbPersecond) + ' kb/s  '
        timeRemaining = self.__phoneBrowser.transferInfo.timeRemaining
        if timeRemaining != -1:
            if timeRemaining >= 60:
                statusString += '(' + str(timeRemaining / 60 + 1) + _(' minutes remaining') + ')'
            else:
                statusString += '(' + str(timeRemaining / 10 * 10 + 10) + _(' seconds remaining') + ')'
        
        gobject.idle_add(self.__transferProgressBar.set_text, statusString)
        
    
    def __transferCompletedCb(self, sender = None):
        gobject.idle_add(self.__sendFileDialog.response, gtk.RESPONSE_CLOSE)
        
    
    def __errorCb(self, sender, message):
        self.__statusBar.push(0, _('Error occured: ') + message)
