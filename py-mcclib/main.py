from mcc_libusb import *

mcc = USB1208FS()
mcc.open()
mcc.usbDConfigPort(DIO_PORTA, DIO_DIR_OUT)
mcc.usbDConfigPort(DIO_PORTB, DIO_DIR_IN)
mcc.usbDOut(DIO_PORTA, 0)

while 1:
    print("\nUSB 1208FS Testing")
    print("----------------")
    print("Hit 'b' to blink LED")
    print("Hit 'c' to test counter")
    print("Hit 'e' to exit")
    print("Hit 'd' to test digital I/O");
    print("Hit 'g' to test analog input scan (differential).")
    print("Hit 'j' to test analog input scan (single ended).")
    print("Hit 'i' to test analog input (differential mode)")
    print("Hit 'h' to test analog input (single ended)")
    print("Hit 'o' to test analog output")
    print("Hit 'O' to test analog output scan")  
    print("Hit 'r' to reset")
    print("Hit 'S' to get status")
    print("Hit 's' to get serial number")
        
    i = raw_input(">> ")
    if i == 'b': #test to see if led blinks
        mcc.usbBlink()
    elif i == 'e':
        mcc.close()
        exit(1)
    elif i == 'd':
        print("\nTesting Digital I/O....")
        print("connect pins 21 through 28 <=> 32 through 39")
        temp = input("Enter a byte number [0-0xff]: ")
        mcc.usbDOut(DIO_PORTA, temp)
        din = mcc.usbDIn(DIO_PORTB)
        print("The number you entered = " + hex(din & 0xff))
    elif i == 'o': #test the analog output
        print("Testing the analog output...")
        channel = input("Enter channel [0-1] => (pin 13-14): ")
        value = input("Enter a value: ")
        mcc.usbAOut(channel, value)
    else:
        continue
