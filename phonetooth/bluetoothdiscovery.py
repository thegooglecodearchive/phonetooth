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

import bluetooth

class BluetoothDevice:
    def __init__(self, address, port, deviceName, serviceName, obexPort=0):
        self.address = address
        self.port = port
        self.obexPort = obexPort
        self.deviceName = deviceName
        self.serviceName = serviceName
        
    def __str__(self):
        return self.name + '(' + self.serviceName + ') - ' + self.address + ':' + str(self.port)

class BluetoothDiscovery:
    def findSerialDevices(self):
        devices = bluetooth.discover_devices(duration = 5, lookup_names = False, flush_cache = True)
        
        serialDevices = []
        for address in devices:
            services = bluetooth.find_service(uuid = bluetooth.SERIAL_PORT_CLASS, address = address)
            services.extend(bluetooth.find_service(uuid = bluetooth.DIALUP_NET_CLASS))
            obexServices = bluetooth.find_service(uuid = bluetooth.OBEX_FILETRANS_CLASS, address = address)
            
            for service in services:
                obexPort = 0
                if len(obexServices) > 0:
                    obexPort = obexServices[0]['port']
                    
                serialDevices.append(BluetoothDevice(service['host'], service['port'], bluetooth.lookup_name(service['host']), service['name'], obexPort))
        
        return serialDevices
