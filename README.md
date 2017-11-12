# Instrumentation of OpenDAQ using RPi 3
The purpose of this project is to create a user interface using a RaspberryPi 3 in order to stream data from OpenDAQ. OpenDAQ data acquisition device is used to read the analog voltage from the photodiode.

## 1. GUI Software and Programming Language consideration
The programming languages taken into cosideration in the project are C++ and Python, and the proposed GUI software is a cross-platform software development environment **Qt Creator** (https://www.qt.io/). There are two possible approaches for the GUI development with their own pros and cons:
* By default, Qt Creator uses **Qt Framework** and high level C++ for cross-platform application development which can work perfectly with RaspberryPi since it is a linux environment. However, since the official language for RPi is python, most drivers and external libraries are mostly written in python (in our case the driver for OpenDAQ is written in python). Therefore, if we select C++ we will need to spend some time convertinf those libaries to support Qt Creator.

* Second approach is to using **PyQt** library along with Python 3 development environment. PyQt also uses Qt Framework discussed above, but, as can be interpreted from its name, it's a Qt library written in python. So, the idea here is to still use Qt Creator but on the GUI part. Since Qt Creator comes with a GUI designer, this can speed up the process dramatically. But this time we will use **PyQt** tool to convert the UI created in Qt Creator to a Python 3 file and from there we will use Python 3 IDE to write the core application.

The second method is preferable, since it is aligned with our project goal and can speed up the development process for the GUI, as well as making it easy to interface with external devices such as OpenDAQ which already has its library written in python.

## 2. OpenDAQ Interface

## References
* Installing Qt Creator on RPi: http://helloraspberrypi.blogspot.fr/2016/03/install-qt5qt-creator-for-raspberry-pi.html
* RPi GUI tutorial: https://www.baldengineer.com/raspberry-pi-gui-tutorial.html
* OpenDAQ usage in Python: http://opendaq-python.readthedocs.io/en/latest/usage.html
