import numpy as np, pylab

data = np.loadtxt('gets_center.csv',delimiter=',')
orig = np.loadtxt('parameters.dat',delimiter=',')
data = data[data[:,0].argsort()]

c_bdmv = data[:,4]
c_bdmw = data[:,7]

r_bdmv = data[:,10]
r_bdmw = data[:,11]

rs_bdmv = r_bdmv/c_bdmv
rs_bdmw = r_bdmw/c_bdmw

rs = orig[:,1]

pylab.title('$r_s$')
pylab.plot(rs,rs,'-k')
pylab.plot(rs,rs_bdmv,'ob')
pylab.xlabel('Real')
pylab.ylabel('BDMV')
pylab.savefig('bdmv.png',dpi=300)
pylab.close()

pylab.title('$r_s$')
pylab.plot(rs,rs,'-k')
pylab.plot(rs,rs_bdmw,'or')
pylab.xlabel('Real')
pylab.ylabel('BDMW')
pylab.savefig('bdmw.png',dpi=300)
pylab.close()
