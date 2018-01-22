# Directory Tree and Description
```
mccdaq-pi3
|   Goals_Timeline
|   Interface Requirements
|   README.md
|   
+---daq-gui (This folder contains all the files used to run and modify the program)
|   |   dialog.ui
|   |   dialog_ui.py
|   |   gui_image_1.PNG
|   |   gui_image_2.PNG
|   |   main.py
|   |   mainwindow.ui
|   |   mainwindow_ui.py
|   |   mcc_libusb.py
|   |   Readme.md
|   |   roi_window.ui
|   \   roi_window_ui.py   
|           
+---Examples (An example for the communication protocol between python and MCC-USB1208FS through libusb library)
|   |   Readme.md
|   \   test_blink.py
|       
+---images
|       
\---py-mcclib (A custom library, developped in Python, used to communicate with MCC-USB120FS)
    |   61-mcc.rules
    |   mcc_libusb.py
    |   Readme.md
    \   test-usb1208FS.py
        
```

**Remark:** The above library is developped in Python with the reference to C library developped by Measurement Computing (https://github.com/Sovichea/Linux_Drivers). More detail to how the library is developped and what method is used, can be found in this Wiki: https://github.com/Sovichea/mccdaq-pi3/wiki

# Instrumentation of DAQ MCC-USB1208FS using RPi 3
The purpose of this project is to create a user interface using a RaspberryPi 3 in order to stream data from OpenDAQ. OpenDAQ data acquisition device is used to read the analog voltage from the photodiode.

## GUI Software and Programming Language consideration
The programming languages taken into cosideration in the project are C++ and Python, and the proposed GUI software is a cross-platform software development environment **Qt Creator** (https://www.qt.io/). There are two possible approaches for the GUI development with their own pros and cons:
* By default, Qt Creator uses **Qt Framework** and high level C++ for cross-platform application development which can work perfectly with RaspberryPi since it is a linux environment. However, since the official language for RPi is python, most drivers and external libraries are mostly written in python (in our case the driver for OpenDAQ is written in python). Therefore, if we select C++ we will need to spend some time converting those libaries to support Qt Creator.

* Second approach is to using **PyQt** library along with Python development environment. PyQt also uses Qt Framework discussed above, but, as can be interpreted from its name, it's a Qt library written in python. So, the idea here is to still use Qt Creator but on the GUI part. Since Qt Creator comes with a GUI designer, this can speed up the process dramatically. But this time we will use **PyQt** tool to convert the UI created in Qt Creator to a Python file and from there we will use Python 3 IDE to write the core application.

The second method is preferable, since it is aligned with our project goal and can speed up the development process for the GUI, as well as making it easy to interface with external devices such as MCCDAQ which already has its library written in python.

## Setup Minimal Raspberry Pi Development Environment on Windows
Though Rapsberry Pi is a low-cost device, setting up to be functional is not easy because it requires the connection to a PC Monitor, Keyboards and Mouse, thus it is not easy to move from place to place and start developping the software on the go. This sometimes can be annoying to beginner who just want to get the board just get started with it. Therefore, we decided to set up a minimal development environment for our project using linux remote desktop or VNC. 

By default, Raspberry Pi should comes with the VNC server installed. To make sure that you have the VNC installed on the Raspberry Pi, always flash the latest raspbian image from https://www.raspberrypi.org/downloads/raspbian/. All we need to do now is first connect the Rapsberry Pi to PC wire an Ethernet cable, run Putty (https://www.putty.org/) and use the IP Address (raspberypi.local) shown in the picture below. Then click open.

![putty](https://github.com/Sovichea/mccdaq-pi3/blob/master/images/putty.PNG)

You should be able to enter the SSH screen as shown below.

**![image_here]**

In case you get an error saying unable to connect, it indicates that SSH was not enable on your Raspberry Pi. The quickest way to enable SSH feature is to plug the Raspberry Pi SD Card to your PC and create an empty file on the root folder called "ssh" without extension, then boot your Raspberry Pi again. This time it should work.

**Note:** Some PC may not recognize the IP name *"raspberrypi.local"*; therefore, you need to manually find the IP Address from Windows command prompt and type 
```
ipconfig
```
Then search for Raspberry Pi IP Address in the Ethernet Adpater section.


Next we login to Raspberry Pi using default logins: *"pi"* for the username and *"raspberry"* for the password. You should be able to see the terminal shown below:

**![image_here]**

Next, to start VNC server, we type in the command

```
sudo raspi-config
```

Then select *Interfacing Option*, *Enable VNC*. Then restart the Rapsberry Pi and close Putty.

Finally, you need to install and run Real VNC Viewer (https://www.realvnc.com/en/connect/download/viewer/windows/). You might to sign up to get the free version. Once the Viewer is opened, type in the same IP as in Putty and press Enter.

![vnc_viewer](https://github.com/Sovichea/mccdaq-pi3/blob/master/images/vnc_viewer.PNG)

You should now able to see to your Raspberry Pi desktop by using the same login as above.

## Setup PyQt Development Environment
Before setting up the environment, you should make sure that the Raspberry Pi runs with the latest update. So, first connect Raspberry Pi to the internet. If you are using Rapsberry Pi 3+, you can connect to the internet through WiFi, but for the lower version, you can only use the USB tethering due to Ethernet port is being used to handle remote desktop. 

Once connected to the internet, open the terminal window and type in the command:
```
sudo apt-get update
sudo apt-get upgrade
```
This should take some times depending on your internet connection and how many software you had on the Raspberry Pi. After the update is complete type in
```
sudo apt-get install python3-pyqt4 python3-pyqtgraph libusb-1.0-0
sudo pip3 libusb1
```
After this, go to `mccdaq-pi3/py-mcclib` and run the following command:
```
sudo cp 61-mcc.rules /etc/udev/rules.d/99-mcc.rules
```
This modify the rule for the USB so that our software can be access the USB port without root permission. This is the minimum setup that you need in order to run the GUI in this project. To run the program, go to `mccdaq-pi3/daq-gui/` folder and type 
```
python3 main.py
```

Next, if you want to install a complete development enviroment install the following package:
```
sudo apt-get install qtcreator qt4-default pyqt4-dev-tools
```
After this, you're ready to develop your own GUI to communicate with DAQ MCC-USB1208FS or other variants with some modification. You can follow the complete guide through the Wiki in this Github https://github.com/Sovichea/mccdaq-pi3/wiki.

**Quick tip:** While using VNC Viewer, you can quickly transfer files between Windows PC and Raspberry Pi using any FTP Client. In our case, we use FileZilla and fill in the same logins as above.

![filezilla](https://github.com/Sovichea/mccdaq-pi3/blob/master/images/filezilla.PNG)

## References
* Installing Qt Creator on RPi: http://helloraspberrypi.blogspot.fr/2016/03/install-qt5qt-creator-for-raspberry-pi.html
* RPi GUI tutorial: https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
* OpenDAQ usage in Python: http://opendaq-python.readthedocs.io/en/latest/usage.html
