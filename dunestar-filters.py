import os
import re
import json
from typing import Dict, Tuple
from lib.siglent.ssa3021x import Ssa3021xTrace, Ssa3021xTraceSet
from astropy import units as u
from astropy.units import Quantity
import matplotlib.pyplot as plt
import numpy as np
from path_data import path_data, path_data_measurements
import lib.frequency.amateur_bands as amateur_bands
from lib.frequency.band import FrequencyBand

def read_trace_data(path_dir: str):
    trace_data = {}
    for file in os.listdir(path_dir):
        if re.search('\.bz2$', file) is None:
            continue
        key = re.sub('\.csv\.bz2$','',file)
        args = {'file': os.path.join(path_dir, file)}
        trace_data[key] = Ssa3021xTraceSet.from_csv(**args)
    return trace_data


def compute_s12_losses(trace_data: Dict[str, Ssa3021xTraceSet], bands: Dict[str, FrequencyBand]) -> Dict[Tuple[str], Dict[str, Quantity]]:
    key_list = [x for x in sorted(trace_data.keys()) if re.search('^[0-9]+', x)]
    s12_loss = {}
    for i in key_list:
        trace_i = trace_data[i].traces[0]
        for k in key_list:
            m_band = np.logical_and(
                trace_i.freq.to(u.MHz) > bands[k].low(u.MHz),
                trace_i.freq.to(u.MHz) < bands[k].high(u.MHz)
            )
            filtered_pwr = -1.0 * trace_i.pwr.to(u.dB(u.mW))[m_band].value
            s12_loss[(i, k)] = {
                'min': np.min(filtered_pwr) * u.dB(1),
                'max': np.max(filtered_pwr) * u.dB(1),
                'avg': np.mean(filtered_pwr)  * u.dB(1)
            }
    return s12_loss

def export_s12_losses(s12_loss: Dict[Tuple[str], Dict[str, Quantity]]):
    key_list = sorted(list({x[0] for x in s12_loss.keys()}))

    # min rejection
    csv_header = ','.join(['source', *list(key_list)])
    csv_rows = []
    for i in key_list:
        csv_rows.append(','.join([i, *[str(s12_loss[(i, x)]['min'].value) for x in key_list]]))
    print('Minimum filter rejection:')
    print(csv_header)
    for row in csv_rows:
        print(row)

    # max rejection
    csv_header = ','.join(['source', *list(key_list)])
    csv_rows = []
    for i in key_list:
        csv_rows.append(','.join([i, *[str(s12_loss[(i, x)]['max'].value) for x in key_list]]))
    print('Maximum filter rejection:')
    print(csv_header)
    for row in csv_rows:
        print(row)

def plot_s12_loss_vs_freq(trace_data: Dict[str, Ssa3021xTraceSet]):
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

if __name__ == '__main__':
    path_dunestar = os.path.join(path_data_measurements, 'dunestar')
    dunestar_bands = amateur_bands.read_bands(os.path.join(path_dunestar, 'band-coverage.json'))
    trace_data = read_trace_data(path_dir=path_dunestar)

    s12_loss_full = compute_s12_losses(trace_data=trace_data, bands=amateur_bands.bands)
    export_s12_losses(s12_loss=s12_loss_full)

    s12_loss_cov = compute_s12_losses(trace_data=trace_data, bands=dunestar_bands)
    export_s12_losses(s12_loss=s12_loss_cov)

    plot_s12_loss_vs_freq(trace_data=trace_data)
