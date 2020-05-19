from PyQt4 import QtGui,QtCore
import pyqtgraph as pg
import numpy as np
import time
##from matplotlib.figure import Figure
##from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
##from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class graphwidget(QtGui.QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(graphwidget, self).__init__(parent)
        self.interface=None
        pg.setConfigOptions(antialias=True)
        self.graphw=pg.GraphicsLayoutWidget()
        self.p6 = self.graphw.addPlot()
        self.p6.setLabel('left', "Metric")
        self.p6.setLabel('bottom', "Iteration")
        self.curve = self.p6.plot(pen='y')
        self.data=[]
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.graphw)
        self.setLayout(layout)
        self.working=False



    def reset(self):
        self.p6.clear()
        self.curve = self.p6.plot(pen='y')
        self.data=[]
        self.p6.setXRange(0, self.interface.Iter_box.value(), padding=0)


    def updatedata(self,data,i):
        self.data.append(data)

        

    def update(self):
        self.curve.setData(self.data)
        pg.QtGui.QApplication.processEvents()
        self.interface.abimggen.update_image()


