import serial

ard = serial.Serial('com3' ,9600)

while True:
    s = input()
    c=s.encode()
    if not ard.isOpen():
        ard.open()
    ard.write(c)
