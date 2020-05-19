from PyDAQmx import *
import numpy
import time

##-----------------------------------------------------------------------
## A module sending and receiving triggers through obscure DAQmx functions
##-----------------------------------------------------------------------  

class triggerIO():

    def __init__(self):

## The maximum time the software will wait for an incoming trigger
        self.timeout=5.0
        self.taskHandleout=TaskHandle()
        self.taskHandlein=TaskHandle()

        self.data0=numpy.ndarray(shape=(1),buffer=numpy.array([0]),dtype=numpy.uint8)
        self.data1=numpy.ndarray(shape=(1),buffer=numpy.array([1]),dtype=numpy.uint8)
        self.datain=numpy.ndarray(shape=(1),buffer=numpy.array([1]),dtype=numpy.uint8)

        self.a=c_ulong()

        DAQmxCreateTask("",byref(self.taskHandleout))
        DAQmxCreateTask("",byref(self.taskHandlein))


## The string specifies the connectors used on the DAQ board for input and output.
## Check the manual of your DAQ if you need to change these parameters (it's not)
## as easy as it looks.
        DAQmxCreateDOChan(self.taskHandleout,"Dev1/port1/line7","output",DAQmx_Val_ChanPerLine)
        DAQmxCreateCICountEdgesChan(self.taskHandlein,"Dev1/ctr0","input",DAQmx_Val_Falling,0,DAQmx_Val_CountUp)


        DAQmxStartTask(self.taskHandleout)
        DAQmxStartTask(self.taskHandlein)

        DAQmxWriteDigitalLines(self.taskHandleout,1,1,10.0,DAQmx_Val_ChanPerLine,self.data0,None,None)
        time.sleep(0.001)    


    def sendTrigger(self):
        DAQmxWriteDigitalLines(self.taskHandleout,1,1,10.0,DAQmx_Val_ChanPerLine,self.data0,None,None)
        time.sleep(0.001)
        DAQmxWriteDigitalLines(self.taskHandleout,1,1,10.0,DAQmx_Val_ChanPerLine,self.data1,None,None)
        time.sleep(0.001)
        DAQmxWriteDigitalLines(self.taskHandleout,1,1,10.0,DAQmx_Val_ChanPerLine,self.data0,None,None)


    def waitForTrigger(self):
        check=0
        waittime=time.clock()
        while check==0:
            data=DAQmxReadCounterScalarU32(self.taskHandlein,10.0,self.a,None)
            if self.a.value!=0 or time.clock()-waittime>self.timeout:
                DAQmxStopTask(self.taskHandlein)
                DAQmxStartTask(self.taskHandlein)
                check=1
class dummytrigger():

    def __init__(self):

## The maximum time the software will wait for an incoming trigger
        time.sleep(0.005)    


    def sendTrigger(self):
        time.sleep(0.016)


    def waitForTrigger(self):
        time.sleep(0.016)

if __name__=='__main__':
    trig=triggerIO()
    for i in range(20):
        trig.waitForTrigger()
        print "trigger received"
