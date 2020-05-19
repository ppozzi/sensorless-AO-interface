import sys
from PyQt4 import QtGui, QtCore, uic
import numpy
import mir_ctrl
import screengrab
import optimizer
import graphplotter
import abimages
import triggers



class MyWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.lensname="ZEISScustom"
        uic.loadUi('interface.ui', self)
        try:
            self.trig=triggers.triggerIO()
        except:
            self.trig=triggers.dummytrigger()
            msgBox = QtGui.QMessageBox( self )
            msgBox.setIcon( QtGui.QMessageBox.Information )
            msgBox.setText( "Trigger box not connected." )
            msgBox.exec_()
        self.abimggen=abimages.imggen(self)
        self.connect(self.Base_box,QtCore.SIGNAL("currentIndexChanged(int)"),self.abimggen.set_thumbnails)
        self.connect(self.save_ab_butt,QtCore.SIGNAL('clicked()'),self.abimggen.save_ab)
        self.graphwid.interface=self
        self.graphwid.reset()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.graphwid.update)
        self.timer.start(100)
        self.lensctr=mir_ctrl.controller(self)
        self.lensctr.start()
        self.connect(self.Base_box,QtCore.SIGNAL("currentIndexChanged(int)"),self.lensctr.change_op)
        self.screengrabber=screengrab.screengrabber(self)
        self.screengrabber.start()
        self.connect(self.selectarea_butt,QtCore.SIGNAL('clicked()'),self.screengrabber.openAreaWindow)
        self.optimizer=optimizer.Optimizer(self)
        self.connect(self.reset_butt,QtCore.SIGNAL('clicked()'),self.optimizer.reset)
        self.connect(self.Start_butt,QtCore.SIGNAL('clicked()'),self.optimizer.toggle)
        self.connect(self.gotoopt_butt,QtCore.SIGNAL('clicked()'),self.goto_opt)
        self.connect(self.cal_done_sig_but,QtCore.SIGNAL('clicked()'),self.optimizer.initialize_calib)
        self.optimizer.start()

        for x in range(18):
            self.connect(self.__dict__['Ab_val_slid_{0}'.format(x)],QtCore.SIGNAL('sliderMoved(int)'),self.update_ab)
        for x in range(18):
            self.connect(self.__dict__['Ab_lim_box_{0}'.format(x)],QtCore.SIGNAL('valueChanged(double)'),self.update_ab)

        self.connect(self.Relax_butt,QtCore.SIGNAL('clicked()'),self.lensctr.relax)
        self.connect(self.saveflat_butt,QtCore.SIGNAL('clicked()'),self.lensctr.saveflat)
        self.connect(self.s_a_butt,QtCore.SIGNAL('clicked()'),self.select_all)
        self.connect(self.ds_a_butt,QtCore.SIGNAL('clicked()'),self.deselect_all)
        self.connect(self.s_a_nt_butt,QtCore.SIGNAL('clicked()'),self.select_nt)


        self.ticks=numpy.zeros(18)
        self.vals=numpy.zeros(18)
        self.lims=numpy.zeros(18)
        
        
        self.show()


    def update_ab(self):
        out=numpy.zeros(18)
        for x in range(18):
            out[x]=float(self.__dict__['Ab_val_slid_{0}'.format(x)].value())/1000.0*self.__dict__['Ab_lim_box_{0}'.format(x)].value()
        self.lensctr.set_values(out)

    def goto_opt(self):
        self.set_values(self.optimizer.optimum)


##    def update_graph(self):
##        if self.optimizer.iter>2:
##            self.graphwid.canvas.draw()
##        self.graph.busy=False

    def set_values(self,values):
        for x in range(18):
            if values[x]>self.__dict__['Ab_lim_box_{0}'.format(x)].value():
                self.__dict__['Ab_val_slid_{0}'.format(x)].setValue(1000)
            elif values[x]<-self.__dict__['Ab_lim_box_{0}'.format(x)].value():
                self.__dict__['Ab_val_slid_{0}'.format(x)].setValue(-1000)
            else:
                self.__dict__['Ab_val_slid_{0}'.format(x)].setValue(int(values[x]/self.__dict__['Ab_lim_box_{0}'.format(x)].value()*1000))

        self.update_ab()

    def select_all(self):
        for x in range(18):
            self.__dict__['Ab_tick_{0}'.format(x)].setChecked(True) 
    def deselect_all(self):
        for x in range(18):
            self.__dict__['Ab_tick_{0}'.format(x)].setChecked(False) 
    def select_nt(self):
        for x in range(3):
            self.__dict__['Ab_tick_{0}'.format(x)].setChecked(False) 
        for x in range(3,18):
            self.__dict__['Ab_tick_{0}'.format(x)].setChecked(True) 

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
