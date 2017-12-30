
from enum import Enum

class A:
    def __new__(cls):
        print ("we have ",cls)
        member = object.__new__(cls)
        return member

class B(object):
    ichBinStatisch = 1
    def __new__(cls):
        member = object.__new__(cls)
        print ("we have ",cls)
        return member

#funktion verstehe ich nicht - wenn dies vorhanden ist wird __new__ 2 mal aufgerufen - strange
class C(Enum):
    AE=1
    BE=2

    #ich denke sowas wie polymorphie - Enum muss eine Methode haben, die
    #__new__ mit zwei parametern aufruft - ist so, in der MetaKlasse zu Enum - das geht mir als laie erstmal
    # zu weit :-)
    def __new__(cls,value):  # der echte Kontruktor in cls habe ich enum 'IPCommand' und value je nach aufruf
        member = object.__new__(cls)
        member._value_ = value
        print ("We have cls ", cls, " and value ", value)
        return member

class D(B):
    def __new__(cls):
        print("new of cls")
        return object.__new__(cls)

print("B: ", B.ichBinStatisch)