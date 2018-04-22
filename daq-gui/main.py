import sys
import csv
import os
import time
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
		
		# maximum data points, equivalent to ~278 hrs with sampling time of 1s
		# or 27.8 hrs at 100ms sampling rate
		self.num_sample = 1000000 # increase this value if needed
		
		# Set initial Enable states for start and stop buttons:
		self.pushButton_stop.setEnabled(False)	
		self.pushButton_start.setEnabled(True)
		# Set initial Enable states for axis modifiers:
		self.pushButton_Save_Data.setEnabled(False)
		self.radioButton_Fit_Plot.setEnabled(False)
		self.radioButton_Time_Interval.setEnabled(False)
		self.lineEdit_Time_Interval.setEnabled(False)
		self.label_20.setEnabled(False)
		self.radioButton_Fit_Plot.setChecked(True)
		
		self.color = ['r','g','b','y','m','k','c','w'] # Set colors for different channel traces
		self.selected_chan = [] # initialize empty selected channel array
		self.data = [] # initialize empty data array
		self.time_data = [] # initialize empty time array
		self.count = 0 # initialize sample count
		self.gain = SE_10_00V*np.ones(8, dtype=int) 
		self.chan = np.zeros(8)
		self.mcc = USB1208FS()
		self.p = self.plotWidget
		self.p.setLabel('left', 'Voltage', 'V'); # Label y-axis
		self.p.setLabel('bottom', 'Number of Sample'); # Label x-axis	
		self.lr = pg.LinearRegionItem([0, 10])
		self.timer = QtCore.QTimer()
		self.roi.graphicsView.setLabel('left', 'Voltage', 'V'); # Label ROI y-axis
		self.roi.graphicsView.setLabel('bottom', 'Sampling Time', 's');	# Label ROI x-axis
		self.p.showGrid(1,1,1) # Enable graph grid with opacity 1
		self.roi.graphicsView.showGrid(1,1,1) # Enable ROI grid with opacity 1
		
		# Widget function assignments:
		self.timer.timeout.connect(self.plot_graph)
		self.dialog.accepted.connect(self.accepted)
		self.pushButton_start.clicked.connect(self.run_dialog)
		self.pushButton_stop.clicked.connect(self.stop_plot)
		self.checkBox_roi.toggled.connect(self.roi_graph)
		self.roi.closed.connect(self.update_app)
		self.lr.sigRegionChanged.connect(self.update_roi)
		self.lineEdit_tmin.returnPressed.connect(self.edit_xmin)
		self.lineEdit_tmax.returnPressed.connect(self.edit_xmax)
		self.lineEdit_ymin.returnPressed.connect(self.edit_ymin)
		self.lineEdit_ymax.returnPressed.connect(self.edit_ymax)
		self.pushButton_fitplot.clicked.connect(self.fit_plot)
		self.lineEdit_sample_rate.textChanged.connect(self.start_enable)
		self.pushButton_Save_Data.clicked.connect(self.save_data)

	def save_data(self): # Save data in a csv file with a 5 decimal point precision
		date_time = str(np.datetime64('now')) # Get current date and time (systme clock)
		# If current date directory exists, save there, else, save in Save_data folder:
		if os.path.exists('/home/pi/Desktop/Saved_data/' + date_time[2:10]):
			filename = '/home/pi/Desktop/Saved_data/' + date_time[2:10] +'/' + date_time + '.csv'
		else:
			filename = '/home/pi/Desktop/Saved_data/' + date_time + '.csv'
		# only channel 0 data is saved
		np.savetxt(filename, np.c_[self.data[0][0:self.count],self.time_data[0][0:self.count]], header="Voltage (V),Time (s)", fmt = '%1.5f' , delimiter=" , ") # Save the data
		self.pushButton_Save_Data.setEnabled(False) # Disable button till more datais acquired
		
	def start_enable(self): # Disables start button until a sampling rate is entered
		if self.lineEdit_sample_rate.text() == '':
			self.pushButton_start.setEnabled(False)
		else:
			self.pushButton_start.setEnabled(True)		
			
	def edit_xmin(self): # Edit x min (activates when enter is pressed)
		xy_range = self.p.viewRange() # get current xy  limits
		self.p.setXRange(float(self.lineEdit_tmin.text()),xy_range[0][1], padding=0)		
	
	def edit_xmax(self): # Edit x max (activates when enter is pressed)
		xy_range = self.p.viewRange() # get current xy limits
		self.p.setXRange(xy_range[0][0],float(self.lineEdit_tmax.text()), padding=0)
		
	def edit_ymin(self): # Edit y min (activates when enter is pressed)
		xy_range = self.p.viewRange() # get current xy limits	
		self.p.setYRange(float(self.lineEdit_ymin.text()), xy_range[1][1], padding=0)
	
	def edit_ymax(self): # Edit y max (activates when enter is pressed)
		xy_range = self.p.viewRange() # get current xy limits	
		self.p.setYRange(xy_range[1][0],float(self.lineEdit_ymax.text()), padding=0)
		
	def fit_plot(self): # Auto-ranges the plot (activated on pushbutton press)
		self.p.autoRange()
		
	def update_roi(self): # Update region of interest graph
		# set xmin and xmax limits to avoid reading erroneous data:
		self.roi.graphicsView.setLimits(xMin = 0)
		self.roi.graphicsView.setLimits(xMax = self.time_data[0][self.count])
		x_min = np.int_(np.floor(self.lr.lines[1].value())) # set xmin value to selected left limit
		x_max = np.int_(np.ceil(self.lr.lines[0].value())) # set xmax value to selected left limit
		self.roi.graphicsView.clear() # clear graph to avoid superposition of data
		for i in range(0, len(self.selected_chan)): # plot all channels
			self.roi.graphicsView.plot(self.time_data[0][x_min:x_max],self.data[i][x_min:x_max], pen=self.color[self.selected_chan[i]]) # plot data vs time
		
	def update_app(self):
		self.checkBox_roi.setChecked(False)
		self.plotWidget.removeItem(self.lr)
		
	def roi_graph(self): # Open/close Region of interest window and create/remove plot
		if self.checkBox_roi.isChecked():
			self.roi.show()
			self.plotWidget.addItem(self.lr)
		else:
			self.roi.close()
			self.plotWidget.removeItem(self.lr)

	def plot_graph(self): # Plot data on main graph
		self.p.clear() # clear plot to avoid superposing data
		
		# Plot data:
		for i in range(0, len(self.selected_chan)): # plot all channels
			value = self.mcc.usbAIn(self.selected_chan[i], self.gain[self.selected_chan[i]]) # get current data
			if self.gain[self.selected_chan[i]] < SE_10_00V:
				self.data[i][self.count] = self.mcc.volts_FS(self.gain[self.selected_chan[i]], value)
			else:
				self.data[i][self.count] = self.mcc.volts_SE(value)
			self.p.plot(self.data[i][:self.count], pen=self.color[self.selected_chan[i]])
		self.count += 1 # increment samples 
		time_now = time.clock() # current time in seconds
		self.time_elapsed = (time_now - self.time_start) # time elapsed since start button pressed
		self.time_data[0][self.count] = (self.time_elapsed) # store time at which each sample is taken
		
		# Set interval while collecting data:
		if self.radioButton_Fit_Plot.isChecked(): # Fit plot
			self.p.autoRange()
		elif self.radioButton_Time_Interval.isChecked(): # Follow an interval
			if len(self.lineEdit_Time_Interval.text())>0: # Activate only if interval is inputted
				t_interval = int(self.lineEdit_Time_Interval.text())
				xy_range = self.p.viewRange()	
				if t_interval <= xy_range[0][1]: # Starts moving the graph if the interval is less than the max saples collected
					self.p.setXRange(self.count-t_interval,self.count, padding=0)
					for i in range(0, len(self.selected_chan)): # re-sizes y axis to fit data
						if i > 0: # check min and max values of all channels
							ymin_new = min(self.data[i][self.count-t_interval:self.count])
							ymax_new = max(self.data[i][self.count-t_interval:self.count])
							if ymin_new < ymin:
								ymin = ymin_new
							if ymax_new > ymax:
								ymax = ymax_new
						else:
							ymin = min(self.data[0][self.count-t_interval:self.count])
							ymax = max(self.data[0][self.count-t_interval:self.count])
					self.p.setYRange(ymin, ymax, padding = 0)		
				else:
					self.p.autoRange()
			else:
				self.p.autoRange()
        
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
	
	def data_run(self):
			# Enable Stop button
			self.pushButton_stop.setEnabled(True)	
			# Disable interval manipulation while data is running:
			self.pushButton_fitplot.setEnabled(False)
			self.pushButton_Save_Data.setEnabled(False)
			self.comboBox_time.setEnabled(False)
			self.comboBox_y.setEnabled(False)
			self.lineEdit_tmin.setEnabled(False)
			self.lineEdit_tmax.setEnabled(False)
			self.lineEdit_ymin.setEnabled(False)
			self.lineEdit_ymax.setEnabled(False)
			self.radioButton_Fit_Plot.setEnabled(True)
			self.radioButton_Time_Interval.setEnabled(True)
			self.lineEdit_Time_Interval.setEnabled(True)
			self.label_20.setEnabled(True)
			self.label_3.setEnabled(False)
			self.label_4.setEnabled(False)
			self.label_5.setEnabled(False)
			self.label_6.setEnabled(False)
			# Disable Region of Interest while data is running:
			self.checkBox_roi.setEnabled(False)
			self.checkBox_roi.setChecked(False)
	
	def data_stop(self):
		# Disable Stop button
		self.pushButton_stop.setEnabled(False)
		# Enable interval manipulation while data is running:
		self.pushButton_fitplot.setEnabled(True)
		self.pushButton_Save_Data.setEnabled(True)
		self.comboBox_time.setEnabled(True)
		self.comboBox_y.setEnabled(True)
		self.lineEdit_tmin.setEnabled(True)
		self.lineEdit_tmax.setEnabled(True)
		self.lineEdit_ymin.setEnabled(True)
		self.lineEdit_ymax.setEnabled(True)
		self.radioButton_Fit_Plot.setEnabled(False)
		self.radioButton_Time_Interval.setEnabled(False)
		self.lineEdit_Time_Interval.setEnabled(False)
		self.label_20.setEnabled(False)
		self.label_3.setEnabled(True)
		self.label_4.setEnabled(True)
		self.label_5.setEnabled(True)
		self.label_6.setEnabled(True)
		self.checkBox_roi.setEnabled(True)		
					
	def stop_plot(self):
		self.data_stop()	
		self.timer.stop()
		self.mcc.usbClose()
		
	def run_dialog(self):	
		if len(self.data) > 0:
			self.dialog.show()
		else:
			self.time_start = time.clock()
			self.time_data = []
			self.time_data.append(np.zeros(self.num_sample))
			self.selected_chan = []
			self.data = []
			self.readParams()
			self.data_run()
			for i in range(0,8):
				if self.chan[i] == 1:
					self.data.append(np.zeros(self.num_sample))
					self.selected_chan.append(i)
			self.mcc.usbOpen()
			self.timer.start(self.sample_rate)
			
	def accepted(self):
		print("accepted")
		self.readParams()
		self.data_run()
		if self.dialog.checkBox.isChecked():
			self.time_start = time.clock()
			self.time_data = []
			self.time_data.append(np.zeros(self.num_sample))
			self.selected_chan = []
			self.data = []
			self.count = 0
			for i in range(0,8):
				if self.chan[i] == 1:
					self.data.append(np.zeros(self.num_sample))
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
    
