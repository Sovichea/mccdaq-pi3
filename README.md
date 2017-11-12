# Instrumentation of OpenDAQ using RPi 3
The purpose of this project is to create a user interface in RaspberryPi 3 in order to stream the data from OpenDAQ. OpenDAQ data acquisition device used to read the analog voltage from the photodiode.

## 1. GUI Software and Programming Language consideration
The programming languages taken into cosideration in the project is C++ and Python and the proposed GUI software is one of the cross-platform software development environment **Qt Creator** (https://www.qt.io/). There are two possible approaches for the GUI development with their own pros and cons:
* By default, Qt Creator use **Qt Framework** and high level C++ for cross-platform application development which can work perfectly with RaspberryPi since it is a linux environment. However, since the official language for RPi is python, most drivers and external library are mostly written in python (in our case the driver for OpenDAQ is written in python). Therefore, if we select C++ we will need to spend some time to convert those libaries to support Qt Creator.

* Second approach is to using **PyQt** library along with Python 3 development environment. PyQt also use Qt Framework discussed above but, as can be interpreted from its name, is Qt library written in Python language. So the idea here is to still use Qt Creator but on the the GUI part. Since Qt Creator comes with a GUI designer, this can speeds up the process dramatically. But this time we will use **PyQt** tool to convert the UI created in Qt Creator to a Python 3 file and from there we will use Python 3 IDE to write the core application.

The second method is preferable, since it align with our project goal and can speed up the development process for the GUI, as well as making it easy to interface with external devices such as OpenDAQ which already has its library written in python.

## 2. OpenDAQ Interface
