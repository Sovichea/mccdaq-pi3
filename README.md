# Instrumentation of DAQ MCC-USB1208FS using RPi 3
The purpose of this project is to create a user interface using a RaspberryPi 3 in order to stream data from OpenDAQ. OpenDAQ data acquisition device is used to read the analog voltage from the photodiode.

## GUI Software and Programming Language consideration
The programming languages taken into cosideration in the project are C++ and Python, and the proposed GUI software is a cross-platform software development environment **Qt Creator** (https://www.qt.io/). There are two possible approaches for the GUI development with their own pros and cons:
* By default, Qt Creator uses **Qt Framework** and high level C++ for cross-platform application development which can work perfectly with RaspberryPi since it is a linux environment. However, since the official language for RPi is python, most drivers and external libraries are mostly written in python (in our case the driver for OpenDAQ is written in python). Therefore, if we select C++ we will need to spend some time converting those libaries to support Qt Creator.

* Second approach is to using **PyQt** library along with Python development environment. PyQt also uses Qt Framework discussed above, but, as can be interpreted from its name, it's a Qt library written in python. So, the idea here is to still use Qt Creator but on the GUI part. Since Qt Creator comes with a GUI designer, this can speed up the process dramatically. But this time we will use **PyQt** tool to convert the UI created in Qt Creator to a Python file and from there we will use Python 3 IDE to write the core application.

The second method is preferable, since it is aligned with our project goal and can speed up the development process for the GUI, as well as making it easy to interface with external devices such as MCCDAQ which already has its library written in python.

## Setup Minimal Raspberry Pi Development Environment
Though Rapsberry Pi is a low-cost device, setting up to be functional is not easy because it requires the connection to a PC Monitor, Keyboards and Mouse, thus it is not easy to move from place to place and start developping the software on the go. This sometimes can be annoying to beginner who just want to get the board just get started with it. Therefore, we decided to set up a minimal development environment for our project using linux remote desktop or VNC. 

By default, Raspberry Pi already comes with the VNC server installed. So, all we need to do is first connect the Rapsberry Pi to PC wire an Ethernet cable and run Putty (https://www.putty.org/).

## References
* Installing Qt Creator on RPi: http://helloraspberrypi.blogspot.fr/2016/03/install-qt5qt-creator-for-raspberry-pi.html
* RPi GUI tutorial: https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
* OpenDAQ usage in Python: http://opendaq-python.readthedocs.io/en/latest/usage.html
