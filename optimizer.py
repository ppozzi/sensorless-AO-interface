from PyQt4 import QtGui, QtCore, Qt
import numpy
import pyDONEc
import hcopt
import time
import os

class Optimizer(QtCore.QThread):
    def __init__(self,interface):
        QtCore.QThread.__init__(self)
        self.interface=interface
        self.running=False
        self.optimum=numpy.zeros(18)
        self.active=range(18)
        self.D=self.interface.Done_D_box.value()
        self.N=self.interface.Iter_box.value()
        self.hc_nsteps=self.interface.Hc_steps_box.value()
        self.lb=numpy.ones(18)
        self.ub=numpy.ones(18)
        for i in range(18):
            self.lb[i]=-self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
            self.ub[i]=self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
        self.lamb=self.interface.Done_lambda_box.value()
        self.sigma=self.interface.Done_sigma_box.value()
        self.expl=numpy.ones(18)*self.interface.Done_expl_box.value()
        self.memory=self.interface.Done_mem_box.value()
        self.iter=0

        self.calibrating=False
        self.data=None


        if os.path.isfile("done_sigmas_act.poz"):
            donesigactfile=open("done_sigmas_act.poz","rb")
            self.donesig_act=pickle.load(donesigactfile)
            donesigactfile.close()
        else:
            self.donesig_act=numpy.ones(18)
            
        if os.path.isfile("done_sigmas_ort.poz"):
            donesigortfile=open("done_sigmas_ort.poz","rb")
            self.donesig_ort=pickle.load(donesigortfile)
            donesigortfile.close()
        else:
            self.donesig_ort=numpy.ones(18)  
        
        if os.path.isfile("done_sigmas_zer.poz"):
            donesigzerfile=open("done_sigmas_zer.poz","rb")
            self.donesig_zer=pickle.load(donesigzerfile)
            donesigzerfile.close()
        else:
            self.donesig_zer=numpy.ones(18)

        self.widths=numpy.ones(18)

        self.M1=0.5
        self.M2=0.8

        self.DONE_opt=pyDONEc.optimizer(numpy.zeros(18),18,self.N,self.lb,self.ub,self.D,self.lamb,self.sigma,self.expl,self.memory)
        self.Hillclimb_opt=hcopt.optimizer(numpy.zeros(18),self.N,self.hc_nsteps,18,self.lb,self.ub)

    def reset(self):
        if self.running:
            self.toggle()
        self.iter=0
        self.interface.set_values(numpy.zeros(18))
        self.interface.graphwid.reset()
##        self.interface.graph.ax.set_xlim(0,self.interface.Iter_box.value())
        self.initialize_Done()
        self.initialize_hc()

##                    if str(self.interface.Alg_Box.currentText())=="Hillclimb":
                  
##                    if str(self.interface.Alg_Box.currentText())=="Random walk":

    def toggle(self):
        if self.running:
            self.running=False
            

        else:
            self.interface.graphwid.reset()
            self.running=True
            self.t=time.clock()
            
            

    def initialize_Done(self):
        active=[]
        limits=[]
        widths=[]
        for i in range(18):
            if self.interface.__dict__['Ab_tick_{0}'.format(i)].isChecked():
                active.append(i)
                limits.append(self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()) 
                if self.interface.Base_box.currentText()=="Voltages":
                    widths.append(self.donesig_act[i])       
                if self.interface.Base_box.currentText()=="GO base":
                    widths.append(self.donesig_ort[i])                              
                if self.interface.Base_box.currentText()=="Zernikes":
                    widths.append(self.donesig_zer[i])      

        self.widths=numpy.asarray(widths)        
        self.active=numpy.asarray(active)
        self.optimum=numpy.zeros(len(active))
        self.lb=numpy.ones(len(active))*(-1)*numpy.asarray(limits)/self.widths
        self.ub=numpy.ones(len(active))*numpy.asarray(limits)/self.widths
        self.D=self.interface.Done_D_box.value()
        self.N=self.interface.Iter_box.value()
        self.lamb=self.interface.Done_lambda_box.value()
        self.sigma=self.interface.Done_sigma_box.value()
        self.expl=numpy.ones(len(active))*self.interface.Done_expl_box.value()
        self.memory=self.interface.Done_mem_box.value()

        self.DONE_opt=pyDONEc.optimizer(numpy.zeros(len(active)),len(active),self.N,self.lb,self.ub,self.D,self.lamb,self.sigma,self.expl,self.memory)


    def initialize_hc(self):
        active=[]
        limits=[]
        for i in range(18):
            if self.interface.__dict__['Ab_tick_{0}'.format(i)].isChecked():
                active.append(i)
                limits.append(self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value())
        self.active=numpy.asarray(active)
        self.optimum=numpy.zeros(len(active))
        self.lb=numpy.ones(len(active))*(-1)*numpy.asarray(limits)
        self.ub=numpy.ones(len(active))*numpy.asarray(limits)
        self.D=self.interface.Done_D_box.value()
        self.N=self.interface.Iter_box.value()
        self.hc_nsteps=self.interface.Hc_steps_box.value()
        self.lamb=self.interface.Done_lambda_box.value()
        self.sigma=self.interface.Done_sigma_box.value()
        self.expl=numpy.ones(len(active))*self.interface.Done_expl_box.value()
        self.memory=self.interface.Done_mem_box.value()

        self.Hillclimb_opt=hcopt.optimizer(numpy.zeros(len(active)),self.N,self.hc_nsteps,len(active),self.lb,self.ub)


    def initialize_calib(self):
        if not self.running:
            self.data=data=numpy.zeros((self.active.shape[0],self.interface.Iter_box.value()/self.active.shape[0]))
            self.calibrating=True
            self.running=True


            

                
            

    def intensity_metric(self,x):
        if str(self.interface.Alg_Box.currentText())=="DONE":
            x=x*self.widths
        v=numpy.zeros(18)
        c=0
        for i in range(18):
            if i in self.active:
                v[i]=x[c]
                c+=1
            else:
                v[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
        self.interface.set_values(v)
        time.sleep(self.interface.trig_out_delay.value()*0.001)
        if self.interface.trig_out_check.isChecked():
            self.interface.trig.sendTrigger()

        if self.interface.trig_in_check.isChecked():
            self.interface.trig.waitForTrigger()
        time.sleep(self.interface.trig_in_delay.value()*0.001)
            
        self.interface.screengrabber.grab_trigger=True
        while self.interface.screengrabber.grab_trigger:
            pass
        image=self.interface.screengrabber.lastimage
        metric=numpy.sum(image).astype(float)/image.size
        self.iter+=1
        if self.iter>2:
            self.interface.graphwid.updatedata(metric,self.iter)
            self.t=time.clock()
        return metric

    def sq_intensity_metric(self,x):
        if str(self.interface.Alg_Box.currentText())=="DONE":
            x=x*self.widths
        v=numpy.zeros(18)
        c=0
        for i in range(18):
            if i in self.active:
                v[i]=x[c]
                c+=1
            else:
                v[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
        self.interface.set_values(v)
        time.sleep(self.interface.trig_out_delay.value()*0.001)
        if self.interface.trig_out_check.isChecked():
            self.interface.trig.sendTrigger()

        if self.interface.trig_in_check.isChecked():
            self.interface.trig.waitForTrigger()
        time.sleep(self.interface.trig_in_delay.value()*0.001)
            
        self.interface.screengrabber.grab_trigger=True
        while self.interface.screengrabber.grab_trigger:
            pass
        image=self.interface.screengrabber.lastimage

        metric= numpy.sum(image**2).astype(float)/image.size
        self.iter+=1
        if self.iter>2:
            pass
            self.interface.graphwid.updatedata(metric,self.iter)
        return metric




    def gradient_metric(self,x):
        if str(self.interface.Alg_Box.currentText())=="DONE":
            x=x*self.widths
        v=numpy.zeros(18)
        c=0
        for i in range(18):
            if i in self.active:
                v[i]=x[c]
                c+=1
            else:
                v[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
        self.interface.set_values(v)
        time.sleep(self.interface.trig_out_delay.value()*0.001)
        if self.interface.trig_out_check.isChecked():
            self.interface.trig.sendTrigger()

        if self.interface.trig_in_check.isChecked():
            self.interface.trig.waitForTrigger()
        time.sleep(self.interface.trig_in_delay.value()*0.001)
            
        self.interface.screengrabber.grab_trigger=True
        while self.interface.screengrabber.grab_trigger:
            pass
        image=self.interface.screengrabber.lastimage

        grad=numpy.gradient(image)
        metric=numpy.sum(numpy.sqrt(grad[0]**2+grad[1]**2))/image.size
        self.iter+=1
        if self.iter>2:
            pass
            self.interface.graphwid.updatedata(metric,self.iter)
        return metric

    def power_metric(self,x):
        if str(self.interface.Alg_Box.currentText())=="DONE":
            x=x*self.widths
        v=numpy.zeros(18)
        c=0
        for i in range(18):
            if i in self.active:
                v[i]=x[c]
                c+=1
            else:
                v[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()
        self.interface.set_values(v)
        time.sleep(self.interface.trig_out_delay.value()*0.001)
        if self.interface.trig_out_check.isChecked():
            self.interface.trig.sendTrigger()

        if self.interface.trig_in_check.isChecked():
            self.interface.trig.waitForTrigger()
        time.sleep(self.interface.trig_in_delay.value()*0.001)
            
        self.interface.screengrabber.grab_trigger=True
        while self.interface.screengrabber.grab_trigger:
            pass
        image=self.interface.screengrabber.lastimage
        image=numpy.fft.fftshift(image)
        pwr_spect=numpy.abs(numpy.fft.fftshift(numpy.fft.fft2(image)))
        coordsx,coordsy=numpy.meshgrid(numpy.linspace(-image.shape[0]/2,image.shape[0]/2,image.shape[0]),
                                       numpy.linspace(-image.shape[0]/2,image.shape[0]/2,image.shape[0]))
        metric= numpy.sum(pwr_spect[numpy.where(numpy.sqrt(coordsx**2+coordsy**2)<self.M2)])-numpy.sum(pwr_spect[numpy.where(numpy.sqrt(coordsx**2+coordsy**2)<self.M1)])
        self.iter+=1
        if self.iter>2:
            pass
            self.interface.graphwid.updatedata(metric,self.iter)
        return metric





    def run(self):
        while 1:
            if self.running:
                if not self.calibrating:
                    if self.iter>self.interface.Iter_box.value():
                        self.interface.goto_opt()
                        self.running=False
                        self.iter=0

                    else:

                        if not self.interface.screengrabber.grab_trigger:
                            if str(self.interface.Alg_Box.currentText())=="DONE":
                                if str(self.interface.Metric_Box.currentText())=="Intensity":
                                    self.DONE_opt.step(self.intensity_metric)
                                if str(self.interface.Metric_Box.currentText())=="Gradient":
                                    self.DONE_opt.step(self.gradient_metric)
                                if str(self.interface.Metric_Box.currentText())=="Sq. Intensity":
                                    self.DONE_opt.step(self.sq_intensity_metric)
                                if str(self.interface.Metric_Box.currentText())=="Power spectrum":
                                    self.DONE_opt.step(self.power_metric)
                                self.optimum=numpy.zeros(18)
                                c=0
                                for i in range(18):
                                    if i in self.active:
                                        self.optimum[i]=self.DONE_opt.getmax()[c]
                                        c+=1
                                    else:
                                        self.optimum[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()

                            if str(self.interface.Alg_Box.currentText())=="Hillclimb":
                                    if str(self.interface.Metric_Box.currentText())=="Intensity":
                                        self.Hillclimb_opt.step(self.intensity_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Gradient":
                                        self.Hillclimb_opt.step(self.gradient_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Sq. Intensity":
                                        self.Hillclimb_opt.step(self.sq_intensity_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Power spectrum":
                                        self.Hillclimb_opt.step(self.power_metric)
                                    self.optimum=numpy.zeros(18)
                                    c=0
                                    for i in range(18):
                                        if i in self.active:
                                            self.optimum[i]=self.Hillclimb_opt.getmax()[c]
                                            c+=1
                                        else:
                                            self.optimum[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()

                            if str(self.interface.Alg_Box.currentText())=="Random walk":
                                    if str(self.interface.Metric_Box.currentText())=="Intensity":
                                        self.Hillclimb_opt.step(self.intensity_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Gradient":
                                        self.Hillclimb_opt.step(self.gradient_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Sq. Intensity":
                                        self.Hillclimb_opt.step(self.sq_intensity_metric)
                                    if str(self.interface.Metric_Box.currentText())=="Power spectrum":
                                        self.Hillclimb_opt.step(power_metric)
                                    self.optimum=numpy.zeros(18)
                                    c=0
                                    for i in range(18):
                                        if i in self.active:
                                            self.optimum[i]=self.Hillclimb_opt.getmax()[c]
                                            c+=1
                                        else:
                                            self.optimum[i]=float(self.interface.__dict__['Ab_val_slid_{0}'.format(i)].value())/1000.0*self.interface.__dict__['Ab_lim_box_{0}'.format(i)].value()



                else:
                    c=0
                    for i in range(self.active.shape[0]):
                        c=0
                        for j in numpy.linspace(self.lb[i],self.ub[i],self.interface.Iter_box.value()/self.active.shape[0]):
                            v=numpy.zeros(self.active.shape[0])
                            v[i]=j
                            if str(self.interface.Metric_Box.currentText())=="Intensity":
                                self.data[i,c]=self.intensity_metric(v)
                            if str(self.interface.Metric_Box.currentText())=="Gradient":
                                self.data[i,c]=self.gradient_metric(v)
                            if str(self.interface.Metric_Box.currentText())=="Sq. Intensity":
                                self.data[i,c]=self.sq_intensity_metric(v)
                            if str(self.interface.Metric_Box.currentText())=="Power spectrum":
                                self.data[i,c]=self.power_metric(v)

                            print i,j,self.data[i,c]
                            
                            c+=1
                    self.calibrating=False
                    self.interface.set_values(numpy.zeros(18))
                    self.running=False


