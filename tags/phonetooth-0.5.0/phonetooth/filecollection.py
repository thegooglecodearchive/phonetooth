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

class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        
    
    def  __lt__(self, other):
        return self.name.lower() < other.name.lower()
    

class Directory:
    def __init__(self, name = ''):
        self.name = name
        self.files = []
        self.directories = []
        self.parent = None
    
    def addFile(self, file):
        self.files.append(file)
    

    def addDirectory(self, fileCollection):
        self.directories.append(fileCollection)
        

    def getSize(self):
        totalSize = 0
        
        for file in self.files:
            totalSize += file.size
            
        for dir in self.directories:
            totalSize += dir.getSize()
            
        return totalSize
