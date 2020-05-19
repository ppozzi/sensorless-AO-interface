from PyQt4 import QtGui, QtCore, Qt
import numpy
import PIL.Image

##-----------------------------------------------------------------------
## Module allowing to select an area of interest on the computer screen
## and acquire screenshots, converted in numpy arrays
##-----------------------------------------------------------------------

## The qt dialog window on which the area of interest must be selected
class areaOfInterest(QtGui.QDialog):
## a signal communicating the coordinates of the area of interest selected
    coordsignal=QtCore.pyqtSignal(numpy.ndarray)


## the parent is actually the main software interface window
    def __init__(self,parent=None):
        super(areaOfInterest,self).__init__(parent)

        self.parent=parent

## acquires one image of the computer second screen. x,y,width and height
## must be adjusted in order to work on computer with different number
## of monitors, or different resolutions.
        self.geom= QtGui.QApplication.desktop().screenGeometry()
        image=QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),self.geom.x(),self.geom.y(),self.geom.width(),self.geom.height())
        self.move(0,0)
        self.resize(self.geom.width(),self.geom.height())

## a rubberband widget to highlight the selected area
        self.rubberband=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

        self.drawing=False
        
## Creation of the dialog window. Only contains a scrollable image of the
## desktop. Mouse clicks are connected to the class functions
        
        self.imageArea=QtGui.QScrollArea()
        self.imageArea.setWidgetResizable(True)
        self.imageLabel=QtGui.QLabel()
        self.imageLabel.setPixmap(image)
        self.imageLabel.mousePressEvent=self.clickOnLabel
        self.imageLabel.mouseReleaseEvent=self.releaseOnLabel
        self.imageLabel.mouseMoveEvent=self.moveOnLabel
        self.imageArea.setWidget(self.imageLabel)

        self.layout=QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.imageArea)

        self.endLabel=0
        self.originLabel=0

    def newImage(self):
        image=QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),self.geom.x(),self.geom.y(),self.geom.width(),self.geom.height())
        self.imageLabel.setPixmap(image)

## mouse click function, if the button pressed is the left button,
## sets the mouse coordinates as the first corner of the area
## of interest, and starts drawing the rubberband. If the button
## pressed is the right button, closes the window emitting the
## coordinates signal
    def clickOnLabel(self, event):
        if event.button()==1:
            self.originLabel=event.pos()
            self.drawing=True
            self.origin=event.pos()
            self.origin.setX(self.origin.x()+self.imageLabel.geometry().x()+13)
            self.origin.setY(self.origin.y()+self.imageLabel.geometry().y()+13)
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, QtCore.QSize()))
            self.rubberband.show()
            QtGui.QWidget.mousePressEvent(self, event)
        if event.button()==2:
            if self.endLabel!=0 and self.originLabel!=0:
                x=self.originLabel.x()
                y=self.originLabel.y()
                width=self.endLabel.x()-self.originLabel.x()
                height=self.endLabel.y()-self.originLabel.y()
                self.coordsignal.emit(numpy.asarray([x,y,width,height]))
            self.close()
            
## if the left mouse button is pressed, this function updates the
## rubberband drawing
    def moveOnLabel(self, event):
        if self.drawing:
            if self.rubberband.isVisible():
                position=event.pos()
                position.setX(position.x()+self.imageLabel.geometry().x()+13)
                position.setY(position.y()+self.imageLabel.geometry().y()+13)
                self.rubberband.setGeometry(
                    QtCore.QRect(self.origin, position).normalized())
        QtGui.QWidget.mouseMoveEvent(self, event)

## if the left mouse button is released, sets the mouse coordinates as
## the opposite corner of the area of interest
    def releaseOnLabel(self, event):
        self.endLabel=event.pos()
        self.drawing=False
        QtGui.QWidget.mouseReleaseEvent(self, event)


## the imagegrabber class, which can open the areaofinterest dialog,
## and acquire screenshots of the selected area of interest
class screengrabber(QtCore.QThread):
    def __init__(self,interface):
        QtCore.QThread.__init__(self)
        self.interface=interface
        self.AOI=areaOfInterest(interface)

        self.AOI.coordsignal.connect(self.changeCoordinates)

        self.grab_trigger=False
        self.lastimage=numpy.zeros((100,100))

## vfariables storing the location of the screenshots area
        self.x=0
        self.y=0
        self.width=1280
        self.height=1024


## function opening the dialog
    def openAreaWindow(self):
        self.AOI.newImage()
        self.AOI.exec_()

## function taking a screenshot, and converting it to a numpy array
## of size width x height x colors
    def grabimage(self):
        incomingImage = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),self.x,self.y,self.width, self.height).toImage()
        incomingImage = incomingImage.convertToFormat(4)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        self.lastimage = numpy.array(ptr).reshape(height, width, 4)[:,:,0:3]
        

## when the dialog window is closed, the coordinates of the screenshot
## area are updated

    def changeCoordinates(self,signalin):
        self.x=signalin[0]
        self.y=signalin[1]
        self.width=signalin[2]
        self.height=signalin[3]

    def run(self):
        while 1:
            if self.grab_trigger:
                self.grabimage()
                self.grab_trigger=False


