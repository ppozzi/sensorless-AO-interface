import numpy
import sys
import os
import time
import pickle
import usb.core
import usb.util



class lens:
    
    def __init__(self,interface,hyst_comp=True):
        self.interface=interface
        
        


        self.SENT_CHANNELS=32
        self.DAC_BITS=12
        self.num_act=18
        
        ##opening connection to the device, based on device ids
        self.dev = usb.core.find(idVendor=0x483, idProduct=0x5750)

        if self.dev is None:
            print "warning: No device found"
        ##set device to configuration number one (parameters can be visualized by
        ## with the command "print self.dev")
        self.dev.set_configuration()
        self.hyst_comp=hyst_comp



        self.voltages=numpy.zeros(self.num_act)


        ##import calibration values for zernikes and gradient orthogonal modes
        
        if os.path.isfile("zernikes_"+self.interface.lensname+".poz"):
            zervoltfile=open("zernikes_"+self.interface.lensname+".poz","rb")
            self.zervolt=pickle.load(zervoltfile)
            zervoltfile.close()
        else:
            print "No zernike calibration found"


        if os.path.isfile("solovievs_"+self.interface.lensname+".poz"):
            ortbasefile=open("solovievs_"+self.interface.lensname+".poz","rb")
            self.ortbase=pickle.load(ortbasefile)
            ortbasefile.close()
        else:
            print "No ortogonal calibration found"

        if os.path.isfile("acttozer_"+self.interface.lensname+".poz"):
            acttozerfile=open("acttozer_"+self.interface.lensname+".poz","rb")
            self.acttozer=pickle.load(acttozerfile)
            acttozerfile.close()
        else:
            print "No zernike matrix calibration found"        

        if os.path.isfile("acttosol_"+self.interface.lensname+".poz"):
            acttosolfile=open("acttosol_"+self.interface.lensname+".poz","rb")
            self.acttosol=pickle.load(acttosolfile)
            acttosolfile.close()
        else:
            print "No orthogonal matrix calibration found"

        if os.path.isfile("flatvoltages_"+self.interface.lensname+".poz"):
            flatvoltfile=open("flatvoltages_"+self.interface.lensname+".poz","rb")
            self.flatvolt=pickle.load(flatvoltfile)
            flatvoltfile.close()
        else:
            print "No flat voltages file found, setting to zero"
            self.flatvolt=numpy.zeros(18)

        ##initialization of hysteresis parameters
        if self.hyst_comp==True:
            exists=True
            for i in range(self.num_act):
                if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_invp_"+str(i).zfill(2)+".txt"):
                    exists=False
                if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_invr_"+str(i).zfill(2)+".txt"):
                    exists=False
                if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_offset_"+str(i).zfill(2)+".txt"):
                    exists=False
            if exists:
                self.invp=numpy.zeros((self.num_act,7))
                self.invr=numpy.zeros((self.num_act,7))
                self.offset=numpy.zeros((self.num_act,4))
                for i in range(self.num_act):
                    self.invp[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_invp_"+str(i).zfill(2)+".txt")
                    self.invr[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_invr_"+str(i).zfill(2)+".txt")
                    self.offset[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_offset_"+str(i).zfill(2)+".txt")
                ##memory lenght
                self.memlen=200
                self.x0est=numpy.zeros(7)
                self.in_v_mem=numpy.zeros((self.num_act,self.memlen))
                self.in_t_mem=numpy.zeros(self.memlen)
                self.p_mem=numpy.zeros((self.num_act,self.memlen+1,self.invp.shape[1]))
                self.n=0
            else:
                print "hysteresis calibration not found"
                self.hyst_comp=False


    def init_hyst(self):
        exists=True
        for i in range(self.num_act):
            if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_invp_"+str(i).zfill(2)+".txt"):
                exists=False
            if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_invr_"+str(i).zfill(2)+".txt"):
                exists=False
            if not os.path.isfile("calibration"+self.interface.lensname+"//hyst_offset_"+str(i).zfill(2)+".txt"):
                exists=False
        if exists:
            self.invp=numpy.zeros((self.num_act,7))
            self.invr=numpy.zeros((self.num_act,7))
            self.offset=numpy.zeros((self.num_act,4))
            for i in range(self.num_act):
                self.invp[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_invp_"+str(i).zfill(2)+".txt")
                self.invr[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_invr_"+str(i).zfill(2)+".txt")
                self.offset[i,:]=numpy.loadtxt("calibration"+self.interface.lensname+"//hyst_offset_"+str(i).zfill(2)+".txt")
            ##memory lenght
            self.memlen=200
            self.x0est=numpy.zeros(7)
            self.in_v_mem=numpy.zeros((self.num_act,self.memlen))
            self.in_t_mem=numpy.zeros(self.memlen)
            self.p_mem=numpy.zeros((self.num_act,self.memlen+1,self.invp.shape[1]))
            self.n=0
        else:
            print "hysteresis calibration not found"
            self.hyst_comp=False

                
            

    def send(self,V_in):
            bytelist=[]
            voltages=numpy.copy(V_in)
        ## limit usb inputs to +-0.8
            voltages[voltages>1.0]=1.0
            voltages[voltages<-0.5]=-0.5
        ## this part is directly translated from c++ code
            for i in range(self.SENT_CHANNELS):
                if (i < self.num_act):
                    temp=int((voltages[i]+1.0)*((1 << (self.DAC_BITS-1))-1))
                    bytelist.append( (temp >> 8) & 0x0F )
                    bytelist.append( temp & 0x00FF )		
                else:
                    bytelist.append( 0x07 )
                    bytelist.append( 0xFF )
                    
            ## send the string to endpoint 0x02
            self.dev.write(0x02,bytelist)



    def compensate_hyst(self,v):
        ##converts desired strokes (measured in voltage) to the correspondent input
        vout=numpy.zeros(self.num_act)
        if self.n<self.memlen:
            self.in_v_mem[:,self.n]=v
            self.in_t_mem[self.n]=time.clock()
            for i in range(self.num_act):
                self.p_mem[i,self.n+1,0]=self.in_v_mem[i,self.n]-self.offset[i,3]
                self.p_mem[i,self.n+1,1:]=numpy.maximum(self.in_v_mem[i,self.n]-self.invr[i,1:]-self.offset[i,3],numpy.minimum(self.in_v_mem[i,self.n]+self.invr[i,1:]-self.offset[i,3],self.p_mem[i,self.n,1:]))
                vout[i]=((-self.offset[i,1]+numpy.sqrt(self.offset[i,1]**2-4*self.offset[i,0]*(self.offset[i,2]-(numpy.dot(self.p_mem[i,:,:],self.invp[i,:])))))/(2*self.offset[i,0]))[self.n+1]
            vout[vout>1.0]=1.0
            vout[vout<-1.0]=-1.0
            self.n+=1 

        else:
            self.in_v_mem=numpy.roll(self.in_v_mem,-1, axis=1)
            self.in_v_mem[:,self.memlen-1]=v
            self.in_t_mem=numpy.roll(self.in_t_mem,-1)
            self.in_t_mem[self.memlen-1]=time.clock()

            self.p_mem=numpy.roll(self.p_mem,-1,axis=1)
            for i in range(self.num_act):
                self.p_mem[i,self.memlen,0]=self.in_v_mem[i,self.memlen-1]-self.offset[i,3]
                self.p_mem[i,self.memlen,1:]=numpy.maximum(self.in_v_mem[i,self.memlen-1]-self.invr[i,1:]-self.offset[i,3],numpy.minimum(self.in_v_mem[i,self.memlen-1]+self.invr[i,1:]-self.offset[i,3],self.p_mem[i,self.memlen-1,1:]))
                vout[i]=((-self.offset[i,1]+numpy.sqrt(self.offset[i,1]**2-4*self.offset[i,0]*(self.offset[i,2]-(numpy.dot(self.p_mem[i,:,:],self.invp[i,:])))))/(2*self.offset[i,0]))[self.memlen]       
            vout[vout>1.0]=1.0
            vout[vout<-1.0]=-1.0

        return vout
               

    def setvoltages(self,volt):
        volt=volt+self.flatvolt


        if not self.hyst_comp:
            self.voltages=volt
        else:
            self.voltages=self.compensate_hyst(volt)
        errors=0
        errors=errors+volt[self.voltages>1.0].size
        errors=errors+volt[self.voltages<-0.5].size
        ## these two lines part should not be necessary due to the send function limitations, but better safe than sorry
        self.voltages[self.voltages<-0.5]=-0.5
        self.voltages[self.voltages>1.0]=1.0

        if errors>0:
            print "Warning: "+str(errors)+" actuators out of range"


        self.send(self.voltages)

        

    def set_hyst_comp(self,newvalue):
        ## a function to enable/disable hysteresis compensation
        self.hyst_comp=newvalue

    def relax(self,total_time=1.0,t=0.005,T=0.025):
        restore_hyst=False
        if self.hyst_comp:
            self.hyst_comp=False
            restore_hyst=True
            
        A_max = 1.0
        A_min = -0.5
        Offset = 0.0

        N = total_time/T

        tau = total_time/5.0

        freq = N/total_time

        A_max_corr = Offset + (A_max-Offset)*numpy.exp(1.0/(4.0*freq*tau))
        A_min_corr = Offset+(A_min-Offset)*numpy.exp(3.0/(4.0*freq*tau))
        A_tot_corr = (A_max_corr-A_min_corr)/2
        shift_corr = (A_max_corr+A_min_corr)/2

        t=time.clock()
        volts=numpy.ones(10)
        while (time.clock()-t<total_time):
            amp = A_tot_corr*numpy.sin(2*numpy.pi*freq*(time.clock()-t))*numpy.exp(-(time.clock()-t)/tau)+(shift_corr-Offset)*numpy.exp(-(time.clock()-t)/tau)+Offset
            self.setvoltages(volts*amp)

        if restore_hyst:
            self.hyst_comp=True
            self.init_hyst()
            




    
    def getzernikes(self):
        ## estimate zernike decomposition of the current corrected wavefront
        return numpy.dot(acttozer,self.voltages)
    

    def getsolovievs(self):
        ## estimate decomposition on the gradient orthogonal base of the current corrected wavefront
        return numpy.dot(acttosol,self.voltages)

    def getvoltages(self):
        ## return current voltages
        return self.voltages

    def setzernikes(self,zer):
        ## set a correction expressed as a Zernike series
        voltages=numpy.zeros(self.num_act)
        for i in range(len(zer)):
            voltages=voltages+zer[i]*self.zervolt[:,i]

        self.setvoltages(voltages)

    def setort(self,ort):
        ## set a correction expressed as a gradient orthogonal series
        voltages=numpy.zeros(self.num_act)
        for i in range(len(ort)):
            voltages=voltages+ort[i]*self.ortbase[:,i]

        self.setvoltages(voltages)


    def addvoltages(self,volt):
        ## add an aberration to the currently corrected one
        self.voltages=self.voltages+volt

        self.setvoltages(self.voltages)

    def addzernikes(self,zer):
        ## add an aberration to the currently corrected one
        for i in range(len(zer)):
            self.voltages=self.voltages+zer[i]*self.zervolt[:,i]*0.3

        self.setvoltages(self.voltages)

    def addort(self,ort):
        ## add an aberration to the currently corrected one
        for i in range(len(ort)):
            self.voltages=self.voltages+ort[i]*self.ortbase[:,i]*0.3

        self.setvoltages(self.voltages)

    def saveflat(self):
        flatvoltfile=open("flatvoltages_"+self.interface.lensname+".poz","wb")
        pickle.dump(self.getvoltages,flatvoltfile)
        flatvoltfile.close()
        
if __name__=="__main__":
    dm=lens(False)
    dm.relax()

    


