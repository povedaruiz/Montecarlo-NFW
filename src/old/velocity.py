import numpy as np, pylab, math, sys, timeit, os, random, datetime, nfw, mcmc,fit , plotter, multiprocessing, time
from scipy.optimize import fsolve

# Gets the concentration and virial radius for several haloes

config = open('config.div','r').readline().split(',')
config[-1] = config[-1].replace('\n','')

processes = int(config[5])
now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
mass_element = 1.0   
plt = 1
total_list = os.listdir(str(config[0]))
len_list = len(total_list)
lists = [total_list[i*len_list // processes: (i+1)*len_list //processes] for i in range(processes)]
jobs = []

if (config[7]=='0'):
    print 'Plotting mode disabled'
    plt = 0
else:
    print 'Plotting mode enabled'
    plt = 1

if config[8]=='0':
    print 'Test mode disabled'
else:
    print 'Test mode enabled'

os.system('mkdir vlct_'+now)
sys.stdout.write('\rCompiling the code used to calculate the center of each halo... ')
sys.stdout.flush()
os.system('cc potential.c -lm -o  potential.out')
sys.stdout.write('Done\n')

def run(directories,process_number):

    process_number+=1
    count = 0
    filename_export = './vlct_'+now+'/results_'+str(process_number)+'.csv'
    os.system('touch '+filename_export)

    for filename in directories:

        count = count + 1
        print '\rWorking with file '+str(count)+' of '+str(len(directories))+' in process '+str(process_number)

    # Creates the "data" array with the information from the file in "path"
        path = os.path.expanduser(str(config[0])+'/'+filename)
        data = np.loadtxt(open(path, 'r'), delimiter=",",skiprows=int(config[4]))

    # Gets the cartesian coordinates for each particle in the halo and the number of particles
        x = data[:,int(config[1])]
        y = data[:,int(config[2])]
        z = data[:,int(config[3])]
        n_points = len(x)

    # Exports a file with the cartesian coordinates of each particle
        file_id = int(filename.split('_')[1])
        positions_name ='positions_'+str(file_id)+'.dat'
        potential_name ='potential_'+str(file_id)+'.dat'
        results_folder ='./vlct_'+now+'/'+str(file_id)
        open(positions_name, "w").write('\n'.join('%lf,%lf,%lf' % (x[i],y[i],z[i]) for i in range(n_points)))

    # Runs the executable "potential.out" that will get the potential energy for each particle
        os.system('./potential.out '+positions_name+' '+potential_name)

    # Finds the particle with the lowest potential and puts it as the new origin
        potential = np.loadtxt(open(potential_name, 'r'))
        maximum = np.argmax(potential)
        x_center,y_center,z_center = x[maximum],y[maximum],z[maximum]

    # Gets the radial distance from the new origin to each particle and sorts it
        r_values = np.sort(np.sqrt((x-x_center)**2 + (y-y_center)**2 + (z-z_center)**2), kind='quicksort')
    
    # Removes the files used by "potential.out"
        os.system('rm '+potential_name+' '+positions_name)

    # Gets the mass for each radius and removes the particle in the origin
        mass = mass_element*np.arange(1,n_points,1)
        radius = np.delete(r_values,0)

    # Gets the average density in function of the radius
        avg_density = mass/((4.0/3.0)*np.pi*(radius**3))
        rho_back = mass_element*(2048.0/1000.0)**3

    # Gets the virial radius
        if config[8]=='0':
            crit = 740.0
            vir_index = np.argmin(np.abs(avg_density-crit*rho_back))

            if np.argmin(np.abs(avg_density-crit*rho_back)) > 1:
                r_vir = radius[vir_index]
            else:
                r_vir = radius[-1]
                vir_index = len(avg_density)-1
        else:
            r_vir = radius[-1]
            vir_index = len(avg_density)-1
            
    # Removes the particles that have a greater radius than the virial radius
        mass = np.resize(mass,vir_index+1)
        radius = np.resize(radius,vir_index+1)

    # Normalizes the mass and radius
        mass = mass/mass[-1]
        radius = radius/radius[-1]

    # Calculates the velocity and finds its maximum
        velocity = np.sqrt(mass/radius)
        v_max = np.max(velocity)
    # Defines the relation between the concentration and the greatest velocity
        def f(c):
            return v_max - np.sqrt(0.216*c/(np.log(1+c)-c/(1+c)))

    # Finds the concentration using f solve
        c = fsolve(f,10.0)

    # Generates plots
        if (plt == 1):

            os.system('mkdir '+results_folder)
            os.chdir(results_folder)

            pylab.plot(radius/radius[-1],velocity/velocity[-1],'.k')
            pylab.plot(radius/radius[-1],np.sqrt(nfw.mass_norm(radius/radius[-1],c)/(radius/radius[-1])),'-r')
            pylab.xlabel('$r_{norm}$')
            pylab.ylabel('$v_{norm}$')
            pylab.savefig('velocity_'+str(filename)+'.pdf',dpi=200)
            pylab.close()

            os.chdir('../../')
            
    # Writes the results for the halo
        export = open(filename_export, 'a')
        line = [[file_id,x_center,y_center,z_center,c,f(c),r_vir,len(mass)+1,n_points]]
        np.savetxt(export,line,fmt=['%d','%lf','%lf','%lf','%lf','%lf','%lf','%d','%d'],delimiter=',')

for i in range(processes):
    p = multiprocessing.Process(target=run, args=(lists[i],i))
    jobs.append(p)
    p.start()
