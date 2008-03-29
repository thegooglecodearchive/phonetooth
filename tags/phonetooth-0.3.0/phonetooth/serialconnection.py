import serial

from gettext import gettext as _

class SerialConnectionException(Exception):
    pass

class SerialConnection:
    def __init__(self, port):
        self.__port = port
        self.__serial = None
        
    
    def __del__(self):
        self.disconnect()
        
    
    def connect(self):
        if self.__serial != None: return
            
        try:
            self.__serial = serial.Serial(self.__port, 19200)
        except serial.SerialException, e:
            raise SerialConnectionException, _('Failed to connect to serial port: ') + str(e)
            
    
    def disconnect(self):
        if self.__serial != None and self.__serial.isOpen():
            self.__serial.close()
            
        self.__serial = None

    
    def send(self, data):
        self.__raiseOnNoneSerial('SerialConnection: send failed, not connected')
        self.__serial.write(data)

    
    def recv(self, size = 1, wait = False):
        self.__raiseOnNoneSerial('SerialConnection: recv failed, not connected');
        return self.__serial.read(size)
        
    
    def __raiseOnNoneSerial(self, message):
        if self.__serial == None:
            raise SerialConnectionException, message
