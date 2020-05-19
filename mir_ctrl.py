import lens_control
import numpy
from PyQt4 import QtGui, QtCore, Qt

class controller(QtCore.QThread):

    def __init__(self,interface):
        QtCore.QThread.__init__(self)
        
        self.interface=interface
        self.lens=lens_control.lens(self.interface,False)
        self.newinput=False
        self.opmode="GO base"
        self.input=numpy.zeros(18)

    def change_op(self):
        if self.interface.Base_box.currentText()=="Voltages":
            self.opmode="Voltages"
            
        if self.interface.Base_box.currentText()=="GO base":
            self.opmode="GO base"
                            
        if self.interface.Base_box.currentText()=="Zernikes":
            self.opmode="Zernikes" 

    def set_values(self,values):
        self.input=values
        self.newinput=True

    def relax(self):
        self.interface.optimizer.running=False
        self.interface.optimizer.reset
        self.lens.relax()
        self.set_values(numpy.zeros(18))
        self.interface.set_values(numpy.zeros(18))



    def run(self):
        while True:
            if self.newinput:
                if self.opmode=="Voltages":
                    self.lens.setvoltages(self.input)
                if self.opmode=="Zernikes":
                    self.lens.setzernikes(self.input)
                if self.opmode=="GO base":
                    self.lens.setort(self.input)
                self.newinput=False
