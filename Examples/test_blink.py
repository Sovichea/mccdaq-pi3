import usb1
from ctypes import *

VID = 0x09db
PID = 0x0082
BLINK_LED = c_char_p(0x40)

with usb1.USBContext() as context:
    handle = context.openByVendorIDAndProductID(VID, PID, skip_on_error = True,)
    if handle is None:
        print ("Device not found.")
        exit(1)
    print ("Device found.")

    if handle.kernelDriverActive(0):
        handle.detachKernelDriver(0)
    handle.claimInterface(0)

    if handle.kernelDriverActive(1):
        handle.detachKernelDriver(1)
    handle.claimInterface(1)

    if handle.kernelDriverActive(2):
        handle.detachKernelDriver(2)
    handle.claimInterface(2)

    if handle.kernelDriverActive(3):
        handle.detachKernelDriver(3)
    handle.claimInterface(3)

    reportID = BLINK_LED
    request_type = usb1.TYPE_CLASS|usb1.RECIPIENT_INTERFACE|usb1.ENDPOINT_OUT
    request = 0x09                  
    wValue = (2 << 8) | 0x40
    wIndex = 0                    

    handle._controlTransfer(request_type, request, wValue, wIndex, byref(reportID), 1, 5000)

    exit(0)
