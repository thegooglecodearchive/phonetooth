import bluetooth
import socket

from gettext import gettext as _

class BluetoothConnectionException(Exception):
    pass

class BluetoothConnection:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.__sock = None
        
    
    def __del__(self):
        self.disconnect()

    
    def connect(self):
        if self.__sock != None: return
            
        try:
            self.__sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.__sock.connect((self.address, self.port))
        except bluetooth.BluetoothError, e:
            raise BluetoothConnectionException, _('Failed to connect to device: ') + str(e)
            
    
    def disconnect(self):
        if self.__sock != None: 
            self.__sock.close()
        self.__sock = None

    
    def send(self, data):
        self.__raiseOnNoneSocket('BluetoothConnection: send failed, not connected')
        self.__sock.sendall(data)

    
    def recv(self, size = 1024, wait = False):
        self.__raiseOnNoneSocket('BluetoothConnection: recv failed, not connected');
        return self.__sock.recv(size, socket.MSG_WAITALL if wait == True else 0)
        
    
    def __raiseOnNoneSocket(self, message):
        if self.__sock == None:
            raise BluetoothConnectionException, message
