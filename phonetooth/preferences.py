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
import bluetoothdiscovery
import ConfigParser

from gettext import gettext as _

class Preferences:
    def __init__(self, preferenceFile = None):
        self.__preferenceFile = preferenceFile
        self.connectionMethod = 'bluetooth'
        self.btDevice = None
        self.customDevice = ''
        self.gammuIndex = 0
        

    def save(self):
        config = ConfigParser.ConfigParser()
        config.add_section('preferences')
        config.set('preferences', 'connectionMethod', self.connectionMethod)
        config.set('preferences', 'customDevice', self.customDevice)
        config.set('preferences', 'gammuIndex', str(self.gammuIndex))
        
        if self.btDevice != None:
            config.set('preferences', 'address', self.btDevice.address)
            config.set('preferences', 'port', str(self.btDevice.port))
            config.set('preferences', 'deviceName', self.btDevice.deviceName)
            config.set('preferences', 'serviceName', self.btDevice.serviceName)
        
        if self.__preferenceFile == None:
            self.__preferenceFile = self.__getPreferenceLocation()
        
        f = open(self.__preferenceFile, 'w')
        config.write(f)
        f.close()
        
    
    def load(self):
        if self.__preferenceFile == None:
            self.__preferenceFile = self.__getPreferenceLocation()
            
        config = ConfigParser.ConfigParser()
        openedFiles = config.read(self.__preferenceFile)
            
        if len(openedFiles) == 0:
            return
                
        try:
            self.btDevice = bluetoothdiscovery.BluetoothDevice(
                config.get('preferences', 'address'),
                int(config.get('preferences', 'port')),
                config.get('preferences', 'deviceName'),
                config.get('preferences', 'serviceName'))
        except:
            self.btDevice == None
                
        try: self.connectionMethod = config.get('preferences', 'connectionMethod')
        except: pass
        try: self.customDevice = config.get('preferences', 'customDevice')
        except: pass
        try: self.gammuIndex = int(config.get('preferences', 'gammuIndex'))
        except: pass
            

    def __getPreferenceLocation(self):
        configDir = os.path.join(os.path.expanduser('~'), '.config/phonetooth')
        
        if not os.path.isdir(configDir):
            os.makedirs(configDir)
            
        return os.path.join(configDir, 'config')
