from i2cdev import I2C
from signal import *
import sys
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore
from threading import Thread

__author__ = 'Nicola La Gloria'


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
        if t & 0x1000:      # if temperature is < 0
            temp -= 256
        return temp

    def close(self):
        self.i2c.close()
        print("Exit")
        sys.exit(0)


class UIWindow(object):

    def __init__(self):
        self.window = QtWidgets.QWidget()
        self.window.setGeometry(0, 0, 320, 240)
        self.label = QtWidgets.QLabel(" warpx.io i2C Temperature Sensor Demo")
        self.lcd_number = QtWidgets.QLCDNumber(self.window)
        self.lcd_number.setGeometry(QtCore.QRect(20, 20, 100, 30))
        self.newfont = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)
        self.label.setFont(self.newfont)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lcd_number)
        self.window.setLayout(self.layout)
        self.window.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.window.show()

        device, bus = 0x18, 2
        self.my_device = Device(device, bus)
        t = Thread(target=self.display_temperature)
        t.start()

    def display_temperature(self):
        while 1:
            self.lcd_number.display("%0.2f" % self.my_device.read_temperature())
            time.sleep(2)


def main():
        app = QtWidgets.QApplication(sys.argv)
        window = UIWindow()
        ret = app.exec_()
        window.my_device.close()
        sys.exit(ret)

if __name__ == '__main__':
    main()

