#! /usr/bin/env python
# -*- coding: utf-8 -*-
import usb1
from ctypes import *
import numpy as np

VID = 0x09db
PID = 0x0082

DIO_PORTA   = (0x00)
DIO_PORTB   = (0x01)
DIO_DIR_IN  = (0x01)
DIO_DIR_OUT = (0x00)

'''
OFFSET_ADJUSTMENT  = (0x1F00)   // Offset Adjustment for the A/D        0x1F00 - 0x1F4F
SE_GAIN_ADJUSTMENT = (0x1F50)   // Single Ended Gain Adjustment for A/D 0x1F50 - 0x1F5F
DE_GAIN_ADJUSTMENT = (0x1F60)   // Differential Gain Adjustment for A/D 0x1F60 - 0x1F67
CAL_PIN_VOLTAGE    = (0x1FA0)   // Calibration pin voltage 0x1FA0 - 0x1FA3
'''

# Status Bits (for 16 bit status word) 
SYNC           = 0x1  # 0 = Sync slave, 1 = Sync master
EXT_TRIG_EDGE  = 0x2  # 0 = trigger falling edge, 1 = trigger rising edge
UPDATE_MODE = 0x8000  # 1 = program memory update mode

# Gain Ranges
SE_10_00V  = (0x9)           # Single Ended 0-10.0 V
BP_20_00V  = (0x0)           # Differential +/- 20.0 V
BP_10_00V  = (0x1)           # Differential +/- 10.0 V
BP_5_00V   = (0x2)           # Differential +/- 5.00 V
BP_4_00V   = (0x3)           # Differential +/- 4.00 V
BP_2_50V   = (0x4)           # Differential +/- 2.50 V
BP_2_00V   = (0x5)           # Differential +/- 2.00 V
BP_1_25V   = (0x6)           # Differential +/- 1.25 V
BP_1_00V   = (0x7)           # Differential +/- 1.00 V
SingleEnded = 0
Differential = 1

# Option values for AInScan
AIN_EXECUTION     = 0x1  # 1 = single execution, 0 = continuous execution
AIN_TRANSFER_MODE = 0x2  # 1 = Immediate Transfer mode  0 = block transfer mode
AIN_TRIGGER       = 0x4  # 1 = Use External Trigger
AIN_DEBUG         = 0x8  # 1 = debug mode.
AIN_GAIN_QUEUE    = 0x10 # 1 = Use Channel Gain Queue, 0 = Use channnel parameters

DCONFIG           = (0x01) # Configure digital port
DIN               = (0x03) # Read digital port
DOUT              = (0x04) # Write digital port

AIN               = (0x10) # Read analog input channel
AIN_SCAN          = (0x11) # Scan analog channels
AIN_STOP          = (0x12) # Stop input scan
ALOAD_QUEUE       = (0x13) # Load the channel/gain queue

AOUT              = (0x14) # Write analog output channel
AOUT_SCAN         = (0x15) # Output values to a range of output channels
AOUT_STOP         = (0x16) # Stop output scan

CINIT             = (0x20) # Initialize counter
CIN               = (0x21) # Read Counter

MEM_READ          = (0x30) # Read Memory
MEM_WRITE         = (0x31) # Write Memory

BLINK_LED         = (0x40) # Causes LED to blink
RESET             = (0x41) # Reset USB interface
SET_TRIGGER       = (0x42) # Configure external trigger
SET_SYNC          = (0x43) # Configure sync input/output
GET_STATUS        = (0x44) # Get device status
SET_CAL           = (0x45) # Set calibaration output
GET_ALL           = (0x46) # Get all analog and digital input values

PREPARE_DOWNLOAD  = (0x50) # Prepare for program memory download
WRITE_CODE        = (0x51) # Write program memory
WRITE_SERIAL      = (0x53) # Write a new serial number to device
READ_CODE         = (0x55) # Read program memory

FS_DELAY = 1000
 
class USB1208FS(object):
	def __init__(self):
		self.handle = None
        
	def usbOpen(self): 
		self.handle = usb1.USBContext().openByVendorIDAndProductID(VID, PID, skip_on_error = True)
		if self.handle is None:
			print ("Device not found.")
			exit(1)
		print ("Device found.")
		if self.handle.getConfiguration() != 1:
			self.handle.setConfiguration(1)

		for i in range(0,4):
			if self.handle.kernelDriverActive(i):
				self.handle.detachKernelDriver(i)
			self.handle.claimInterface(i)
		return self.handle

	def usbClose(self):
		self.handle.clearHalt(usb1.ENDPOINT_IN | 1)
		self.handle.clearHalt(usb1.ENDPOINT_OUT| 2)
		self.handle.clearHalt(usb1.ENDPOINT_IN | 3)
		self.handle.clearHalt(usb1.ENDPOINT_IN | 4)
		self.handle.clearHalt(usb1.ENDPOINT_IN | 5)
		
		for i in range(0,4):
			self.handle.releaseInterface(i)
		self.handle.close()
	
	def usbReset(self):
		reportID = c_byte(RESET)
		request_type = usb1.TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x09                  
		wValue = (2 << 8) | RESET
		wIndex = 0
		self.handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 1, 5000)
        
	def usbBlink(self):
		reportID = c_byte(BLINK_LED)
		request_type = usb1.TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x09                  
		wValue = (2 << 8) | BLINK_LED
		wIndex = 0
		self.handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 1, 5000)

	# configure digital port
	def usbDConfigPort(self, port, direction):
		'''
		This command sets the direction of the DIO port to input or output. 
		 Port:      0 = Port A,  1 = Port B
		 Direction: 0 = output,  1 = input
		'''
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | DCONFIG   # HID ouptut
		wIndex = 0                    # Interface

		reportID = DCONFIG
		config_port = (c_byte*3)()
		config_port[0] = reportID
		config_port[1] = port
		config_port[2] = direction
		config_port_p = cast(config_port, POINTER(c_byte))
		self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, len(config_port), 5000)
        
	def usbDIn(self, port):
		'''
		This command writes data to the DIO port bits that are configured as outputs.
		 Port: 0 = Port A, 1 = Port B
		 Data: value to write to the port
		'''
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | DIN       # HID ouptut
		wIndex = 0                    # Interface

		reportID = c_byte(DIN)
		read_port = (c_byte*3)()
		read_port[0] = reportID
		self.handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 1, 5000)

		transferred = self.handle._interruptTransfer(usb1.ENDPOINT_IN | 1, read_port, len(read_port), FS_DELAY)
		return read_port[port+1]
        
	def usbDOut(self, port, value):
		'''
		This command writes data to the DIO port bits that are configured as outputs.
		 Port: 0 = Port A, 1 = Port B
		 Data: value to write to the port
		'''
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | DOUT      # HID ouptut
		wIndex = 0                    # Interface

		reportID = DOUT
		config_port = (c_byte*3)()
		config_port[0] = reportID
		config_port[1] = port
		config_port[2] = value
		config_port_p = cast(config_port, POINTER(c_byte))
		self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, len(config_port), 5000)
		
	def usbAOut(self, channel, value):
		'''
		This command writes the value to an analog output channel. The value
		is a 16-bit unsigned value, but the DAC is a 12-bit DAC. The lower 4
		bits of the value are ignored by the DAC. The equation for the
		output voltage is:

			V_out = ( k / 2^16 ) * V_ref 

		where k is the value written to the device and V_ref = 4.096V.

		channel: the channel to write (0 or 1)
		value:   the value to write
		'''
		value <<= 4
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | AOUT      # HID ouptut
		wIndex = 0                    # Interface 
		reportID = AOUT

		config_port = (c_byte*4)()
		config_port[0] = reportID
		config_port[1] = channel            # 0 or 1
		config_port[2] = value & 0x00ff     # low byte
		config_port[3] = value >> 8         # high byte
		config_port_p = cast(config_port, POINTER(c_byte))
		self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, len(config_port), 5000)
		
	def usbAIn(self, channel, gain):
		'''
		This command reads the value from an analog input channel,
		etting the desired gain range first.  The returned value is a
		2s-complement signed 16-bit number.
		channel: the channel to read (0-7)
		range:   the gain range (0-7)
		'''
		mode = SingleEnded

		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | AIN      # HID ouptut
		wIndex = 0                    # Interface 
		reportID = AIN

		if gain == SE_10_00V:
			mode = SingleEnded
			channel += 8
			gain = 0
		else:
			mode = Differential
			
		config_port = (c_byte*3)()
		config_port[0] = reportID
		config_port[1] = channel            
		config_port[2] = gain     
		config_port_p = cast(config_port, POINTER(c_byte))
			
		self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, 3, 5000)
		report = (c_byte*3)()
		report = self.handle.interruptRead(usb1.ENDPOINT_IN | 1, 3, FS_DELAY)
		
		value = 0
		if mode == Differential:
			value = np.int16(report[1] | (report[2] << 8))
			print(format(report[2], '02x') + format(report[1], '02x'))
			value /= (1<<4)
		else:
			uvalue = np.uint16(report[1] | (report[2] << 8))
			if uvalue > 0x7ff0:
				uvalue = 0
			elif uvalue > 0x7fe0:
				uvalue = 0xfff
			else:
				uvalue >>= 3
				uvalue &= 0xfff
			value = uvalue - 0x800
		return value
		
	def usbAIn_Scan(self, lowchannel, highchannel, count, frequency, options):
		'''
		This command scans a range of analog input channels and sends the
		  readings in interrupt transfers. The gain ranges that are
		  currently set on the desired channels will be used (these may be
		  changed with AIn or ALoadQueue.

			lowchannel:  the first channel of the scan (0 – 7)
			highchannel: the last channel of the scan (0 – 7)
			count:       the total number of samples to perform, used only in single execution mode
			options:     bit 0: 1 = single execution, 0 = continuous execution
						 bit 1: 1 = immediate transfer mode, 0 = block transfer mode
						 bit 2: 1 = use external trigger
						 bit 3: 1 = debug mode (scan returns consecutive integers instead of
									sampled data, used for checking for missed data, etc.)
						 bit 4: 1 = use channel gain queue, 0 = use channel parameters specified
						 bits 5-7: not used
			
		  The sample rate is set by the internal 16-bit incrementing timer
		  running at a base rate of 10MHz. The timer is controlled by
		  timer_prescale and timer_preload. These values are only used if the
		  device has been set to master the SYNC pin with the SetSync command.

		  The data will be returned in packets utilizing interrupt in endpoints. Two endpoints will be
		  used; each endpoint allows 64 bytes of data to be sent every millisecond, so the theoretical
		  limit is:
			  2 endpoints * 64 bytes/ms = 128 bytes/ms = 128,000 bytes/s = 64,000 samples/s

		  The data will be in the format:
		  lowchannel sample 0 : lowchannel + 1 sample 0 :… : hichannel sample 0
		  lowchannel sample 1 : lowchannel + 1 sample 1 :… : hichannel sample 1
		  .
		  .
		  .
		  lowchannel sample n : lowchannel + 1 sample n : … : hichannel sample n

		  The data will use successive endpoints, beginning with the first
		  endpoint at the start of a scan and cycling through the second
		  endpoint until reaching the specified count or an AScanStop is sent.
		  Immediate transfer mode is used for low sampling rates to avoid
		  delays in receiving the sampled data. The data will be sent at the
		  end of every timer period, rather than waiting for the buffer to
		  fill. Both endpoints will still be used in a sequential manner. This
		  mode should not be used if the aggregate sampling rate is greater
		  than 2,000 samples per second in order to avoid data loss.

		  The external trigger may be used to start data collection
		  synchronously. If the bit is set, the device will wait until the
		  appropriate trigger edge is detected, then begin sampling data at
		  the specified rate. No messages will be sent until the trigger is
		  detected.
		'''
		chan = np.zeros((8,), dtype=np.uint8)
		gains = np.zeros((8,), dtype=np.uint8)
		
		data = (c_byte*64)() # consist of 62 bytes of data and 2 bytes scan index
		arg = (c_byte*11)() 
		arg_p = cast(arg, POINTER(c_byte))
		
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | AIN_SCAN  # HID ouptut
		wIndex = 0                    # Interface
		
		if (highchannel > 7):
			print("usbAInScan_SE: highchannel out of range.")
			return None;

		if (lowchannel > 7): 
			print("usbAInScan_SE: lowchannel out of range.")
			return None
		

		if (lowchannel > highchannel): 
			print("usbAInScan_SE: lowchannel greater than highchannel")
			return None
		

		num_samples = count
		if (count%31):
			count += (31 - count%31)    # fill up entire scan line
		
		# Set the channel gain.
		arg[0] = AIN_SCAN
		arg[1] = lowchannel
		arg[2] = highchannel
		arg[3] = count & 0xff           # low byte
		arg[4] = (count >>  8) & 0xff
		arg[5] = (count >> 16) & 0xff
		arg[6] = (count >> 24) & 0xff   # high byte
		arg[7] = 0						# prescale
		arg[8] = 0						# preload low
		arg[9] = 0						# preload high
		arg[10] = options  
		
		preload = 0
		prescale = 0
		for prescale in range(0, 9):
			preload = np.uint32(10e6/((frequency) * (1<<prescale)))
			if (preload <= 0xffff):
				arg[7] = prescale & 0xff
				arg[8] =  preload & 0xff          # low byte
				arg[9] =  (preload >> 8) & 0xff   # high byte
				#frequency = 10.e6/((1<<prescale)*preload)
				break
		
		if ((arg[0] == 9) | (preload == 0)) :
			print("usbAInScan_USB1208FS_SE: frequency out of range")
			return None
		
		self.handle._controlTransfer(request_type, request, wValue, wIndex, arg_p, len(arg), 5000)

		sdata = np.zeros((num_samples,), dtype=np.int16)
		
		i = 0
		pipe = 1  # Initial Enpoint to receive data.
		
		while ( num_samples > 0 ) :
			self.handle._interruptTransfer(usb1.ENDPOINT_IN |(pipe+2), data, len(data), 1000)
			print(np.uint8(data[62]))
			if (num_samples > 31) :
				for k in range(0,31) :
					data_val = np.int16(data[2*k] | data[2*k+1] << 8)
					sdata[i+k] =  data_val/(1<<4)
					
				num_samples -= 31;
				i += 31;
				
			else :   # only copy in a partial scan
				for k in range (0, num_samples) :
					data_val = np.int16(data[2*k] | data[2*k+1] << 8)
					sdata[i+k] =  data_val/(1<<4)
				
				num_samples = 0
				break;
			
			pipe = (pipe)%3 + 1  #pipe should take the values 1, 2 or 3
		
		self.usbAIn_Stop()
		return sdata
		
	def usbAIn_Scan_SE(self, lowchannel, highchannel, count, frequency, options):
		chan = np.zeros((8,), dtype=np.uint8)
		gains = np.zeros((8,), dtype=np.uint8)
		
		data = (c_byte*64)() # consist of 62 bytes of data and 2 bytes scan index
		arg = (c_byte*11)() 
		arg_p = cast(arg, POINTER(c_byte))
		
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | AIN_SCAN  # HID ouptut
		wIndex = 0                    # Interface
		
		if (highchannel > 7):
			print("usbAInScan_SE: highchannel out of range.")
			return None;

		if (lowchannel > 7): 
			print("usbAInScan_SE: lowchannel out of range.")
			return None
		

		if (lowchannel > highchannel): 
			print("usbAInScan_SE: lowchannel greater than highchannel")
			return None
		

		num_samples = count
		if (count%31):
			count += (31 - count%31)    # fill up entire scan line
		
		# Set the channel gain.
		arg[0] = AIN_SCAN
		arg[1] = lowchannel + 8
		arg[2] = highchannel + 8
		arg[3] = count & 0xff           # low byte
		arg[4] = (count >>  8) & 0xff
		arg[5] = (count >> 16) & 0xff
		arg[6] = (count >> 24) & 0xff   # high byte
		arg[7] = 0						# prescale
		arg[8] = 0						# preload low
		arg[9] = 0						# preload high
		arg[10] = options  
		
		preload = 0
		prescale = 0
		if ((frequency > 0.596) & (frequency < 50000)) :
			for prescale in range(0, 9):
				preload = np.uint32(10e6/((frequency) * (1<<prescale)))
				if (preload <= 0xffff):
					arg[7] = prescale & 0xff
					arg[8] =  preload & 0xff          # low byte
					arg[9] =  (preload >> 8) & 0xff   # high byte
					#frequency = 10.e6/((1<<prescale)*preload)
					break
		elif (frequency == 0.0) :
			preload = 0xffff
			arg[8] = 0xff                    # low byte
			arg[9] = (preload >> 8) & 0xff   # high byte
			arg[7] = 1
		else :
			print("usbAOutScan_USB1208FS_SE: frequency out of range")
			return None
		
			
		if ((arg[0] == 9) | (preload == 0)) :
			print("usbAInScan_USB1208FS_SE: frequency out of range")
			return None
		
		# Set the gain +/-10V 
		nchan = highchannel - lowchannel + 1;
		for i in range(0, nchan):
			chan[i] = lowchannel + i
			gains[i] = SE_10_00V
		
		self.usbALoadQueue(nchan, chan, gains);		
		self.handle._controlTransfer(request_type, request, wValue, wIndex, arg_p, len(arg), 5000)

		sdata = np.zeros((num_samples,), dtype=np.uint16)
		
		i = 0
		pipe = 1  # Initial Enpoint to receive data.
		
		while ( num_samples > 0 ) :
			self.handle._interruptTransfer(usb1.ENDPOINT_IN |(pipe+2), data, len(data), 1000)
			
			if (num_samples > 31) :
				for k in range(0,32) :
					data_val = np.uint16(data[2*k] | data[2*k+1] << 8)
					if (data_val > 0x7ff0) :
						data_val = 0
					elif (data_val > 0x7fe0) :
						data_val = 0xfff
					else :
						data_val >>= 3
						data_val &= 0xfff

					sdata[i+k] =  data_val - 0x800
				num_samples -= 31;
				i += 31;
				
			else :   # only copy in a partial scan
				for k in range (0, num_samples) :
					data_val = np.uint16(data[2*k] | data[2*k+1] << 8)

					if (data_val > 0x7ff0) :
						data_val = 0
					elif (data_val > 0x7fe0) :
						data_val = 0xfff
					else :
						data_val >>= 3
						data_val &= 0xfff
					
					sdata[i+k] =  data_val - 0x800
				
				num_samples = 0
				break;
			
			pipe = (pipe)%3 + 1  #pipe should take the values 1, 2 or 3
		
		self.usbAIn_Stop()
		return sdata
		
	def usbAIn_Stop(self):
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 # HID Set_Report
		wValue = (2 << 8) | AIN_STOP  # HID ouptut
		wIndex = 0                    # Interface

		reportID = c_byte(AIN_STOP)
		self.handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 1, 5000)

	def usbALoadQueue(self, num, chan, gains):
		'''
		The device can scan analog input channels with different gain
		settings. This function provides the mechanism for configuring each
		channel with a unique range. 

		num:  the number of channel / gain pairs to follow (max 8)
		chan[]: array of the channel numbers (0 – 7)
		gain[]: array of the  gain ranges (0 – 7)
		'''
		request_type = usb1.REQUEST_TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
		request = 0x9                 		 # HID Set_Report
		wValue = (2 << 8) | ALOAD_QUEUE      # HID ouptut
		wIndex = 0                    		 # Interface
		
		if num > 8:
			num = 8

		config_port = (c_byte*18)()
		config_port[0] = ALOAD_QUEUE	# reportID
		config_port[1] = num			# number of channel/gain pairs to follow (max 8).
		
		for i in range(0,num):			# 16 more bytes are for channel-gain pair
			if gains[i] == SE_10_00V :
				config_port[2 + 2*i] = chan[i] + 8;
				config_port[2 + 2*i+1] = 0;
			else:
				config_port[2 + 2*i] = chan[i];
				config_port[2 + 2*i+1] = gains[i];
		config_port_p = cast(config_port, POINTER(c_byte))
		
		self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, len(config_port), 5000)
		

	def volts_SE(self, num):
		return (10.0 * num / 0x7ff)

	def volts_FS(self, gain, num):
		if gain == BP_20_00V:
			return 20.0 * num / 0x7ff
		elif gain == BP_10_00V:
			return 10.0 * num / 0x7ff
		elif gain == BP_5_00V:
			return 5.0 * num / 0x7ff
		elif gain == BP_4_00V:
			return 4.0 * num / 0x7ff
		elif gain == BP_2_50V:
			return 2.5 * num / 0x7ff
		elif gain == BP_2_00V:
			return 2.0 * num / 0x7ff
		elif gain == BP_1_25V:
			return 1.25 * num / 0x7ff
		elif gain == BP_1_00V:
			return 1.0 * num / 0x7ff
		else:
			return 0









        
