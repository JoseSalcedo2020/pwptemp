def temp_time(n, well):
    """
    :param n:
    :param well:
    :return:
    """
    from .initcond import init_cond
    from .heatcoefficients import heat_coef
    from .linearsystem import temp_calc
    from .plot import profile
    from .analysis import param_effect
    from .torque_drag import calc_torque_drag
    from .fluid import initial_density, calc_density
    # Simulation main parameters
    time = n  # circulating time, h
    tcirc = time * 3600  # circulating time, s
    deltat = 60
    tstep = int(tcirc / deltat)
    ic = init_cond(well)
    well.rhof, rhof_initial = initial_density(well, ic)
    well.drag, well.torque = calc_torque_drag(well)  # Torque/Forces, kN*m / kN
    hc = heat_coef(well, deltat)
    temp = temp_calc(well, ic, hc)

    for x in range(1, tstep):
        well.rhof = calc_density(well, ic, rhof_initial)
        well.drag, well.torque = calc_torque_drag(well)  # Torque/Forces, kN*m / kN

        ic.tdsio = temp.tdsi
        ic.tdso = temp.tds
        ic.tao = temp.ta
        ic.tcsgo = temp.t3
        ic.tsr = temp.tsr
        hc_new = heat_coef(well, deltat)
        temp = temp_calc(well, ic, hc_new)

    class TempDist(object):
        def __init__(self):
            self.tdsi = temp.tdsi
            self.tds = temp.tds
            self.ta = temp.ta
            self.tr = temp.tr
            self.tcsg = temp.tcsg
            self.toh = temp.toh
            self.tsr = temp.tsr
            self.tfm = ic.tfm
            self.time = time
            self.md = well.md
            self.riser = well.riser
            self.csgs_reach = temp.csgs_reach
            self.deltat = deltat

        def plot(self, sr=False):
            profile(self, sr)

        def effect(self, md_length=1):
            effect = param_effect(self, well, md_length)
            return effect

        def well(self):
            return well

        def stab(self):
            stab = stab_time(well)
            return stab

    return TempDist()


def stab_time(well):
    from statistics import mean
    from .initcond import init_cond
    from.plot import behavior
    ta = []
    for n in range(1, 3):
        ta.append(temp_time(n, well).ta)

    valor = mean(ta[0]) - mean(ta[1])
    finaltime = 2

    while abs(valor) >= 0.01:
        ta.append(temp_time(finaltime+1, well).ta)
        valor = mean(ta[finaltime]) - mean(ta[finaltime-1])
        finaltime = finaltime + 1

    tbot = []
    tout = []

    for n in range(finaltime):
        tbot.append(ta[n][-1])
        tout.append(ta[n][0])

    class StabTime(object):
        def __init__(self):
            self.finaltime = finaltime
            self.tbot = tbot
            self.tout = tout
            self.tfm = init_cond(well).tfm

        def plot(self):
            behavior(self)

    return StabTime()


def temp_times(n, x, well):
    from numpy import arange
    from .plot import profile_multitime
    temps_list = []
    times_list = []
    for i in list(arange(x, n+x, x)):
        current_temp = temp_time(i, well)
        temps_list.append(current_temp)
        times_list.append(i)

    class TempDist(object):
        def __init__(self):
            self.values = temps_list
            self.times = times_list

        def plot(self, tdsi=True, ta=False, tr=False, tcsg=False, tfm=True, tsr=False):
            profile_multitime(self, tdsi=tdsi, ta=ta, tr=tr, tcsg=tcsg, tfm=tfm, tsr=tsr)

    return TempDist()


# BUILDING GENERAL FUNCTIONS FOR DRILLING MODULE


def temp(n, mdt=3000, casings=[], wellpath_data=[], bit=0.216, grid_length=50, profile='V', build_angle=1, kop=0, eob=0,
             sod=0, eod=0, kop2=0, eob2=0, change_input={}):
    from .input import data, set_well
    from .. import wellpath
    tdata = data(casings, bit)
    for x in change_input:   # changing default values
        if x in tdata:
            tdata[x] = change_input[x]
        else:
            raise TypeError('%s is not a parameter' % x)
    if len(wellpath_data) == 0:
        depths = wellpath.get(mdt, grid_length, profile, build_angle, kop, eob, sod, eod, kop2, eob2)
    else:
        depths = wellpath.load(wellpath_data, grid_length)
    well = set_well(tdata, depths)
    temp_distribution = temp_time(n, well)

    return temp_distribution


def temps(n, x, mdt=3000, casings=[], wellpath_data=[], bit=0.216, grid_length=50, profile='V', build_angle=1, kop=0, eob=0,
             sod=0, eod=0, kop2=0, eob2=0, change_input={}):
    from .input import data, set_well
    from .. import wellpath
    tdata = data(casings, bit)
    for i in change_input:   # changing default values
        if i in tdata:
            tdata[i] = change_input[i]
        else:
            raise TypeError('%s is not a parameter' % i)
    if len(wellpath_data) == 0:
        depths = wellpath.get(mdt, grid_length, profile, build_angle, kop, eob, sod, eod, kop2, eob2)
    else:
        depths = wellpath.load(wellpath_data, grid_length)
    well = set_well(tdata, depths)
    temp_distributions = temp_times(n, x, well)

    return temp_distributions


def input_info(about='all'):
    from .input import info
    info(about)


def stab(mdt=3000, casings=[], wellpath_data=[], bit=0.216, deltaz=50, profile='V', build_angle=1, kop=0, eob=0, sod=0,
         eod=0, kop2=0, eob2=0, change_input={}):
    from .input import data, set_well
    from .. import wellpath
    tdata = data(casings, bit)
    for x in change_input:  # changing default values
        if x in tdata:
            tdata[x] = change_input[x]
        else:
            raise TypeError('%s is not a parameter' % x)
    if len(wellpath_data) == 0:
        depths = wellpath.get(mdt, deltaz, profile, build_angle, kop, eob, sod, eod, kop2, eob2)
    else:
        depths = wellpath.load(wellpath_data, deltaz)
    well = set_well(tdata, depths)
    stabilization = stab_time(well)

    return stabilization
