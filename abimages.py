from PyQt4 import QtGui, QtCore, Qt
import numpy
import PIL
import pickle
import os


class imggen(QtCore.QThread):

    
    def __init__(self,interface):
        QtCore.QThread.__init__(self)
        self.interface=interface
        self.acts=numpy.zeros((128,128,18))
        for i in range(18):
            self.acts[:,:,i]=numpy.asarray(PIL.Image.open("thumbs"+self.interface.lensname+"\\actuators\\act"+str(i).zfill(2)+".tif"))
        self.zers=numpy.zeros((128,128,18))
        for i in range(18):
            self.zers[:,:,i]=numpy.asarray(PIL.Image.open("thumbs"+self.interface.lensname+"\\zernikes\\zer"+str(i).zfill(2)+".tif"))
        self.orts=numpy.zeros((128,128,18))
        for i in range(18):
            self.orts[:,:,i]=numpy.asarray(PIL.Image.open("thumbs"+self.interface.lensname+"\\orthogonal\\zer"+str(i).zfill(2)+".tif"))

        ortstrokesfile=open("orthogonal_strokes"+self.interface.lensname+".poz","rb")
        self.ortstrokes=numpy.mean(pickle.load(ortstrokesfile),axis=1)
        ortstrokesfile.close()
        zerstrokesfile=open("zernike_strokes"+self.interface.lensname+".poz","rb")
        self.zerstrokes=numpy.mean(pickle.load(zerstrokesfile),axis=1)
        zerstrokesfile.close()

        self.ab_plot=numpy.ones((128,128))*128.0
        

        self.set_thumbnails()



    def generate_ab(self):
        weights=numpy.zeros(18)
        for i in range(18):
            weights[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
            
        if self.interface.Base_box.currentText()=="Voltages":
            self.ab_plot=numpy.sum(self.acts*weights[None,None,:],axis=2)
            
        if self.interface.Base_box.currentText()=="GO base":
            self.ab_plot=numpy.sum(self.orts*weights[None,None,:],axis=2)
                            
        if self.interface.Base_box.currentText()=="Zernikes":
            self.ab_plot=numpy.sum(self.zers*weights[None,None,:],axis=2)                  


    def update_image(self):
        self.generate_ab()
        showimage=self.convert8(numpy.modf(self.ab_plot-numpy.min(self.ab_plot))[0])
        img=QtGui.QImage(showimage.data,128,128,QtGui.QImage.Format_Indexed8)
        imgpixmap=QtGui.QPixmap.fromImage(img)
        self.interface.Aberration_label.setPixmap(imgpixmap.scaled(290,290))


    def set_thumbnails(self):
        if self.interface.Base_box.currentText()=="Voltages":
            for i in range(18):
                act8=self.convert8(self.acts[:,:,i])
                imgact=QtGui.QImage(act8.data,128,128,QtGui.QImage.Format_Indexed8)
                imgpixmap=QtGui.QPixmap.fromImage(imgact)
                self.interface.__dict__['Ab_thumb_{0}'.format(i)].setPixmap(imgpixmap.scaled(25,25))
                self.interface.__dict__['Ab_lim_box_{0}'.format(i)].setValue(1.0)
        if self.interface.Base_box.currentText()=="GO base":
            for i in range(18):
                ort8=self.convert8(self.orts[:,:,i])
                imgort=QtGui.QImage(ort8.data,128,128,QtGui.QImage.Format_Indexed8)
                ortpixmap=QtGui.QPixmap.fromImage(imgort)
                self.interface.__dict__['Ab_thumb_{0}'.format(i)].setPixmap(ortpixmap.scaled(25,25))
                self.interface.__dict__['Ab_lim_box_{0}'.format(i)].setValue(self.ortstrokes[i])
        if self.interface.Base_box.currentText()=="Zernikes":
            for i in range(18):
                zer8=self.convert8(self.zers[:,:,i])
                imgzer=QtGui.QImage(zer8.data,128,128,QtGui.QImage.Format_Indexed8)
                zerpixmap=QtGui.QPixmap.fromImage(imgzer)
                self.interface.__dict__['Ab_thumb_{0}'.format(i)].setPixmap(zerpixmap.scaled(25,25))
                self.interface.__dict__['Ab_lim_box_{0}'.format(i)].setValue(self.zerstrokes[i])

    def save_ab(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self.interface, 'Save Aberration', 'Saved_aberrations', selectedFilter='*.tif')
        if fileName:
            PIL.Image.fromarray(self.ab_plot).save(str(fileName))

    def convert8(self,image):
        Min=numpy.min(image)
        Max=numpy.max(image)
        if Min==Max:
            image_c=numpy.ones((128,128))*128.0
        else:
            image_c=(image-Min)/(Max-Min)*255.0
        return image_c.astype("uint8")
