import usb1
from ctypes import *

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

FS_DELAY = 200
 
class USB1208FS(object):
    def __init__(self):
        self.handle = None
        
    def open(self): 
        self.handle = usb1.USBContext().openByVendorIDAndProductID(VID, PID, skip_on_error = True)
        if self.handle is None:
            print ("Device not found.")
            exit(1)
        print ("Device found.")
        if self.handle.getConfiguration() != 1:
            self.handle.setConfiguration(1)
        
        for i in range(0,3):
            if self.handle.kernelDriverActive(i):
                self.handle.detachKernelDriver(i)
            self.handle.claimInterface(i)

    def close(self):
        self.handle.clearHalt(usb1.ENDPOINT_IN | 1);
	self.handle.clearHalt(usb1.ENDPOINT_OUT| 2);
	self.handle.clearHalt(usb1.ENDPOINT_IN | 3);
	self.handle.clearHalt(usb1.ENDPOINT_IN | 4);
	
        for i in range(0,3):
            self.handle.releaseInterface(i)
        self.handle.close()
        
        
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
        self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, 3, 5000)
        
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
        #read_port = create_string_buffer(3)
        read_port[0] = reportID
        read_port_p = cast(read_port, POINTER(c_byte))
        self.handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 3, 5000)
        
        transferred = self.handle._interruptTransfer(usb1.ENDPOINT_IN | 1, read_port, 3, FS_DELAY)
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
        self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, 3, 5000)

		
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
	self.handle._controlTransfer(request_type, request, wValue, wIndex, config_port_p, 4, 5000)

	
    def volts_SE(self, num):
        return 10.0 * num / 0x7ff

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









        
