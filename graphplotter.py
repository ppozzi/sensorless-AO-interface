from PyQt4 import QtGui, QtCore, Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
import numpy

##-----------------------------------------------------------------------
##Module containing a pyqt thread class, managing the plotting of Zernike
##coefficients and metric graphs. The main interface script creates one
##instance of the class, and adds its parameter "canvas" to the interface
##layout.
##The function "update" must be connected to the update signal of the
##optimizer thread
##The function "reset" must be connected to the reset signal of the
##optimizer thread
##-----------------------------------------------------------------------



class graphplotter(QtCore.QThread):
    up_graph=QtCore.Signal()

    
    def __init__(self,interface):
        QtCore.QThread.__init__(self)
        self.interface=interface
        self.busy=False
        self.refresh=0.1
        self.t=time.clock()
        self.ax=self.interface.graphwid.figure.add_subplot(111)
        self.metricsgraph=self.ax.plot(numpy.asarray(range(self.interface.Iter_box.value())),numpy.zeros(self.interface.Iter_box.value()))


## The thread starts right away on its creation        
        self.start()



    def run(self):
        while 1:
            if self.interface.optimizer.running:
                if time.clock()-self.t>self.refresh and not self.busy and self.interface.optimizer.iter>2:
                    self.busy=True
                    currmet=numpy.copy(self.interface.optimizer.metrics[:self.interface.optimizer.iter])            
                    self.metricsgraph[0].set_data(range(currmet.shape[0]),currmet)
                    self.ax.set_ylim(numpy.min(currmet),numpy.max(currmet)+1)

                    self.up_graph.emit()
                    self.t=time.clock()



                
            


