import bluetooth

class BluetoothDevice:
    def __init__(self, address, port, name):
        self.address = address
        self.port = port
        self.name = name
        
    def __str__(self):
        return self.name + ' - ' + self.address + ':' + str(self.port)

class BluetoothDiscovery:
    def findSerialDevices(self):
        services = bluetooth.find_service( name = "Bluetooth Serial Port", uuid = bluetooth.SERIAL_PORT_CLASS )
        devices = []
        for service in services:
            devices.append(BluetoothDevice(service["host"], service["port"], bluetooth.lookup_name(service["host"])))
        return devices
