import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from mcc_libusb import *

from mainwindow_ui import *
from dialog_ui import *
from roi_window_ui import *

class ROIWindow(QtGui.QWidget, Ui_Form_roi):
	closed = QtCore.Signal()
	
	def __init__(self, parent=None):
		super(ROIWindow, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
		self.setupUi(self)
		
	def closeEvent(self, event):
		#print("ROI closed")
		self.closed.emit()

class Dialog(QtGui.QDialog, Ui_Dialog):
	def __init__(self, parent=None):
		super(Dialog, self).__init__(parent)
		self.setupUi(self)
		self.checkBox.toggled.connect(self.state_toggled)
	
	def state_toggled(self):
		if self.checkBox.isChecked():
			self.pushButton_accept.setText("OK")
		else:
			self.pushButton_accept.setText("Continue")
		
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
		self.dialog = Dialog()
		self.roi = ROIWindow()
		self.show()
		
		self.color = ['r','g','b','y','m','k','c','w']
		self.selected_chan = []
		self.data = []
		self.count = 0
		self.roi_plot = None
		self.gain = SE_10_00V*np.ones(8, dtype=int)
		self.chan = np.zeros(8)
		self.mcc = USB1208FS()
		self.p = self.plotWidget		
		self.lr = pg.LinearRegionItem([0, 10])
		self.timer = QtCore.QTimer()
		
		
		self.timer.timeout.connect(self.plot_graph)
		self.dialog.accepted.connect(self.accepted)
		self.pushButton_start.clicked.connect(self.run_dialog)
		self.pushButton_stop.clicked.connect(self.stop_plot)
		self.checkBox_roi.toggled.connect(self.roi_graph)
		self.roi.closed.connect(self.update_app)
		self.lr.sigRegionChanged.connect(self.update_roi)
		
	def update_roi(self):
		self.roi.graphicView.setXRange(*self.lr.getRegion(), padding=0)
	
	def update_app(self):
		self.checkBox_roi.setChecked(False)
		self.plotWidget.removeItem(self.lr)
		
	def roi_graph(self):
		if self.checkBox_roi.isChecked():
			self.roi.show()
			self.plotWidget.addItem(self.lr)
		else:
			self.roi.close()
			self.plotWidget.removeItem(self.lr)

	def plot_graph(self):
		self.p.clear()
		for i in range(0, len(self.selected_chan)):
			value = self.mcc.usbAIn(self.selected_chan[i], self.gain[self.selected_chan[i]])
			if self.gain[self.selected_chan[i]] < SE_10_00V:
				self.data[i][self.count] = self.mcc.volts_FS(self.gain[self.selected_chan[i]], value)
			else:
				self.data[i][self.count] = self.mcc.volts_SE(value)
			self.p.plot(self.data[i][:self.count], pen=self.color[self.selected_chan[i]])
		self.count += 1
        
	def readParams(self):
		self.sample_rate = int(self.lineEdit_sample_rate.text())
		if self.tabWidget.currentIndex() == 0:
			self.gain = SE_10_00V*np.ones(8,dtype=int)
			self.chan[0] = self.checkBox_chan0.isChecked()
			self.chan[1] = self.checkBox_chan1.isChecked()
			self.chan[2] = self.checkBox_chan2.isChecked()
			self.chan[3] = self.checkBox_chan3.isChecked()
			self.chan[4] = self.checkBox_chan4.isChecked()
			self.chan[5] = self.checkBox_chan5.isChecked()
			self.chan[6] = self.checkBox_chan6.isChecked()
			self.chan[7] = self.checkBox_chan7.isChecked()
		else:
			self.gain[0] = self.comboBox_gain_1.currentIndex()
			self.gain[1] = self.comboBox_gain_2.currentIndex()
			self.gain[2] = self.comboBox_gain_3.currentIndex()
			self.gain[3] = self.comboBox_gain_4.currentIndex()
			self.gain[4] = 0
			self.gain[5] = 0
			self.gain[6] = 0
			self.gain[7] = 0
			
			self.chan[0] = self.checkBox_chan10.isChecked()
			self.chan[1] = self.checkBox_chan32.isChecked()
			self.chan[2] = self.checkBox_chan54.isChecked()
			self.chan[3] = self.checkBox_chan76.isChecked()
			self.chan[4] = 0
			self.chan[5] = 0
			self.chan[6] = 0
			self.chan[7] = 0
				
	
	def stop_plot(self):
		self.timer.stop()
		self.mcc.usbClose()
		
	def run_dialog(self):
		if len(self.data) > 0:
			self.dialog.show()
		else:
			self.selected_chan = []
			self.data = []
			self.readParams()
			for i in range(0,8):
				if self.chan[i] == 1:
					self.data.append(np.zeros(10000))
					self.selected_chan.append(i)
			self.mcc.usbOpen()
			self.timer.start(self.sample_rate)
			
	def accepted(self):
		print("accepted")
		self.readParams()
		if self.dialog.checkBox.isChecked():
			self.selected_chan = []
			self.data = []
			self.count = 0
			for i in range(0,8):
				if self.chan[i] == 1:
					self.data.append(np.zeros(10000))
					self.selected_chan.append(i)
		self.mcc.usbOpen()
		self.timer.start(self.sample_rate)

def main():
	app = QtGui.QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
    
