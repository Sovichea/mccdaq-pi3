# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'roi_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form_roi(object):
    def setupUi(self, Form_roi):
        Form_roi.setObjectName(_fromUtf8("Form_roi"))
        Form_roi.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Form_roi)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphicsView = PlotWidget(Form_roi)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout.addWidget(self.graphicsView)

        self.retranslateUi(Form_roi)
        QtCore.QMetaObject.connectSlotsByName(Form_roi)

    def retranslateUi(self, Form_roi):
        Form_roi.setWindowTitle(_translate("Form_roi", "Form", None))

from pyqtgraph import PlotWidget
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'roi_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form_roi(object):
    def setupUi(self, Form_roi):
        Form_roi.setObjectName(_fromUtf8("Form_roi"))
        Form_roi.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Form_roi)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphicsView = PlotWidget(Form_roi)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout.addWidget(self.graphicsView)

        self.retranslateUi(Form_roi)
        QtCore.QMetaObject.connectSlotsByName(Form_roi)

    def retranslateUi(self, Form_roi):
        Form_roi.setWindowTitle(_translate("Form_roi", "Form", None))

from pyqtgraph import PlotWidget
