from i2cdev import I2C
from signal import *
import sys
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
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
		super().__init__()
		self.label = QtWidgets.QLabel()
		self.label_units = QtWidgets.QLabel()
		
		self.setTemperature( temperature )
		self.setUnits( units )
		
		self.label.setPalette(palette)
		self.label_units.setPalette(palette)
		
		self.label.setFont(QtGui.QFont("Arial", size))
		self.label.setContentsMargins(0,0,0,0)
		
		self.label_units.setFont(QtGui.QFont("Arial", size/1.6))
		self.label_units.setContentsMargins( round(size/8), round(size/4),0,0)
		
		
		self.layout = QtWidgets.QHBoxLayout()
		self.layout.setContentsMargins(0,0,0,0)
		
		self.layout.setSpacing(0)
		self.layout.addWidget( self.label )
		self.layout.addWidget( self.label_units )
		self.layout.addStretch()
		
		self.setLayout( self.layout )
	
	def setUnits( self, unit_str, show_degree = True ):
		
		if( show_degree and unit_str[0] != "°" ):
			self.label_units.setText( "°" + unit_str )
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

class UIWindow(object):

	def __init__(self):
		self.window = QtWidgets.QWidget()
		self.window.setGeometry(0, 0, 240, 320)
		
		# set Window background color
		
		window_palette = self.window.palette()
		window_palette.setColor(self.window.backgroundRole(), QtGui.QColor(32,32,32) )
		self.window.setPalette(window_palette)
		
		# define a few more palettes for fonts
		
		palette_fg_white = self.window.palette();
		palette_fg_white.setColor(QtGui.QPalette.Foreground, QtCore.Qt.white) #QtGui.QColor(255,255,255));
		
		palette_fg_tan = self.window.palette();
		palette_fg_tan.setColor(QtGui.QPalette.Foreground, QtGui.QColor(167,158,136))
		
		palette_fg_gray = self.window.palette();
		palette_fg_gray.setColor(QtGui.QPalette.Foreground, QtGui.QColor(127,127,127))
			
		#define some fonts
		#self.newfont = QtGui.QFont("Effra", 12, QtGui.QFont.Bold)
		font_label = QtGui.QFont("Arial", 14)
		font_city =  QtGui.QFont("Arail", 18)
	
		#define our various labels
		
		label_city = QtWidgets.QLabel("PORTALAND, OR")
		label_city.setPalette(palette_fg_tan)
		label_city.setFont( font_city )
		
		label_current = QtWidgets.QLabel("<font color='#a79e88'>CURRENT</font>")
		label_current.setFont(font_label)
		
		label_outside = QtWidgets.QLabel("<font color='#a79e88'>OUTSIDE</font>")
		label_outside.setFont(font_label)
		
		label_feelslike = QtWidgets.QLabel("<font color='#a79e88'>FEELS LIKE</font>")
		label_feelslike.setFont(font_label)
		
		#define our temperature objects
		
		self.temperature_current = TemperatureWidget(21.1, "C", 48, palette_fg_white)
		self.temperature_outside = TemperatureWidget(18.7, "C", 24, palette_fg_gray)
		self.temperature_feelslike = TemperatureWidget(None, "C", 24, palette_fg_gray)
		
		
		#define weather forecast objects
		label_dates = QtWidgets.QLabel("<font color='#a79e88'>TUE &nbsp; WED &nbsp; THU &nbsp;&nbsp;&nbsp; FRI &nbsp;&nbsp;&nbsp;&nbsp; SAT</font>")
		label_dates.setFont(font_label)
		
		img_path = os.getcwd() + '/resources/weather_icons.png'
		#if ( not os.path.isfile(img_path) ):
		#	print ( "img not found" )
		pixmap = QtGui.QPixmap( img_path )
		label_weather_icons = QtWidgets.QLabel()
		label_weather_icons.setContentsMargins(0,5,0,0)
		label_weather_icons.setPixmap(pixmap)
		
		
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setSpacing( 0 )
		self.layout.setContentsMargins(16,20,0,0) #when we rotate layout, this order will change
		
		self.layout.addWidget(label_city)
		self.layout.addSpacing(20)
		
		self.layout.addWidget( label_current )
		self.layout.addWidget( self.temperature_current )
		
		self.layout.addSpacing(10)
		
		ext_temperature_layout = QtWidgets.QHBoxLayout()
		self.layout.addLayout(ext_temperature_layout)
		
		outside_temperature_container_layout = QtWidgets.QVBoxLayout()
		outside_temperature_container_layout.addWidget(label_outside)
		outside_temperature_container_layout.addWidget(self.temperature_outside)
		
		feelslike_temperature_container_layout = QtWidgets.QVBoxLayout()
		feelslike_temperature_container_layout.addWidget(label_feelslike)
		feelslike_temperature_container_layout.addWidget(self.temperature_feelslike)
		
		ext_temperature_layout.addLayout(outside_temperature_container_layout)
		ext_temperature_layout.addSpacing(25)
		ext_temperature_layout.addLayout(feelslike_temperature_container_layout)
		ext_temperature_layout.addStretch()
		
		self.layout.addSpacing(40)
		self.layout.addWidget( label_dates )		
		self.layout.addWidget(label_weather_icons)
		self.layout.addStretch()
		
		self.window.setLayout(self.layout)
		self.window.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
		self.window.show()

		device, bus = 0x18, 2
		self.my_device = Device(device, bus)
		self.t = Thread(target=self.display_temperature)
		self._running = True
		self.t.start()

	def display_temperature(self):
		while self._running:
			self.temperature_current.setTemperature( self.my_device.read_temperature )
			time.sleep(1)

def main():
	app = QtWidgets.QApplication(sys.argv)
	window = UIWindow()
	ret = app.exec_()
	window.my_device.close()
	window._running = False
	sys.exit(ret)

if __name__ == '__main__':
	main()

