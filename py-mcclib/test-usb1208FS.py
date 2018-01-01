from mcc_libusb import *
import datetime
import time
import numpy as np

mcc = USB1208FS()
mcc.usbOpen()
#mcc.usbDConfigPort(DIO_PORTA, DIO_DIR_OUT)
#mcc.usbDConfigPort(DIO_PORTB, DIO_DIR_IN)
#mcc.usbDOut(DIO_PORTA, 0)
#num = mcc.usbAIn(1, BP_1_00V)
#print(str(mcc.volts_FS(BP_1_00V, num)))

#channel = np.array([1, 2, 3, 7])
#gain = np.array([SE_10_00V, BP_10_00V, BP_20_00V, BP_1_25V])
#mcc.usbALoadQueue(4, channel, gain)
#mcc.usbReset()
#mcc.usbAIn_Stop()
options = AIN_EXECUTION | AIN_GAIN_QUEUE
sdata = mcc.usbAIn_Scan_SE(0, 0, 50, 1000, options)
print(sdata)
print(mcc.volts_SE(np.average(sdata)))
#mcc.usbALoadQueue(1, np.array([1]), np.array([BP_10_00V]))
#sdata1 = mcc.usbAIn_Scan(1,1,50,1000, AIN_EXECUTION)
#print(sdata1)
#print(mcc.volts_FS(BP_10_00V, np.average(sdata1)))

mcc.usbClose()

'''
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

	i = input(">> ")
	if i == 'b': #test to see if led blinks
		mcc.usbBlink()
		
	elif i == 'e':
		mcc.close()
		exit(1)
		
	elif i == 'd':
		print("\nTesting Digital I/O....")
		print("connect pins 21 through 28 <=> 32 through 39")
		temp = int(input("Enter a byte number [0-0xff]: "))
		mcc.usbDOut(DIO_PORTA, temp)
		din = mcc.usbDIn(DIO_PORTB)
		print("The number you entered = " + hex(din & 0xff))
		
	elif i == 'i':
		print("Testing the analog input differential...")
		gain = int(input("Enter gain: "))
		channel = int(input("Enter channel [0-7]: "))
		value = mcc.usbAIn(channel, gain)
		print("Channel: " + str(channel) + ": value = " + str(value))
		
	elif i == 'h':
		print("Testing the analog input single ended...")
		#channel = input("Entner channel [0-7]: ")
		for i in range(0, 100):
			start = datetime.datetime.now()
			for j in range(0,8):
				value = mcc.usbAIn(j, SE_10_00V)
				print("Channel: %d: Value = 0x%04X, %.2fV" % (j%8 ,value, mcc.volts_SE(value)))
			delta = datetime.datetime.now() - start;
			print("%d" % (delta.microseconds))
			time.sleep(0.1)
		
	elif i == 'o': #test the analog output
		print("Testing the analog output...")
		channel = int(input("Enter channel [0-1] => (pin 13-14): "))
		value = int(input("Enter a value: "))
		mcc.usbAOut(channel, value)
		
	else:
		continue
'''
