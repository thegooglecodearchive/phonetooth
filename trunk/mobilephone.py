import socket
import bluetooth
import contacts

class BluetoothDevice:
    def __init__(self, address, port, serviceName):
        self.serviceName = serviceName
        self.address = address
        self.port = port

class BluetoothDiscovery:
    def findSerialDevices(self):
        services = bluetooth.find_service( name = "Bluetooth Serial Port", uuid = bluetooth.SERIAL_PORT_CLASS )
        
        devices = []
        for service in services:
            devices.append(BluetoothDevice(service["host"], service["port"], service["name"]))
        return devices
        
class MobilePhone:
    def __init__(self, device):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((device.address, device.port))
        
    def __del__(self):
        self.sock.close()
        
    def getManufacturer(self):
        return self.__sendAndParseATCommand('AT+CGMI\r')
        
    def getModel(self):
        return self.__sendAndParseATCommand('AT+CGMM\r')

    def getBatteryStatus(self):
        return self.__sendAndParseATCommand('AT+CBC\r')

    def getSerialNumber(self):
        return self.__sendAndParseATCommand('AT+CGSN\r')
        
    def powerOff(self):
        return self.__sendAndParseATCommand('AT+CPOF\r')
        
    def sendSMS(self, message, recipient):
        self.__sendAndParseATCommand('ATZ\r')
        self.__sendAndParseATCommand('AT+CMGF=1\r') # text mode
        
        # send message information and wait for prompt
        messageCommand = 'AT+CMGS="' + recipient + '"\r'
        self.sock.sendall(messageCommand)
        reply = self.sock.recv(len(messageCommand) + 4, socket.MSG_WAITALL) # read message + '\r\n> '

        if reply[-2:] == '> ':
            self.__sendAndParseATCommand(message + chr(26)) # message + CTRL+Z
        else:
            raise Exception, 'Failed to send message'
            
    def getContacts(self):
        self.__sendAndParseATCommand('AT+CPBS="ME"\r')
        reply = self.__sendATCommand('AT+CPBR=?\r')
        reply = self.__sendATCommand('AT+CPBR=1,1000\r')
        rawContacts = reply.strip().split('\r\n')
        
        if rawContacts[-1] != 'OK':
            raise Exception, 'Failed to get contact list'
            
        contactList = []
        rawContacts = rawContacts[1:-1] # remove at command response
        for contact in rawContacts:
            fields = contact.split(',')
            contactList.append(contacts.Contact(fields[3][1:-1], fields[1][1:-1]))
        
        return contactList
        
    def __sendAndParseATCommand(self, atCommand):
        self.sock.sendall(atCommand)
        reply = self.__sendATCommand(atCommand)
 
        while not (reply.endswith('OK\r\n') or reply.endswith('ERROR\r\n')):
            reply += self.sock.recv(1024)
            
        if reply.endswith('OK\r\n'):
            begin = reply.find('\r\r\n')
            end = reply.rfind('\r\r\n')
            
            return reply[begin+3:end]
        else:
            raise Exception, 'AT Command: ' + atCommand[:-1] + ' not supported by phone'
            
    def __sendATCommand(self, atCommand):
        self.sock.sendall(atCommand)
        reply = ""
        while not (reply.endswith('OK\r\n') or reply.endswith('ERROR\r\n')):
            reply += self.sock.recv(1024)
            
        return reply
