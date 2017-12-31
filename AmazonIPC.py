#c lass to connect to the amazon avs, means connect to the java programm
# provide in the sample app

from enum import Enum
import socket
import sys
import time

class IPCommand(Enum): # vererbung - Enum also Basisklasse
    DISCONNECT              = 1 # OUTGOING : Ask the AVS client to disconnect from us
    WAKE_WORD_DETECTED      = 2 # OUTGOING : sent to AVS client when a wake word is detect
    PAUSE_WAKE_WORD_ENGINE  = 3 # INCOMING : request to pause the engine and yield the Mic
    RESUME_WAKE_WORD_ENGINE = 4 # INCOMING : request to resume the engine
    CONFIRM                 = 5 # OUTGOING : sent to AVS client to confirm the engine has stopped
    UNKNOWN                 = 6 # n/a : for error & default cases
    # nach senden der 2 schalte die wake word detection aus und warte so lange bis die
    # 3 irgendwann kommt

    # in der Meta-Klasse von enum wird die Methode __new__ mit zwei Argumenten aufgerufen
    def __new__(cls,value): # der echte Kontruktor in cls habe ich enum 'IPCommand' und value je nach aufruf
        member = object.__new__(cls)
        member._value_ = value
        #print ("We have cls ", cls, " and value ", value)
        return member
    def __int__(self):
        return self._value_



class IPCConnection:
    def __init__(self,port = 5123):
        self.connected   = False
        self.port        = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def __del__(self):
        self.sendCommand(IPCommand.DISCONNECT)
        self.sock.close();

    def connect(self):
        if not self.connected:
            try:
                print ("Try to connect")
                self.sock.connect(('localhost',self.port))
                self.connected = True
            except:
                print("Can't connect to socket:", sys.exc_info()[0])
        else:
            print("connected, nothing to do")

    def sendCommand(self,command):
        if not self.connected:
            print("We have no connection")
        else:
            bytes = int(command).to_bytes(4,byteorder='big') # big bei einem Byte :-)
            #in's knie geschossen, der java-server erwartet 4 bytes big getestet, big geht
            print("send byte ",bytes)
            self.sock.sendall(bytes)
            # send 1 Byte - htonl etc duerfte egal sein ?

    def receiveUntilDone(self):
        if not self.connected:
            print("We have no connection")
        else: #da er 4 bytes annimmt, sendet er auch 4? nein, unklar, lese byte weise habe auch 0 0 4 0 zurueck bekommen :(
            received = bytearray(1)
            result = 0;
            while result != int(IPCommand.RESUME_WAKE_WORD_ENGINE):
                result = 0
                anzahl = self.sock.recv_into(received)
                #for b in received:
                #    result = result * 256 + int(b)
                result=int.from_bytes([received[0]],byteorder='big')
                print ("received ",anzahl," bytes: ", received, " Integer: ", result)


if __name__ == '__main__':
    conn = IPCConnection()
    conn.sendCommand(IPCommand.WAKE_WORD_DETECTED)
    conn.receiveUntilDone();

    #conn.sendCommand(IPCommand.DISCONNECT)
    #print ("discon: ", IPCommand.DISCONNECT)
    #print ("confirm: ", IPCommand.CONFIRM)
