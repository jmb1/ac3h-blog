import os
import re
import json
from lib.siglent.ssa3021x import Ssa3021xTrace, Ssa3021xTraceSet
from astropy import units as u
import matplotlib.pyplot as plt
import numpy as np
from path_data import path_data, path_data_measurements

path_dunestar = os.path.join(path_data_measurements, 'dunestar')

file_bands = os.path.join(path_data, 'bands.json')
with open(file_bands, 'r') as f:
    bands = json.load(f)

trace_data = {}
for file in os.listdir(path_dunestar):
    if re.search('\.bz2$', file) is None:
        continue
    key = re.sub('\.csv\.bz2$','',file)
    args = {'file': os.path.join(path_dunestar, file)}
    trace_data[key] = Ssa3021xTraceSet.from_csv(**args)

key_list = [x for x in sorted(trace_data.keys()) if re.search('^[0-9]+', x)]
s12_loss = {}
for i in key_list:
    trace_i = trace_data[i].traces[0]
    for k in key_list:
        m_band = np.logical_and(
            trace_i.freq.to(u.MHz).value > bands[k]['lowerMhz'],
            trace_i.freq.to(u.MHz).value < bands[k]['upperMhz']
        )
        filtered_pwr = -1.0 * trace_i.pwr.to(u.dB(u.mW)).value[m_band]
        s12_loss[(i, k)] = {
            'min': np.min(filtered_pwr),
            'max': np.max(filtered_pwr),
            'avg': np.mean(filtered_pwr)
        }

# min rejection
csv_header = ','.join(['source', *list(key_list)])
csv_rows = []
for i in key_list:
    csv_rows.append(','.join([str(s12_loss[(i, x)]['min']) for x in key_list]))
print('Minimum filter rejection:')
print(csv_header)
for row in csv_rows:
    print(row)

# max rejection
csv_header = ','.join(['source', *list(key_list)])
csv_rows = []
for i in key_list:
    csv_rows.append(','.join([str(s12_loss[(i, x)]['max']) for x in key_list]))
print('Maximum filter rejection:')
print(csv_header)
for row in csv_rows:
    print(row)

fig = plt.figure
for key in sorted(trace_data):
    if re.search('^[0-9]+', key[0]) is None:
        continue
    plt.plot(trace_data[key].traces[0].freq.to(u.MHz).value, 
             trace_data[key].traces[0].pwr.to(u.dB(u.mW)).value, label=key)
plt.grid('both')
plt.xlabel('MHz')
plt.ylabel('dB')
plt.legend()
plt.title('Dunestar Filters: S12 Power')
plt.show()
