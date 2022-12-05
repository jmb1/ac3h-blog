import os
from lib.siglent.ssa3021x import Ssa3021xTrace
from astropy import units as u
from path_data import path_data_measurements

path_dunestar = os.path.join(path_data_measurements, 'dunestar')

t = Ssa3021xTrace.from_csv(file=os.path.join(path_dunestar, '10m.csv'))