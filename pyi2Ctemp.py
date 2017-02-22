#!/usr/bin/python

from i2cdev import I2C
from signal import *
import sys
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal

from threading import Thread

import os

__author__ = 'Nicola La Gloria and Aaron Oki Moore'


class Device(object):
	def __init__(self, device, bus):
		self.device = device
		self.bus = bus
		self.i2c = I2C(device, bus)
		self.MCP9808_REG_AMBIENT_TEMP = b'\x05'
		self.MCP9808_REG_CONFIG = b'\x01'
		self.MCP9808_REG_CONFIG_SHUTDOWN = b'\x0100'

	def init_device(self):
		self.i2c.write(self.MCP9808_REG_CONFIG)
		self.i2c.write(self.MCP9808_REG_CONFIG_SHUTDOWN)

	def read_temperature(self):
		self.i2c.write(self.MCP9808_REG_AMBIENT_TEMP)
		val = self.i2c.read(2)  # read 16 bit register
		t = int(val.encode("hex"), 16)
		temp = float(t & 0x0fff) / 16
		if t & 0x1000:	  # if temperature is < 0
			temp -= 256
		return temp

	def close(self):
		self.i2c.close()
		print("Exit")
		sys.exit(0)

class TemperatureWidget(QtWidgets.QWidget):
	def __init__(self, temperature = "--.-", units = "C", size = 48, palette = None):      
		super(TemperatureWidget,self).__init__()
		
		self.label = QtWidgets.QLabel()
		self.label_units = QtWidgets.QLabel()
		
		self.setTemperature( temperature )
		self.setUnits( units )
		
		self.label.setPalette(palette)
		self.label_units.setPalette(palette)
		
		self.label.setFont(QtGui.QFont("Effra", size))
		self.label.setContentsMargins(0,0,0,0)
		
		self.label_units.setFont(QtGui.QFont("Effra", size/1.6))
		self.label_units.setContentsMargins( 0, round(size/8), 0, round(size/4))
		
		self.layout = QtWidgets.QHBoxLayout()
		self.layout.setContentsMargins(0,0,0,0)
		
		self.layout.setSpacing(0)
		self.layout.addWidget( self.label )
		self.layout.addWidget( self.label_units )
		self.layout.addStretch()		
		
		self.setLayout( self.layout )
		
		
	
	def setUnits( self, unit_str, show_degree = True ):
		
		if( show_degree and unit_str[0] != "&deg;" ):
			self.label_units.setText( "<html>&deg;" + unit_str + "</html>" )
		else:
			self.label_units.setText(unit_str)
	
		
	def setTemperature( self, temperature ):
		
		if( isinstance(temperature,str) ):
			self.label.setText( temperature )
	
		elif( isinstance(temperature,int) or isinstance(temperature,float) ):
			temperature_format = "%0.1f"
			self.label.setText( temperature_format % temperature )

		else :
			self.label.setText( "--.-" )

class UIWindow( QtWidgets.QWidget ):

	def __init__(self):
		super(UIWindow,self).__init__()
		
		#self.window = QtWidgets.QWidget()
		self.setGeometry(0, 0, 320, 240)
		
		# set Window background color
		self.window_palette = self.palette()
		self.window_palette.setColor(self.backgroundRole(), QtGui.QColor(0,0,0) )
		self.setPalette(self.window_palette)
		
		# define a few more palettes for fonts
		
		palette_fg_white = self.palette();
		palette_fg_white.setColor(QtGui.QPalette.Foreground, QtCore.Qt.white) #QtGui.QColor(255,255,255));
		
		palette_fg_tan = self.palette();
		palette_fg_tan.setColor(QtGui.QPalette.Foreground, QtGui.QColor(200,200,200))
		
		palette_fg_gray = self.palette();
		palette_fg_gray.setColor(QtGui.QPalette.Foreground, QtGui.QColor(200,200,200))
			
		#define some fonts
		#self.newfont = QtGui.QFont("Effra", 12, QtGui.QFont.Bold)
		font_label = QtGui.QFont("Effra", 14)
		font_city =  QtGui.QFont("Effra", 24)
	
		#define our various labels
		
		self.label_city = QtWidgets.QLabel("HOME")
		self.label_city.setPalette(palette_fg_tan)
		self.label_city.setFont( font_city )
		
		self.label_current = QtWidgets.QLabel("CURRENT TEMPERATURE:")
		self.label_current.setPalette(palette_fg_tan)
		self.label_current.setFont(font_label)
		
		#define our temperature objects
		
		self.temperature_current = TemperatureWidget(21.8, "C", 60, palette_fg_white)
		
		
		#define weather forecast objects
		self.label_dates = QtWidgets.QLabel("<font color='#a79e88'>MON &nbsp;&nbsp;&nbsp; TUE &nbsp;&nbsp;&nbsp;&nbsp; WED &nbsp;&nbsp;&nbsp;&nbsp; THU &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; FRI</font>")
		self.label_dates.setFont(font_label)
		
		img_path = os.getcwd() + "/resources/weather_icons.png"
		
		pixmap = QtGui.QPixmap( img_path )
		
		label_weather_icons = QtWidgets.QLabel()
		label_weather_icons.setContentsMargins(0,5,0,0)
		label_weather_icons.setPixmap(pixmap)
		
		
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setSpacing( 0 )
		self.layout.setContentsMargins(25,25,0,0) #when we rotate layout, this order will change
		
		self.layout.addWidget( self.label_city )
		self.layout.addSpacing(15)
		
		self.layout.addWidget( self.label_current )
		self.layout.addWidget( self.temperature_current )
		
		self.layout.addSpacing(10)
		
		self.layout.addWidget( self.label_dates )
		self.layout.addWidget(label_weather_icons)
		
		self.layout.addStretch()
		
		self.setLayout(self.layout)
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)

		device, bus = 0x18, 2
		try:
			self.my_device = Device(device, bus)
			self.thread = DeviceThread(self.my_device)		
			self.thread.start()
		
			self.thread.signal.connect( self.eventHandler )
		except:
			pass;
		
	hvac_mode = None
	
	def eventHandler(self, temp):
		if ( temp > 28.4 and self.hvac_mode == None ):
			
			self.window_palette.setColor(self.backgroundRole(), QtGui.QColor(24,75,255) )
			self.setPalette(self.window_palette)
			
			self.label_city.setStyleSheet("background-color: rgb(24,75,255); color: rgb(235,235,235)");
			self.label_current.setStyleSheet("background-color: rgb(24,75,255); color: rgb(235,235,235)");
			
			self.label_dates.setStyleSheet("background-color: rgb(24,75,255); color: rgb(235,235,235)");
			
			
			
			self.temperature_current.label.setStyleSheet("background-color: rgb(24,75,255);");
			self.temperature_current.label_units.setStyleSheet("background-color: rgb(24,75,255);");
			
			
			self.hvac_mode = "Cool"
			
		elif( temp < 23.5 and self.hvac_mode == None ):
			self.window_palette.setColor(self.backgroundRole(), QtGui.QColor(255,127,17) )
			self.setPalette(self.window_palette)
			
			self.label_city.setStyleSheet("background-color: rgb(255,127,17); color: rgb(200,200,200)");
			self.label_current.setStyleSheet("background-color: rgb(255,127,17); color: rgb(200,200,200)");
			
			self.label_dates.setStyleSheet("background-color: rgb(255,127,17); color: rgb(200,200,200)");
			
			
			self.temperature_current.label.setStyleSheet("background-color: rgb(255,127,17);");
			self.temperature_current.label_units.setStyleSheet("background-color: rgb(255,127,17);");
			
			
			
			
			self.hvac_mode = "Heat"
			
		if( (temp < 26.0 and self.hvac_mode == "Cool" ) or (temp > 25.0 and self.hvac_mode == "Heat") ):
			self.window_palette.setColor(self.backgroundRole(), QtGui.QColor(0,0,0) )
			self.setPalette(self.window_palette)
			self.label_city.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)");
			self.label_current.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)");
			
			self.label_dates.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)");
			
			self.temperature_current.label.setStyleSheet("background-color: rgb(0,0,0);");
			self.temperature_current.label_units.setStyleSheet("background-color: rgb(0,0,0);");
			
			
			self.hvac_mode = None
			
		self.temperature_current.setTemperature(temp)
			
class DeviceThread(QtCore.QThread):
	signal = pyqtSignal(float)
	device = None
	
	def __init__(self,device):
		super(DeviceThread,self).__init__()
		self._running = True
		self.device = device
		
	def run(self):
		last = None
		while self._running:
			temp = self.device.read_temperature()
			
			if( temp != last ):
				self.signal.emit(temp)
				last = temp
			#self.temperature_current.setTemperature( temp )
			time.sleep(0.25)
			
def main():
	app = QtWidgets.QApplication(sys.argv)
	window = UIWindow()
	window.show()
	ret = app.exec_()
	window.my_device.close()
	window._running = False
	sys.exit(ret)

if __name__ == '__main__':
	main()

