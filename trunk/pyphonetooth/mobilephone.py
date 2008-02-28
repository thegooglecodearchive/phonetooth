import socket
import bluetooth

from pyphonetooth import contacts

class BluetoothDevice:
    def __init__(self, address, port, name):
        self.address = address
        self.port = port
        self.name = name

class BluetoothDiscovery:
    def findSerialDevices(self):
        services = bluetooth.find_service( name = "Bluetooth Serial Port", uuid = bluetooth.SERIAL_PORT_CLASS )
        devices = []
        for service in services:
            devices.append(BluetoothDevice(service["host"], service["port"], bluetooth.lookup_name(service["host"])))
        return devices

class MobilePhone:
    def __init__(self, device):
        self.__sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.__sock.connect((device.address, device.port))
        
        self.__sendATCommand('ATE0\r')
        
    def __del__(self):
        self.__sock.close()
        
    def getManufacturer(self):
        return self.__sendATCommand('AT+CGMI\r')
        
    def getModel(self):
        return self.__sendATCommand('AT+CGMM\r')
        
    def getSerialNumber(self):
        return self.__sendATCommand('AT+CGSN\r')

    def getBatteryStatus(self):
        return self.__sendATCommand('AT+CBC\r')

    def getSerialNumber(self):
        return self.__sendATCommand('AT+CGSN\r')
        
    def powerOff(self):
        return self.__sendATCommand('AT+CPOF\r')
        
    def sendSMS(self, message, recipient):
        self.__sendATCommand('ATZ\r')
        self.__sendATCommand('AT+CMGF=1\r') # text mode
        
        # send message information and wait for prompt
        messageCommand = 'AT+CMGS="' + recipient + '"\r'
        self.__sock.sendall(messageCommand)
        reply = self.__sock.recv(len(messageCommand) + 4, socket.MSG_WAITALL) # read message + '\r\n> '

        if reply[-2:] == '> ':
            self.__sendATCommand(message + chr(26)) # message + CTRL+Z
        else:
            raise Exception, 'Failed to send message'
            
    def getContacts(self, location):
        if location == 'SIM':
            self.__sendATCommand('AT+CPBS="SM"\r')
        elif location == 'PHONE':
            self.__sendATCommand('AT+CPBS="ME"\r')
        else:
            raise Exception, 'Invalid contact location specified'
            
        reply = self.__sendATCommand('AT+CPBR=?\r')
        memorySlots = self.__parseMemorySlots(reply)
        reply = self.__sendATCommand('AT+CPBR=1,' + memorySlots + '\r')
        rawContacts = reply.strip().split('\r\n')
        
        contactList = []
        for contact in rawContacts:
            fields = contact.split(',')
            contactList.append(contacts.Contact(fields[3][1:-1], fields[1][1:-1]))
        
        return contactList
        
    def __sendATCommand(self, atCommand):
        self.__sock.sendall(atCommand)
         
        reply = ""
        while not (reply.endswith('OK\r\n') or reply.endswith('ERROR\r\n')):
            reply += self.__sock.recv(1024)
            
        if reply.endswith('OK\r\n'):
            end = reply.rfind('\r\nOK\r\n')
            return reply[2:end]
        else:
            raise Exception, 'AT Command: ' + atCommand[:-1] + ' not supported by phone'
            
    def __parseMemorySlots(self, reply):
        #+CPBR:(1-100),40,14,0
        begin   = reply.find('-') + 1
        end     = reply.rfind(')')
        
        return reply[begin:end]