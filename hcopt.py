import numpy
from scipy.optimize import minimize


def lorentzres(pars,lb,ub,vals):
    xvals=numpy.linspace(lb,ub,vals.shape[0])
    yvals=pars[0]*(1.0/(numpy.pi*pars[2])*pars[2]**2/(pars[2]**2+(xvals-pars[3])**2))+pars[1]

    return numpy.sqrt(numpy.mean((yvals-vals)**2))


class optimizer():
    def __init__(self,startvect,N,n_steps,d,lb,ub):
        self.optimum=startvect
        self.N=N
        self.n=0
        self.ab=lb[0]
        self.lb=lb
        self.ub=ub
        self.c=0
        self.d=d
        self.n_steps=n_steps
        self.vals=numpy.zeros(self.n_steps)
        
    def step(self,function):
        v=numpy.copy(self.optimum)
        v[self.n]=self.ab
        self.vals[self.c]=function(v)
        self.ab+=(self.ub[self.n]-self.lb[self.n])/(self.n_steps-1)
        self.c+=1

        if self.c==self.n_steps:
##            p0=numpy.asarray([numpy.max(self.vals),numpy.min(self.vals),self.ub[self.n],numpy.argmax(self.vals)*((self.ub[self.n]-self.lb[self.n])/(self.n_steps-1))+self.lb[self.n]])
##            b=[(0.0,None),(None,None),(0.0000001,None),(self.lb[self.n],self.ub[self.n])]
##            pars=minimize(lorentzres,p0,args=(self.lb[self.n],self.ub[self.n],self.vals),bounds=b)['x']
            xvals=numpy.linspace(self.lb[self.n],self.ub[self.n],self.vals.shape[0])
            p=numpy.polyfit(xvals,self.vals,2, full=False)
##            simdata=pars[0]*(1/(numpy.pi*pars[2])*pars[2]**2/(pars[2]**2+(xvals-pars[3])**2))+pars[1]
            self.optimum[self.n]=-pars[1]/(2.0*pars[0])
            self.n+=1
            if self.n<self.d:
                self.ab=self.lb[self.n]
            else:
                self.n=0
                self.ab=self.lb[0]
            self.c=0

    def getmax(self):
        return self.optimum

if __name__=="__main__":
    A=20.0
    off=-1.0
    x0s=(numpy.random.random(12)-0.5)
    amps=(numpy.random.random(12)*4.0)
          
    def ndimlor(x):
        val=0.0
        for i in range(12):
            val+=1.0/12.0*(A/(numpy.pi*amps[i])*amps[i]**2/(amps[i]**2+(x[i]-x0s[i])**2)+off)
        return val

    

    opt=optimizer(numpy.random.random(12)-0.5,3000,100,12,-numpy.ones(12),numpy.ones(12))

    for i in range(3000):
        opt.step(ndimlor)
        print numpy.sqrt(numpy.mean((opt.getmax()-x0s)**2))
        


    
