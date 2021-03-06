### residual stress calculation
import matplotlib.pyplot as plt
import numpy as np
from MP.mat import mech
from MP import read_blocks
rb=read_blocks.main
FlowCurve = mech.FlowCurve
cos = np.cos
sin = np.sin
pi  = np.pi
def reader(fn='igstrain_load_ph1.out',isort=False,icheck=False):
    if isort: from MP.ssort import sh as sort
    dl = open(fn).readlines()
    npb = dl[1].split()[0]
    dl = dl[2:]
    print npb
    ds = open(fn).read()
    d = ds.split('npb')[1]
    #d = np.loadtxt(fn,skiprows=2).T
    d = rb(fn,skiprows=2)

    steps = np.unique(d[0])
    nstp = len(steps)

    #phis = np.unique(d[1]) # this shoudn't sort...
    phis=[]
    for i in range(len(d[1])):
        pp = d[1][i]
        if pp in phis: pass
        else: phis.append(pp)

    phis = np.array(phis)
    nphi = len(phis)
    psis = []

    for i in range(len(dl)):
        d = dl[i].split()
        st, ph, beta, psi1, psi2 = map(float, [d[0], d[1], d[2], d[3], d[4]])
        if ph!=phis[0]: break
        psis.append(psi1)
        psis.append(psi2)

    psis   = np.array(psis); npsis  = len(psis)
    epshkl = np.zeros((nstp,nphi,npsis))
    ngr    = np.zeros((nstp,nphi,npsis))
    v      = np.zeros((nstp,nphi,npsis))
    steps  = np.zeros((nstp))
    il = 0
    for istp in range(nstp):
        for iphi in range(nphi):
            for ibeta in range(npsis/2):
                il = ibeta + iphi*npsis/2 + nphi*npsis/2*istp
                dat = map(float,dl[il].split())
                steps[istp] = dat[0]
                psi1, psi2 = dat[3],dat[4]
                eps1, eps2 = dat[5],dat[6]
                n1, n2 = dat[9],dat[10]
                v1, v2 = dat[11],dat[12]
                epshkl[istp,iphi,ibeta*2]   = eps1
                epshkl[istp,iphi,ibeta*2+1] = eps2
                ngr[istp,iphi,ibeta*2]   = n1
                ngr[istp,iphi,ibeta*2+1] = n2
                v[istp,iphi,ibeta*2]   = v1
                v[istp,iphi,ibeta*2+1] = v2

    if isort:
        # phi sort
        ph = phis.copy()
        # ph.sort()
        if not(all(phis==ph)):
            print phis
            print ph
            phis = ph
            print 'Data along phi should be rearranged'
            for istp in range(nstp):
                for ipsi in range(npsis):
                    ep = epshkl[istp,:,ipsi]
                    ng = ngr[istp,:,ipsi]
                    vv = v[istp,:,ipsi]
                    ph, ep, ng, vv = sort(phis,ep,ng,vv)

                    epshkl[istp,:,ipsi] = ep[:,ipsi]
                    ngr[istp,:,ipsi] = ng[:,ipsi]
                    v[istp,:,ipsi] = vv[:,ipsi]
        else: pass

        # psi sort
        ps = psis.copy()
        ps.sort()
        if not(all(psis==ps)):
            # print psis
            # print ps
            print 'Data along psi should be rearranged'
            for istp in range(nstp):
                for iphi in range(nphi):
                    ep = epshkl[istp,iphi,:]
                    ng = ngr[istp,iphi,:]
                    vv = v[istp,iphi,:]

                    dum, ep, ng, vv = sort(psis,ep,ng,vv)

                    epshkl[istp,iphi,:] = ep[:]
                    ngr[istp,iphi,:] = ng[:]
                    v[istp,iphi,:] = vv[:]
            psis=ps
        else:pass

    if icheck:
        plt.plot(psis,epshkl[-3,0,:])
        plt.plot(psis,epshkl[-2,0,:])
        plt.plot(psis,epshkl[-1,0,:])

        plt.plot(psis,epshkl[-3,1,:])
        plt.plot(psis,epshkl[-2,1,:])
        plt.plot(psis,epshkl[-1,1,:])

    return psis, phis, epshkl, ngr, v, steps

def read_exp(fn='Bsteel_BB_00.txt',path='rs'):
    """
    return sorted experimental results
    """
    from os import sep
    from glob import glob
    from plot_sin2psi import read as read
    from MP.ssort import sh as sort

    paths = '%s%s'%(path,sep)

    files = np.loadtxt('%s%s'%(paths,fn),skiprows=2,dtype='str')

    nstp = len(files)
    fns,ex,ey = [], [], []
    fs = glob('%s%s*.txt'%(paths,files[0][0]))
    fs.sort() # sorted ...
    nphi = len(fs); phis = []
    for i in range(nphi):
        phis.append(float(fs[i].split('Phi')[1].split('.')[0]))
        sin2psi,ehkl,dspacing,psi = read(fs[i])
        npsi = len(psi)
    psis = psi
    ehkl = np.zeros((nstp,nphi,npsi))
    dhkl = np.zeros((nstp,nphi,npsi))
    strain = np.zeros((2,nstp))

    for i in range(len(files)):
        e_xx, e_yy = float(files[i][1]), float(files[i][2])
        fns.append(files[i][0])
        ex.append(e_xx); ey.append(e_yy)
        fs = glob('%s%s*.txt'%(paths,fns[i]))
        strain[0,i] = e_xx
        strain[1,i] = e_yy
        dum = []
        for iphi in range(len(fs)):
            sin2psi, eps, ds, ps = read(fs[iphi])
            dum.append(eps)
            x,y = sort(ps,eps)
            ehkl[i,iphi,:] = y
            x,y, = sort(ps,ds)
            dhkl[i,iphi,:] = y

    psi = x
    psi  = np.array(psi)
    phis = np.array(phis)
    ehkl = np.array(ehkl)
    strain = np.array(strain)
    return phis,psi,ehkl,dhkl,strain

# def __check_power_law_fit__():
#     fig=plt.figure(1);ax=fig.add_subplot(111)
#     x = np.linspace(1,10,10)
#     y = np.cos(-x**2/8.0)

#     ax.plot(x,y,'s',label='data')
#     new_x = np.linspace(1,10,1000)
#     y_lin = interpolate(new_x,x,y,iopt=1)
#     ax.plot(new_x,y_lin,'--',label='NN')

#     xlog = np.log(x)
#     ylog = np.log(y)

#     fig=plt.figure(2);ax=fig.add_subplot(111)
#     ax.plot(xlog,ylog)

#     z = np.polyfit(xlog,ylog,1)

#     print z
#     # f = np.poly1d(z)

def __check_interpolate__():
    fig=plt.figure();ax=fig.add_subplot(111)
    x = np.linspace(2,9,10)
    y = np.cos(-x**2/8.0)

    ax.plot(x,y,'s',label='data')

    new_x = np.linspace(1,10,1000)

    y_nn = interpolate(new_x,x,y,iopt=0)
    y_near = interpolate(new_x,x,y,iopt=1)
    y_cub = interpolate(new_x,x,y,iopt=2)
    y_qud = interpolate(new_x,x,y,iopt=3)
    y_L = interpolate(new_x,x,y,iopt=4)
    y_poly2 = interpolate(new_x,x,y,iopt=5)
    y_poly3 = interpolate(new_x,x,y,iopt=6)
    ## y_power = interpolate(new_x,x,y,iopt=7)
    y_zero = interpolate(new_x,x,y,iopt=8)
    y_slinear = interpolate(new_x,x,y,iopt=9)

    ax.plot(new_x,y_nn,'-',label='piece-wise linear')
    ax.plot(new_x,y_near,'--',label='Assign nearest')
    ax.plot(new_x,y_cub,'--',label='Cubic')
    ax.plot(new_x,y_qud,'--',label='Qudratic')
    # ax.plot(new_x,y_zero,'--',label='Zero')
    # ax.plot(new_x,y_slinear,'-',label='Slinear')
    ax.plot(new_x,y_L,'--',label='L')
    # # ax.plot(new_x,y_poly2,'--',label='Poly2')
    # # ax.plot(new_x,y_poly3,'--',label='Poly3')
    ## ax.plot(new_x,y_power,'--',label='Power')

    ax.legend(loc='best',fancybox=True,
              ncol=2).get_frame().set_alpha(0.5)

    fig.savefig('fitting_ref.pdf')
    pass

def interpolate(xs,xp,fp,iopt=0):
    """
    Various interpolation methods
    Default is 'nearest-neighbour interpolation'.
    Using NumPy's generic interp function,
    'piecewise linear interpolation'

    In case data is located beyond the bounds,
    simply use the two last ending data points to
    linearly extrapolate.

    Choice of interpolation method
      0: Piece wise linear (Linear intp by nearest neighbours)
      1: Assign nearest data (nearest)
      2: Cubic
      3: Quadratic
      4: Linear fit
      5: Poly2
      6: Poly3
      7: Left for power law fit?
      8: zero
      9: slinear

    Arguments
    =========
    xs
    xp
    fp
    iopt = 0

    (xp,fp) : given data
    """
    from scipy.interpolate import interp1d

    y_left=[]; y_right=[]
    if any(xs[i]<xp[0] or xs[i]>xp[-1]
           for i in range(len(xs)))\
               and iopt!=7 and iopt!=4:
        # print 'Part of the array should be',
        # print 'exptrapolated.'

        indices = []
        xs_within = []; left=[]; right=[]
        for i in range(len(xs)):
            if not(xs[i]<xp[0] or xs[i]>xp[-1]):
                xs_within.append(xs[i])

            if xs[i]<xp[0]:
                left.append(xs[i])
            elif xs[i]>xp[-1]:
                right.append(xs[i])

        ## left
        if len(left)>0:
            x=xp[0:2]
            y=fp[0:2]
            z=np.polyfit(x,y,1)
            f_lin = np.poly1d(z)
            y_left = f_lin(left)

        ## right
        if len(right)>0:
            x=xp[::-1][0:2][::-1]
            y=fp[::-1][0:2][::-1]
            z=np.polyfit(x,y,1)
            f_lin = np.poly1d(z)
            y_right = f_lin(right)

        ## assigning only x points within the bounds
        ## for "interpolation"
        xs = xs_within[::]

    # print y_left
    # print y_right
    # raise IOError


    if len(xp)!=len(fp): raise IOError, \
       'len(xp) should be equal to len(fp)'
    if not (np.all(np.diff(xp)>=0)):
        raise ValueError, \
            'xp is not monotonically increasing'

    if iopt==0:
        # piece-wise linear (nearest neightbour)
        f= interp1d(xp,fp,'linear')
    elif iopt==1:
        # assign nearest value
        f = interp1d(xp,fp,'nearest')
    elif iopt==2:
        f = interp1d(xp,fp,'cubic')
    elif iopt==3:
        f = interp1d(xp,fp,'quadratic')
    elif iopt==4:
        z = np.polyfit(xp,fp,1)
        f = np.poly1d(z)
    elif iopt==5:
        z = np.polyfit(xp,fp,2)
        f = np.poly1d(z)
    elif iopt==6:
        z = np.polyfit(xp,fp,3)
        f = np.poly1d(z)
    elif iopt==7:
        raise IOError, 'Not completed.'
        # x_dat = xp[::]
        # xp = np.log(xp)
        # fp = np.log(fp)
        # z = np.polyfit(xp,fp,1)
        # f = np.poly1d(z)
    elif iopt==8:
        f = interp1d(xp,fp,'zero')
    elif iopt==9:
        f = interp1d(xp,fp,'slinear')
    else:
        raise IOError, 'Unexpected iopt given'

    try: y = f(xs)
    except ValueError:
        print 'Error occured'
        raise IOError

    Y=[]
    for i in range(len(y_left)):
        Y.append(y_left[i])
    for i in range(len(y)):
        Y.append(y[i])
    for i in range(len(y_right)):
        Y.append(y_right[i])

    return Y

def u_gaussian(epshkl,sigma=5e-5):
    return np.random.normal(0.,sigma) + epshkl

def u_epshkl(e,sigma=5e-5):
    a=[]
    for i in range(len(e)):
        d = u_gaussian(e[i],sigma)
        a.append(d)
    return a

def __torad__(*args):
    newarray = []
    for a in args:
        newarray.append(a*pi/180.)
    return newarray

def __todegree__(*args):
    newarray = []
    for a in args:
        newarray.append(a*180./pi)
    return newarray

def __deco__(ax,ft=15,iopt=0,ij=None):
    """
    """
    if iopt==0:
        ax.set_xlabel(r'$\sin^2{\psi}$',dict(fontsize=ft))
        ax.set_ylabel(r'$\varepsilon^{\mathrm{hkl}}$',
                      dict(fontsize=ft))
    if iopt==1:
        ax.set_xlabel(r'$\sin^2{\psi}$',dict(fontsize=ft))
        if ij==None:
            label = r'$F_{ij}$'
        else:
            label = r'$F_{%i%i}$'%(
                ij[0],ij[1])
        ax.set_ylabel(label,dict(fontsize=ft))
        #ax.set_ylim(-2,2)

    if iopt==2:
        ax.set_xlabel(r'$\sin^2{\psi}$',dict(fontsize=ft))
        ax.set_ylabel(r'$\varepsilon_{\mathrm{IG}}^{\mathrm{hkl}}$',
                      dict(fontsize=ft))
    if iopt==3:
        ax.set_xlabel(r'$\bar{E}^{\mathrm{eff}}$',dict(fontsize=ft))
        ax.set_ylabel(r'$\bar{\Sigma}^{\mathrm{eff}}$',dict(fontsize=ft))
    ax.grid('on')

# coefficients for isotropic samples...
def a(phi,psi,s1,s2): return 0.5 * s2 * cos(phi)**2 * sin(psi)**2 + s1 # s11
def b(phi,psi,s1,s2): return 0.5 * s2 * sin(phi)**2 * sin(psi)**2 + s1 # s22
def c(phi,psi,s1,s2): return 0.5 * s2 * cos(psi)**2 + s1               # s33
def d(phi,psi,s1,s2): return 0.5 * s2 * sin(2*phi) * sin(psi)**2       # s12
def e(phi,psi,s1,s2): return 0.5 * s2 * cos(phi) * sin(2*psi)          # s13
def f(phi,psi,s1,s2): return 0.5 * s2 * sin(phi) * sin(2*psi)          # s23

class DiffDat:
    """
    Standard diffraction class that can work for both
    the experimental and simulative sets of diffraction
    data obtained either by proto or by EVPSC.
    """
    def __init__(self,
                 phi=None,
                 psi=None,
                 sf=None,
                 ig=None,
                 ehkl=None,
                 dhkl=None,name=None,
                 strain=None,
                 stress=None,
                 vf=None,ngr=None,
                 *args
                 ):
        """
        Complete data structure for a set of data for
        diffraction-based stress analysis.
        The key objects that require are:
        1) stress factor
        2) Intergranular strain
        3) Lattice strain
        4) Macro strain at which the 'unknown' stress
               will be found based on the mentioned
               1), 2) and 3) elements.

        sf (nstp, k, nphi,npsi)
        ig (nstp, nphi, npsi)
        ehkl (nstp, nphi,npsi)
        strain (nstp,6)
        vf (nstp,nphi,npsi)

        ** We follow Hauk's convention for stress components
        ----------------------------------------------------
           i  ij in (Voigt)    or     (Hauk)
           0         (1,1)             (1,1)
           1         (2,2)             (2,2)
           2         (3,3)             (3,3)
           3         (2,3)             (1,2)
           4         (1,3)             (1,3)
           5         (1,2)             (2,3)
        """
        self.ijh = [[1,1],[2,2],[3,3],[1,2],[1,3],[2,3]]
        self.ijv = [[1,1],[2,2],[3,3],[2,3],[1,3],[1,2]]
        self.nstp = None
        self.sf=sf
        self.ig=ig
        self.ehkl=ehkl
        self.dhkl=dhkl
        self.vf=vf
        self.ngr=np.array(ngr,dtype='int')

        if type(self.vf)==type(None):
            self.vf = np.zeros(self.ehkl.shape)*np.nan
        if type(self.ngr)==type(None):
            self.ngr = np.zeros(self.ehkl.shape)*np.nan

        if type(sf)!=type(None): self.nstp = len(sf) # (nstp,k,nphi,npsi)
        if type(ig)!=type(None): self.nstp = len(ig) # (nstp,k,nphi,npsi)
        if type(ehkl)!=type(None): self.nstp = len(ehkl) # (nstp,k,nphi,npsi)
        if type(dhkl)!=type(None): self.nstp = len(dhkl) # (nstp,k,nphi,npsi)

        self.stress=stress
        self.strain = np.array(strain).copy()

        self.flow = FlowCurve()
        self.flow.get_6stress(stress.T)
        self.flow.get_6strain(strain.T)

        self.strain_eff = self.strain.T[0]+self.strain.T[1]
        #self.flow.get_eqv()
        #self.strain_eff = self.flow.epsilon_vm

        self.phi=phi; self.psi=psi
        self.nphi = len(self.phi)
        self.npsi = len(self.psi)
        self.name=name
        self.ndat = self.nphi*self.npsi

        if self.nstp!=None: nstp = self.nstp
        nphi = self.nphi
        npsi = self.npsi

        if self.sf!=None and nstp!=None:
            if (nstp,6,nphi,npsi) != sf.shape:
                raise IOError, 'SF is not in right structure'
        if self.ig!=None and nstp!=None:
            if (nstp,nphi,npsi) != ig.shape:
                raise IOError, 'IG is not in right structure'
        if self.ehkl!=None and nstp!=None:
            if (nstp,nphi,npsi) != ehkl.shape:
                raise IOError, 'ehkl is not in right structure'
        if self.dhkl!=None and nstp!=None:
            if (nstp,nphi,npsi) != dhkl.shape:
                raise IOError, 'ehkl is not in right structure'

    def interp_psi(self,psi,iopt=1):
        """
        interpolate with respect to psi

        iopt=0: interpolate along psi
        iopt=1: interpolate along +- sin(psi)**2
        """
        from numpy import sign
        nstp = self.nstp
        nphi = self.nphi
        npsi_new = len(psi)
        x = np.array(psi).copy() # or sin(psi)**2 +- sign should be attached...
        x0 = self.psi
        if iopt==1:
            x = sign(x) * sin(x)**2
            x0 = sign(x0) * sin(x0)**2

        if self.sf!=None:
            sf_new = np.zeros((nstp,6,nphi,npsi_new))
            for istp in range(nstp):
                for iphi in range(nphi):
                    for k in range(6):
                        y = self.sf[istp,k,iphi,:]
                        sf_new[istp,k,iphi,:] = \
                            interpolate(x,x0,y)
        if self.ig!=None:
            ig_new = np.zeros((nstp,nphi,npsi_new))
            for istp in range(nstp):
                for iphi in range(nphi):
                    y = self.ig[istp,iphi,:]
                    ig_new[istp,iphi,:] = \
                        interpolate(x,x0,y)
        if self.ehkl!=None:
            ehkl_new = np.zeros((nstp,nphi,npsi_new))
            for istp in range(nstp):
                for iphi in range(nphi):
                    y = self.ehkl[istp,iphi,:]
                    ehkl_new[istp,iphi,:] = \
                        interpolate(x,x0,y)
        if self.dhkl!=None:
            dhkl_new = np.zeros((nstp,nphi,npsi_new))
            for istp in range(nstp):
                for iphi in range(nphi):
                    y = self.dehkl[istp,iphi,:]
                    dhkl_new[istp,iphi,:] = \
                        interpolate(x,x0,y)

        if self.sf!=None:
            self.sf = sf_new.copy()
        if self.ig!=None:
            self.ig = ig_new.copy()
        if self.ehkl!=None:
            self.ehkl = ehkl_new.copy()
        if self.dhkl!=None:
            self.dhkl = dhkl_new.copy()

        self.psi = np.array(psi).copy()
        self.npsi = len(self.psi)

    def interp_strain(self,strain):
        """
        Interpolate with respect to the given strains
        """
        ijh = self.ijh
        strain = np.array(strain).copy()
        nstp_new = len(strain)
        print 'nstp_new:', nstp_new
        nphi = self.nphi
        npsi = self.npsi
        x = strain.T[0]+strain.T[1] # effective strain (thickness strain)

        if self.sf!=None:
            sf_new = np.zeros((nstp_new,6,nphi,npsi))
            for k in range(6):
                for iphi in range(nphi):
                    for ipsi in range(npsi):
                        y = self.sf[:,k,iphi,ipsi].copy()
                        sf_new[:,k,iphi,ipsi] = \
                            interpolate(x,self.strain_eff,y)
        if self.ehkl!=None:
            ehkl_new = np.zeros((nstp_new,nphi,npsi))
            for iphi in range(nphi):
                for ipsi in range(npsi):
                    y = self.ehkl[:,iphi,ipsi].copy()
                    ehkl_new[:,iphi,ipsi] = \
                        interpolate(x,self.strain_eff,y)
        if self.dhkl!=None:
            dhkl_new = np.zeros((nstp_new,nphi,npsi))
            for iphi in range(nphi):
                for ipsi in range(npsi):
                    y = self.dhkl[:,iphi,ipsi].copy()
                    dhkl_new[:,iphi,ipsi] = \
                        interpolate(x,self.strain_eff,y)
        if self.ig!=None:
            ig_new = np.zeros((nstp_new,nphi,npsi))
            for iphi in range(nphi):
                for ipsi in range(npsi):
                    y = self.ig[:,iphi,ipsi].copy()
                    ig_new[:,iphi,ipsi] = \
                        interpolate(x,self.strain_eff,y)

        self.strain = np.array(strain).copy()
        self.strain_eff= self.strain.T[0]+self.strain.T[1]
        self.nstp=len(self.strain)

        if self.sf!=None: self.sf=sf_new.copy()
        if self.ehkl!=None: self.ehkl=ehkl_new.copy()
        if self.dhkl!=None: self.dhkl=dhkl_new.copy()
        if self.ig!=None: self.ig=ig_new.copy()

    def determine_phis(self,phi_new):
        """
        Rearrange SF/ehkl/IG for the given phis
        """
        deg = 180./pi
        nphi = self.nphi
        npsi = self.npsi
        nstp = self.nstp
        phi_old  = self.phi.tolist()
        nphi_new = len(phi_new)
        ind = []
        for i in range(len(phi_new)):
            try:
                j = phi_old.index(phi_new[i])
            except ValueError:
                print i
                print 'Mirror?'
                print 'Is this okay to set -phi = phi?'
                j = phi_old.index(abs(phi_new[i]))
                print 'Warning!!!> Go ahead only',
                print ' if you know what you are getting to'
                ind.append(j)
            else: ind.append(j)

        print np.array(phi_new)*deg
        print np.array(phi_old)*deg
        sf_new = np.zeros((nstp,6,nphi_new,npsi))
        ehkl_new = np.zeros((nstp,nphi_new,npsi))
        dhkl_new = np.zeros((nstp,nphi_new,npsi))
        ig_new = np.zeros((nstp,nphi_new,npsi))
        for i in range(len(ind)):
            if self.sf!=None:
                sf_new[:,:,i,:] = self.sf[:,:,ind[i],:]
            if self.ehkl!=None:
                ehkl_new[:,i,:] = self.ehkl[:,ind[i],:]
            if self.dhkl!=None:
                dhkl_new[:,i,:] = self.dhkl[:,ind[i],:]
            if self.ig!=None:
                ig_new[:,i,:] = self.ig[:,ind[i],:]

        if self.sf!=None: self.sf = sf_new.copy()
        if self.ehkl!=None: self.ehkl = ehkl_new.copy()
        if self.dhkl!=None: self.dhkl = dhkl_new.copy()
        if self.ig!=None: self.ig = ig_new.copy()

        self.phi = np.array(phi_new)
        self.nphi = len(self.phi)

    def mask_vol(self):
        """
        Mask data in case that volume (ngr) is zero
        This method may be useful for model data
        """
        if (self.ngr[::]!=0).all():
            return
        else:
            print 'Vol=0 found:'
            for i in range(self.nstp):
                for j in range(self.nphi):
                    for k in range(self.npsi):
                        if self.ngr[i,j,k]==0:
                            #print i,j,k
                            self.mask(istp=i,iphi=j,ipsi=k)

    def mask_vol_margin(self,pmargin):
        """
        Mask grains whose volume is lower than
        a critical margin

        Arguments
        =========
        pmargin = 0.1 (discard 10% below)
        """
        for istp in range(self.nstp):
            ## find average volume for each nstp
            for iphi in range(self.nphi):
                npsi = 0; vf_tot = 0.
                for ipsi in range(self.npsi):
                    if self.vf[istp,iphi,ipsi]>0 and\
                       not(np.isnan(self.vf[istp,iphi,ipsi])):
                        npsi = npsi + 1
                        vf_tot = vf_tot + self.vf[istp,iphi,ipsi]
                vf_mean = vf_tot / npsi
                margin = vf_mean * pmargin
                for ipsi in range(self.npsi):
                    if self.vf[istp,iphi,ipsi]<margin \
                       and not(np.isnan(self.vf[istp,iphi,ipsi])):
                        self.mask(istp,iphi,ipsi)

    def mask(self,istp,iphi,ipsi):
        """
        Mask for the given psi angles at particular deformation

        1) This is to delete the cases where no volume fraction
        is obtained as a result of severe texture development
        2) It can be also used for a parametric study, for which
         data from a certain psi are removed.
        """
        self.sf[istp,:,iphi,ipsi]=np.nan
        self.ig[istp,iphi,ipsi]=np.nan
        self.ehkl[istp,iphi,ipsi]=np.nan

        self.sf=np.ma.array(self.sf)
        self.ig=np.ma.array(self.ig)
        self.ehkl=np.ma.array(self.ehkl)

    def plot(self,ifig=1):
        from plt_lib import setFigLinesBW as figbw
        ijh = self.ijh
        deg = 180/pi
        nphi = self.nphi
        nspi = self.npsi
        nstp = len(self.strain)
        x = sin(self.psi)**2
        if self.sf!=None:
            fig_sf = plt.figure(ifig,figsize=(16,9))
            ax_sf =[]
            for iphi in range(nphi):
                for k in range(6):
                    ax=fig_sf.add_subplot(6,nphi,k*nphi+iphi+1)
                    if k==0: ax.set_title(r'$\phi=$%4.1f'%
                                          (self.phi[iphi]*deg))
                    ax.grid('on')
                    ax.locator_params(nbins=4)
                    ax_sf.append(ax)
                    __deco__(ax=ax,iopt=1,ft=15,ij=ijh[k])
                    for istp in range(nstp):
                        y = self.sf[istp,k,iphi,:]
                        ax.plot(x,y*1e6,'-x')
            #figbw(fig_sf) # make'em BW style
            fig_sf.tight_layout()

        if self.ehkl!=None:
            fig_ehkl = plt.figure(ifig+1,figsize=(16,4))
            ax_ehkl=[]
            for iphi in range(nphi):
                ax=fig_ehkl.add_subplot(1,nphi,iphi+1)
                ax.grid('on')
                ax.locator_params(nbins=4)
                ax_ehkl.append(ax)
                __deco__(ax=ax,iopt=0)
                for istp in range(nstp):
                    y = self.ehkl[istp,iphi,:]
                    ax.plot(x,y*1e3)
                    if istp==0: ax.set_title(r'$\phi=$%4.1f$^\circ$'%
                                             (self.phi[iphi]*deg))
            fig_ehkl.tight_layout()

        if self.ig!=None:
            fig_ig = plt.figure(ifig+2,figsize=(16,4))

            ax_ehkl=[]
            for iphi in range(nphi):
                ax=fig_ig.add_subplot(1,nphi,iphi+1)
                ax.grid('on')
                ax.locator_params(nbins=4)
                ax_ehkl.append(ax)
                __deco__(ax=ax,iopt=2)
                for istp in range(nstp):
                    y = self.ig[istp,iphi,:]
                    ax.plot(x,y*1e3)
            fig_ig.tight_layout()

class ResidualStress:
    def __init__(self,
                 mod_ext=None,
                 fnmod_epshkl='int_els_ph1.out',
                 #fnmod_ig='igstrain_unload_ph1.out',
                 #fnmod_ig='igstrain_bix_ph1.out',
                 fnmod_ig='igstrain_fbulk_ph1.out',

                 fnmod_sf='igstrain_fbulk_ph1.out',

                 fnmod_str='STR_STR.OUT',

                 fnexp_ehkl='Bsteel_BB_00.txt',

                 fnexp_sf='YJ_Bsteel_BB.sff',

                 exppath='rs',

                 fnPF='rs/new_flowcurves.dat',
                 ifig=1,i_ip=0):
        """
        Arguments
        =========
        fnmod='int_els_ph1.out'
        fnig='igstrain_unload_ph1.out'
        fnsf='igstrain_fbulk_ph1.out'
        fnstr='STR_STR.OUT'
        fnexp_ehkl='Bsteel_BB_00.txt'

        fnexp_sf='YJ_Bsteel_BB.sff'
        exppath='rs'
        ifig=1

        i_ip = 0 (collective stress analysis)
               1 (stress analysis only to check consistency in model)
        """
        if mod_ext!=None:
            print "mod_ext <%s> is given"%mod_ext
            fnmod_epshkl = '%s.%s'%(
                fnmod_epshkl.split('.')[0],mod_ext)
            fnmod_ig = '%s.%s'%(
                fnmod_ig.split('.')[0],mod_ext)
            fnmod_sf = '%s.%s'%(
                fnmod_sf.split('.')[0],mod_ext)
            fnmod_str = '%s.%s'%(
                fnmod_str.split('.')[0],mod_ext)

        #######################################

        # we follow Hauk's convention here...

        #     ij for SF   ij in Hauk's convention
        #  0     (1,1)         (1,1)
        #  1     (2,2)         (2,2)
        #  2     (3,3)         (3,3)
        #  3     (2,3)         (1,2)
        #  4     (1,3)         (1,3)
        #  5     (1,2)         (2,3)
        # import paths;paths.main()
        #from MP.ssort import sh as sort

        if i_ip==0:

            # read model eps^hkl, eps^0, SF
            self.readmod(fnmod_epshkl=fnmod_epshkl,
                         fnmod_ig=fnmod_ig,fnmod_sf=fnmod_sf,
                         fnmod_str=fnmod_str)
            # read experimental eps^hkl, eps^0, SF
            self.readexp(fnexp_ehkl=fnexp_ehkl,fnexp_sf=fnexp_sf,path=exppath)

            # read PF eps^hkl, eps^0, SF
            self.readPF(fnPF)

            self.dat_ref = self.dat_xray
            # psi interpolatioin
            self.dat_model.interp_psi(psi=self.dat_ref.psi.copy())
            self.dat_sf.interp_psi(psi=self.dat_ref.psi.copy())

            # strain interpolation
            self.dat_model.interp_strain(strain=self.dat_ref.strain.copy())
            self.dat_sf.interp_strain(strain=self.dat_ref.strain.copy())

            # phi correction (correct phis)
            self.dat_model.determine_phis(phi_new=self.dat_ref.phi.copy())
            self.dat_sf.determine_phis(phi_new=self.dat_ref.phi.copy())
            self.dat_PF.determine_phis(phi_new=self.dat_ref.phi.copy())

            self.dat_model.plot(ifig=5)
            plt.figure(5).savefig('SF_model.pdf')
            plt.figure(6).savefig('ehkl_model.pdf')
            plt.figure(7).savefig('eps0_model.pdf')
            self.dat_sf.plot(ifig=10)
            plt.figure(10).savefig('SF_exp.pdf')
            plt.figure(12).savefig('eps0_exp.pdf')
            self.dat_xray.plot(ifig=15)
            plt.figure(16).savefig('ehkl_exp.pdf')
            plt.show()

            self.dat_PF.plot(ifig=20)
            plt.figure(20).savefig('SF_PF.pdf')
            plt.figure(21).savefig('ehkl_PF.pdf')
            plt.figure(22).savefig('eps0_PF.pdf')

        elif i_ip==1:
            # read model eps^hkl, eps^0, SF
            self.readmod(fnmod_epshkl=fnmod_epshkl,
                         fnmod_ig=fnmod_ig,fnmod_sf=fnmod_sf,
                         fnmod_str=fnmod_str)
            self.dat_ref = self.dat_model
        elif i_ip==2:
            # read only the experimental eps^hkl
            self.readexp(fnexp_ehkl=fnexp_ehkl,
                         fnexp_sf=fnexp_sf,path=exppath)

        self.i_ip = i_ip

    def readmod(self,fnmod_epshkl,fnmod_ig,fnmod_sf,fnmod_str,
                psi_stp=1):
        """
        read model eps^hkl and ig-strain sf

        All varaibles are meant to be sorted by phi and psis

        ## Selective use of psi should be possible for
        ## parametric study
        """
        from RS import pepshkl
        from pepshkl import reader2 as reader_sf
        from MP.ssort import sh as sort
        # eps^hkl from model
        datm = reader(fnmod_epshkl,isort=True)
        self.stepsm = map(int,datm[-1])
        self.psism = datm[0]; self.npsim = len(self.psism)
        self.phism = datm[1]; self.nphim = len(self.phism)
        self.psism = self.psism * pi / 180.
        self.phism = self.phism * pi / 180.
        self.ndatm = len(self.phism) * len(self.psism)
        ehklm = datm[2] # last state... steps, datm[2] -> epshkl
        ngr = datm[3]; vf = datm[4]
        ehklm_sorted = np.zeros((len(self.stepsm),self.nphim,self.npsim))

        # ig strain from model
        if fnmod_ig!=None:
            #eps0m should be in dimension of: (nstp,nphi,nspi)
            try:
                self.eps0m = reader(fn=fnmod_ig,isort=True)[2]
            except:
                print '\n***********************************************************'
                print 'Given fnmod_ig filename is %s'%fnmod_ig
                print 'This file is not readable by reader method in rs.py module'
                print 'trial with reader2 method in pepshkl.py module is performed'
                print '***********************************************************\n'
                t,dum = reader_sf(fn=fnmod_ig,iopt=1)
                # t[0] ! ehkl
                # t[1] ! e (macro)
                # t[2] ! ehkle    (ehkl - emacro)
                # t[3] ! fhkl
                # t[4] ! fbulk    (f bulk?)
                # t[5] ! ige       e(hkl) - f_hkl*Sij
                # t[6] ! Sij
                # t[7] ! phi
                # t[8] ! psi
                # t[2] ![nst,nsf, nphi, npsi]
                print 'IG strain (self.eps0m) was defined as e(hkl) - f_hkl*S(ij)'
                self.eps0m=t[5][:,0,:,:]

        elif fnmod_ig==None:
            self.eps0m = np.zeros(self.ehklm.shape)

        # stress factor from model
        t, usf = reader_sf(fn=fnmod_sf)
        sfm = t[3] # [istp,k,phi,psi] {fhkl} Stress Factor

        self.sfm = np.zeros((sfm.shape[0],6,sfm.shape[2],sfm.shape[3]))
        for istp in range(len(sfm)):
            for k in range(len(sfm[istp])):
                for iphi in range(len(sfm[istp,k])):
                    self.sfm[istp,k,iphi,:] = sfm[istp,k,iphi,:].copy()

        dum_psi = t[8,0,0,0]
        dum = self.sfm[:,3,:,:] # SF_23
        self.sfm[:,3,:,:] = self.sfm[:,5,:,:]
        self.sfm[:,5,:,:] = dum[:,:,:]
        for istp in range(len(self.sfm)):
            for k in range(len(self.sfm[istp])):
                for iphi in range(len(self.sfm[istp,k])):
                    x = dum_psi
                    y = self.sfm[istp,k,iphi,:].copy()
                    x,y=sort(x,y)
                    self.sfm[istp,k,iphi,:] = y[:]

        # stress/strain states
#        dstr=np.loadtxt(fnmod_str,skiprows=1).T
        dstr=rb(fnmod_str,skiprows=1)
        if len(dstr.shape)==1:
            dstr = np.array([dstr]).T

        evm,svm,e11,e22,e33,e23,e13,e12,s11,s22,s33,s23,s13,s12 \
            = dstr[:14]
        self.strainm_con = np.array([e11,e22,e33,e12,e13,e23])
        self.stressm_con = np.array([s11,s22,s33,s12,s13,s23])
        self.strainm = []
        self.stressm = []

        # for ist in range(len(self.stepsm)):
        #     self.strainm.append(self.strainm_con.T[self.stepsm[ist]])
        #     self.stressm.append(self.stressm_con.T[self.stepsm[ist]])
        for ist in range(len(self.stepsm)):
            self.strainm.append(self.strainm_con.T[ist])
            self.stressm.append(self.stressm_con.T[ist])

        self.strainm=np.array(self.strainm)
        self.stressm=np.array(self.stressm)

        self.dat_model = DiffDat(
            phi=self.phism,psi=self.psism,
            sf=self.sfm,ig=self.eps0m,ehkl=datm[2],
            name='EVPSC',strain=self.strainm,
            stress=self.stressm,
            vf=vf,ngr=ngr)

    def readexp(self,fnexp_ehkl,fnexp_sf,path='rs'):
        """
        Read experimental eps^hkl, eps^0, stress factor
        """
        import os
        from MP.ssort import sh as sort
        from MP.ssort import shellSort as shsort
        from MP.ssort import ind_swap as idsort
        from sff_plot import reader as read_sff

        self.phise,self.psise,self.ehkle,self.dhkle,straine\
            = read_exp(fnexp_ehkl,path='rs')

        self.sfe,self.eps0e,self.sfe_phis,self.sfe_psis,\
            self.sfe_exx = read_sff('%s%s%s'%(path,os.sep,fnexp_sf))

        print '\n*****************************************************'
        print ' Warning in strain_sf determination:'
        print ' Eyy <- Exx since only Exx is included in *.sff file'
        print '*****************************************************\n'

        self.straine=np.zeros((len(straine.T),6))
        for istp in range(len(self.straine)):
            self.straine[istp][0] = straine[0][istp]
            self.straine[istp][1] = straine[1][istp]
        self.strain_sf=np.zeros((len(self.sfe_exx),6))
        for istp in range(len(self.sfe_exx)):
            self.strain_sf[istp][0] = self.sfe_exx[istp]
            self.strain_sf[istp][1] = self.sfe_exx[istp]
        self.sfe_exx=np.array(self.sfe_exx)
        # # self.sf_exp[istr,iphi,npsis,6]
        self.sfe=self.sfe.swapaxes(1,3)#[istr,6,npsis,iphi]
        self.sfe=self.sfe.swapaxes(2,3)#[istr,6,iphi,npsis]
        self.sfe = self.sfe*1e-6
        sf12 = self.sfe[:,5,:,:].copy()
        self.sfe[:,5,:,:] = self.sfe[:,3,:,:]
        self.sfe[:,3,:,:] = sf12[:,:,:]

        # to radian
        self.phise,self.psise,self.sfe_phis,self.sfe_psis \
            = __torad__(self.phise,self.psise,self.sfe_phis,self.sfe_psis)

        ## self.dat_xray and self.dat_sf
        self.dat_xray=DiffDat(phi=self.phise,psi=self.psise,
            sf=None,ig=None,ehkl=self.ehkle,dhkl=self.dhkle,name='X-ray',
            strain=self.straine)
        self.dat_sf = DiffDat(phi = self.sfe_phis,psi = self.sfe_psis,
            sf=self.sfe,ig=self.eps0e,ehkl=None,name='SF',
            strain=self.strain_sf)

    def readPF(self,fnPF):
        from ght_anl import reader
        from MP.ssort import sh as sort
        fij, ig, phi, psi, strain, sij, dhkl,d0hkl,ehkl = reader(fnPF)

        phi,psi = __torad__(phi,psi)
        print phi, psi
        nstp = len(ig)
        nphi = len(ig[0])
        npsi = len(psi)

        # fij (6,nstp,nphi,npsi) 11,22,33,23,13,12
        f23 = fij[3,:,:,:].copy()
        fij[3,:,:,:] = fij[5,:,:,:].copy()
        fij[5,:,:,:] = f23.copy()
        fij = fij.swapaxes(0,1)
        fij = fij *1e-6

        # ig (nstp,nphi,npsi)
        # strain (eps_xx)
        new_strain = np.zeros((nstp,6))
        new_strain[:,0] = strain[:].copy()
        new_strain[:,1] = strain[:].copy()

        ## sorting
        for istp in range(nstp):
            for iphi in range(nphi):
                # ig
                y = ig[istp,iphi,:]
                x,y = sort(psi,y)
                ig[istp,iphi,:] = y.copy()

                # ehkl
                y = ehkl[istp,iphi,:]
                x,y = sort(psi,y)
                ehkl[istp,iphi,:] = y.copy()
                # sf
                for k in range(6):
                    y = fij[istp,k,iphi,:]
                    x,y=sort(psi,y)
                    fij[istp,k,iphi,:] = y.copy()

        self.dat_PF=DiffDat(phi=phi,psi=psi,sf=fij,ehkl=ehkl,ig=ig,
                            strain=new_strain)

    def analysis(self,iopt,istp,ifig=44):
        """
        Define the self.phis, self.psis, self.sf, self.ig, self.tdat

        Arguments
        =========
        iopt=1
        """
        self.phis=self.dat_ref.phi.copy(); self.nphi = len(self.phis)
        self.psis=self.dat_ref.psi.copy(); self.npsi = len(self.psis)
        nphi = self.nphi
        if iopt==0:
            """
              SF      IG     ehkl
            EVPSC   EVPSC   EVPSC
            """
            self.sf   = self.dat_model.sf[istp].copy()
            self.eps0 = self.dat_model.ig[istp].copy()
            self.ehkl = self.dat_model.ehkl[istp].copy()
        if iopt==1:
            self.sf   = self.dat_sf.sf[istp].copy()
            self.eps0 = self.dat_sf.ig[istp].copy()

        # if iopt==1:
        #     """
        #       SF     IG     ehkl
        #       EXP    EXP    EXP
        #     """
        #     self.sf   = self.dat_sf.sf[istp].copy()
        #     self.eps0 = self.dat_sf.ig[istp].copy()
        #     self.ehkl = self.dat_xray.ehkl[istp].copy()
        # if iopt==2:
        #     """
        #       SF     IG      ehkl
        #      EVPSC  EVPSC    EXP
        #     """
        #     self.sf   = self.dat_model.sf[istp].copy()
        #     self.eps0 = self.dat_model.ig[istp].copy()
        #     self.ehkl = self.dat_xray.ehkl[istp].copy()
        # if iopt==3:
        #     """
        #       SF     IG      ehkl
        #      EVPSC   EXP    EVPSC
        #     """
        #     self.sf   = self.dat_model.sf[istp].copy()
        #     self.eps0 = self.dat_sf.ig[istp].copy()
        #     self.ehkl = self.dat_model.ehkl[istp].copy()
        # if iopt==4:
        #     """
        #       SF     IG      ehkl
        #      EXP    EVPSC    EVPSC
        #     """
        #     self.sf   = self.dat_sf.sf[istp].copy()
        #     self.eps0 = self.dat_model.ig[istp].copy()
        #     self.ehkl = self.dat_model.ehkl[istp].copy()

        self.tdat = self.ehkl - self.eps0
        fig=plt.figure(ifig,figsize=(14,3))
        figs=plt.figure(112,figsize=(14,3))
        axes=[]; axesf=[]
        for iphi in range(nphi):
            ax =fig.add_subplot(1,nphi,iphi+1)
            axs=figs.add_subplot(1,nphi,iphi+1)
            ax.set_title(r'$\phi=%3.1f^\circ$'%(self.phis[iphi]*180/pi))
            axs.set_title(r'$\phi=%3.1f^\circ$'%(self.phis[iphi]*180/pi))
            ax.locator_params(nbins=4)
            axs.locator_params(nbins=4)
            axes.append(ax);axesf.append(axs)

        self.sf[2,:,:]=0.
        self.sf[3,:,:]=0.
        self.sf[4,:,:]=0.
        self.sf[5,:,:]=0.

        self.coeff()
        # stress calculation
        stress=self.find_sigma()
        for iphi in range(nphi):
            x = sin(self.psis)**2
            #x = self.psis
            l, = axes[iphi].plot(
                x,self.Ei[iphi],'b--',
                label=r'$E_{i}$')
            c = l.get_color()
            axes[iphi].plot(
                x,self.tdat[iphi],'x',color=c,
                label=r'$\varepsilon^{hkl} - \varepsilon^{hkl}_0$')
            axes[iphi].plot(
                x,self.ehkl[iphi],'+',color='k',
                label=r'$\varepsilon^{hkl}$',alpha=0.2)
            axes[iphi].plot(
                x,self.eps0[iphi],'.',color='k',
                label=r'$\varepsilon^{hkl}_0$',alpha=0.2)
            __deco__(ax=axes[iphi],iopt=0)
            l, = axesf[iphi].plot(
                x,self.sf[0][iphi],'b-o',
                label=r'$F_{11}$')
            __deco__(ax=axesf[iphi],iopt=1)

            if iphi==0: axes[iphi].legend(loc='best',fancybox=True)\
                                  .get_frame().set_alpha(0.5)
        print stress
        fig.tight_layout()
        figs.tight_layout()
        fig.savefig('fit_Ei_iopt%i.pdf'%(iopt))
        figs.savefig('fit_SF_iopt%i.pdf'%(iopt))
        return stress

    def find_sigma(self,ivo=None,init_guess=[0,0,0,0,0,0],
                   weight=None):
        """
        Find the stress by fitting the elastic strains
        1) Guess Ei from stress
        2) Minimize difference between the guessed Ei
           and the observed Ei, i.e., eps(hkl) - eps(IG)
        3) If weight is given, weight the object array in the
           elementwise. For that, shape of the weight array
           should be (self.nphi,self.npsi)

        Arguments
        =========
        ivo        = None
        init_guess = [0,0,0,0,0,0]
        weight     = None
        """
        from scipy import optimize
        fmin = optimize.leastsq

        ## Whether or not weight was given
        if type(weight)==type(None):
            f_objf = self.f_least
            least_args = (ivo)
        else:
            f_objf = self.f_least_weighted
            least_args = (ivo,weight)
        ##

        dat=fmin(f_objf,init_guess,args=least_args,
                 full_output=True,xtol=1e-12,ftol=1e-12,maxfev=1000)
        stress=dat[0]
        cov_x, infodict, mesg, ier = dat[1:]
        if not(ier in [1,2,3,4]):
            raise IOError, "Solution was not found."
        return stress

    def find_sigma_d(self):
        from scipy import optimize
        fmin = optimize.leastsq
        dat = fmin(self.f_least_d,x0=[0,0,0,0,0,0],full_output=True)
        stress=dat[0]
        cov_x, infodict, mesg, ier = dat[1:]
        if not(ier in [1,2,3,4]):
            raise IOError, "Solution was not found."

        print stress

    def xec(self):
        """ Isotropic X-ray elastic constants """
        self.E = 200000. # [MPa]
        self.nu = 0.3
        self.s1 = -self.nu/self.E
        self.s2 = 2*(1+self.nu)/self.E

    def calc_Ei(self,ivo=None):
        """
        Back calculate the elastic strain
        based on 'stress' and elastic coefficients

        ivo = None
        """
        self.Ei = np.zeros((self.nphi,self.npsi))
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                self.Ei[iphi,ipsi] = 0
                for k in range(6): # six components
                    # once ivo is given, optimization runs only
                    # for the given ivo components
                    if ivo==None or (ivo!=None and k in ivo):
                        self.Ei[iphi,ipsi] = self.Ei[iphi,ipsi] \
                            + self.cffs[k,iphi,ipsi] * self.sigma[k]

    def calc_Di(self,d0c=None,d0=None):
        self.Di = np.zeros(self.nphi, self,npsi)
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                self.Di[iphi,ipsi] = 0
                for k in range(6):
                    self.Di[iphi,ipsi] = \
                        self.Di[iphi,ipsi] \
                        + self.cffs[k,iphi,ipsi]\
                        * self.sigma[k]
        if d0c==None and d0==None:
            d0_avg = np.average(self.Di[::])
            self.Di[iphi,ipsi] = self.Di[iphi,ipsi] * d0_avg + d0_avg
        else: self.Di[iphi,ipsi] = self.Di[iphi,ipsi] * d0c + d0

    def coeff(self):
        """
        Calculates a, b, c, d, e, f
        using the isotropic s1 s2 diffraction elastic constants or
              the stress factors
        """
        self.cffs=np.zeros((6,self.nphi,self.npsi))
        self.xec()
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                self.cffs[0,iphi,ipsi] = a(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s11
                self.cffs[1,iphi,ipsi] = b(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s22
                self.cffs[2,iphi,ipsi] = c(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s33
                self.cffs[3,iphi,ipsi] = d(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s12
                self.cffs[4,iphi,ipsi] = e(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s13
                self.cffs[5,iphi,ipsi] = f(self.phis[iphi],self.psis[ipsi],self.s1,self.s2) # s23

        ## overwrite coefficient by stress factor (DEC)
        self.cffs = self.sf[:,:,:].copy()

    def plot(self,stress=[0,0,0,0,0,0],ivo=None,iopt=0,label='None'):
        """
        iopt=0: plot tdat
        iopt=1: plot Ei
        """
        from MP.lib import mpl_lib
        wide_fig = mpl_lib.wide_fig
        rm_inner = mpl_lib.rm_inner
        tune_xy_lim = mpl_lib.tune_xy_lim
        ticks_bin_u = mpl_lib.ticks_bins_ax_u
        self.sigma=np.array(stress)
        self.coeff()
        self.calc_Ei(ivo=ivo) # calculated self.Ei
        # plot and compare self.Ei / self.tdat
        phi = self.phis
        psi = self.psis
        nphi = self.nphi
        npsi = self.npsi

        fig = wide_fig(nw=nphi)
        for iphi in range(nphi):
            ph = phi[iphi]
            ax = fig.axes[iphi]
            #x = psi
            x = sin(psi*np.pi/180.)**2
            ax.plot(psi,self.tdat[iphi],'x',label=r'$\varepsilon^{hkl}$')
            ax.plot(psi,self.Ei[iphi],'-',label=r'$fitting$')

        rm_inner(fig.axes)
        ticks_bin_u(fig.axes)
        tune_xy_lim(fig.axes)

    def f_least_d(self,stress=[0,0,0,0,0,0]):
        """
        """
        self.sigma=np.array(stress)
        self.coeff()
        self.calc_Di() # initial estimation of d0c

        f_array = []
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                f_array.append(self.tdat[iphi,ipsi] - self.Di[iphi,ipsi])
        return np.array(f_array)

    def f_least(self,stress=[0,0,0,0,0,0],ivo=None):
        """
        1. Assign y to self.Ei
        2. f_array = exp_dat - f(stress, y)
        3. return f_array
        """
        self.sigma=np.array(stress)
        self.coeff()
        self.calc_Ei(ivo=ivo)
        f_array = [ ]
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                d = self.tdat[iphi,ipsi] \
                    - self.Ei[iphi,ipsi]
                if np.isnan(d): d = 0
                f_array.append(d)
        return np.array(f_array)

    def f_least_weighted(self,stress=[0,0,0,0,0,0],ivo=None,
                         weight=None):
        """
        For weighted linear least square method
        """
        if type(weight)==type(None):
            raise IOError, "Argument weight should be given"
        if np.shape(weight)!=(self.nphi,self.npsi):
            raise IOError, "Argument weight is not compatible"

        self.sigma=np.array(stress)
        self.coeff()
        self.calc_Ei(ivo=ivo)
        ## weight Ei by volumes in (phi,psi)
        f_array = [ ]
        for iphi in range(self.nphi):
            for ipsi in range(self.npsi):
                d = self.tdat[iphi,ipsi] \
                    - self.Ei[iphi,ipsi]
                d = d * weight[iphi,ipsi]
                if np.isnan(d): d = 0
                f_array.append(d)
        return np.array(f_array)

def psi_reso2(mod=None,ntot=2):
    """
    Make the data nearly-equal spaced along psi (sin2psi) axis

    Arguments
    =========
    mod  = None
    ntot = 2
    """
    sf   = mod.sf
    eps0 = mod.eps0
    ehkl = mod.ehkl
    tdat = mod.tdat # tdat is the stress proportional part

    phis = mod.phis; psis = mod.psis
    nphi = mod.nphi; npsi = mod.npsi

    sin2psi_=[]
    for i in range(len(psis)):
        sin2psi_.append(np.sign(psis) * sin(psis)**2)

    spc = np.linspace(np.min(sin2psi_),np.max(sin2psi_),ntot)

    inds = []
    for i in range(len(spc)):
        ixd = find_nearest(sin2psi_,spc[i])
        inds.append(ixd)

    sf   = select_psi(sf,inds)
    eps0 = select_psi(eps0,inds)
    ehkl = select_psi(ehkl,inds)
    tdat = select_psi(tdat,inds)
    phis = phis[::]

    new_psi = []
    for i in range(len(inds)):
        new_psi.append(psis[inds[i]])
    psis = np.array(new_psi)
    nphi = len(phis); npsi = len(psis)

    mod.sf = sf    ; mod.npsi = npsi
    mod.eps0 = eps0; mod.ehkl = ehkl; mod.tdat = tdat
    mod.phis = phis; mod.psis = psis; mod.nphi = nphi

    # ## mod.dat_model
    # mod.dat_model.sf   = select_psi(mod.dat_model.sf,inds)
    # mod.dat_model.ig   = select_psi(mod.dat_model.ig,inds)
    # mod.dat_model.vf   = select_psi(mod.dat_model.vf,inds)
    # mod.dat_model.ehkl = select_psi(mod.dat_model.ehkl,inds)
    # mod.dat_model.psi  = psis[::]
    # mod.dat_model.npsi = len(mod.dat_model.psi)

def psi_reso3(obj,psi,ntot=2):
    """
    Reduce elements along the psi axis,
    which is assumed as the ending axis

    Arguments
    =========
    obj
    psi
    ntot
    """
    sign_sin2psi = []
    for i in range(len(psi)):
        sign_sin2psi.append(
            np.sign(psi) \
            * sin(psi)**2)
    # equal distance
    spc  = np.linspace(np.min(sign_sin2psi),
                       np.max(sign_sin2psi),ntot)
    inds = []
    for i in range(len(spc)):
        inds.append(find_nearest(
            sign_sin2psi,spc[i]))
    return select_psi(obj, inds)

def select_psi(dat,inds):
    array = []
    dum = dat.T
    for i in range(len(inds)):
        array.append(dum[inds[i]])
    return np.array(array).T

def find_nearest(array,value):
    return (np.abs(array-value)).argmin()


def psi_reso(mod=None,nbin=2):
    sf = mod.sf
    eps0 = mod.eps0
    ehkl = mod.ehkl
    tdat = mod.tdat # tdat is the stress proportional part

    phis = mod.phis
    psis = mod.psis
    nphi = mod.nphi
    npsi = mod.npsi

    sf = sf[::,::,::nbin]
    eps0 = eps0[::,::nbin]
    ehkl = ehkl[::,::nbin]
    tdat = tdat[::,::nbin]
    phis = phis[::]
    psis = psis[::nbin]

    nphi = len(phis)
    npsi = len(psis)

    mod.sf=sf
    mod.eps0=eps0
    mod.ehkl=ehkl
    mod.tdat=tdat
    mod.phis=phis
    mod.psis=psis
    mod.nphi=nphi
    mod.npsi=npsi


def filter_psi(mod=None,psimx=None,sin2psimx=None):
    """
    Arguments
    =========
    mod   = None
    psimx = None
    sin2psimx = None
    """
    sf   = mod.sf
    eps0 = mod.eps0
    ehkl = mod.ehkl
    tdat = mod.tdat # tdat is the stress proportional part

    phis = mod.phis
    psis = mod.psis
    nphi = mod.nphi
    npsi = mod.npsi

    # assumed that psis is sorted - ascending order
    if psimx!=None:
        psimx = psimx * pi/180.
        for i in range(len(psis)):
            if psis[i]>=-psimx:
                i0=i; break
        for i in range(len(psis)):
            if psis[i]>=psimx:
                i1=i; break
    if sin2psimx!=None:
        ref = sin(psis)**2.
        for i in range(len(ref)):
            if ref[i]<= sin2psimx:
                i0 = i; break
        reft = ref[::-1]
        for i in range(len(reft)):
            if reft[i]<=sin2psimx:
                i1 = len(reft) - i; break

    sf = sf[:,:,i0:i1]
    eps0 = eps0[:,i0:i1]
    ehkl = ehkl[:,i0:i1]
    tdat = tdat[:,i0:i1]
    phis = phis[::]
    psis = psis[i0:i1]

    nphi = len(phis)
    npsi = len(psis)

    mod.sf=sf
    mod.eps0=eps0
    mod.ehkl=ehkl
    mod.tdat=tdat
    mod.phis=phis
    mod.psis=psis
    mod.nphi=nphi
    mod.npsi=npsi

    ## mod.dat_model
    mod.dat_model.sf   = mod.dat_model.sf[:,:,:,i0:i1]
    mod.dat_model.ig   = mod.dat_model.ig[:,:,i0:i1]
    mod.dat_model.vf   = mod.dat_model.vf[:,:,i0:i1]
    mod.dat_model.ehkl = mod.dat_model.ehkl[:,:,i0:i1]
    mod.dat_model.psi  = mod.dat_model.psi[i0:i1]
    mod.dat_model.npsi  = len(mod.dat_model.psi)


def filter_psi2(obj=None,sin2psi=[],bounds=[0.,1.]):
    """
    Limit psi values - trim some elements from the obj
    array as to assert only a certain range of psi (sin2psi)

    Arguments
    =========
    obj     = None
    sin2psi =
    bounds  = [0,  1.]
    """
    inds = []
    for i in range(len(sin2psi)):
        val = sin2psi[i]
        if val>=bounds[0] and val<=bounds[1]:
            inds.append(i)
    shape = np.array(obj.shape)
    shape[-1] = len(inds)
    new_obj = np.zeros(shape)
    new_obj_t = new_obj.swapaxes(0,-1)
    obj_t = obj.swapaxes(0,-1)

    for i in range(len(inds)):
        new_obj_t[i]=obj_t[inds[i]]

    new_obj = new_obj_t.swapaxes(0,-1)
    return new_obj
