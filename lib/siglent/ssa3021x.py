import os
import re
from astropy import units as u
import bz2
import io
from typing import Dict
import numpy as np

def meta_dict(meta_lines: list) -> dict:
    meta = {x[0]: x[1:] for x in meta_lines}
    for key in meta.keys():
        if len(meta[key]) < 1:
            meta[key] = None
            continue
        for (i, item) in enumerate(meta[key]):
            try:
                meta[key][i] = int(item)
            except ValueError:
                try:
                    meta[key][i] = float(item)
                except ValueError:
                    meta[key][i] = str(item)
        if len(meta[key]) == 1:
            meta[key] = meta[key][0]
    return meta

class Ssa3021xTrace:
    def __init__(self, meta: dict, freq: u.Quantity, pwr: u.Quantity):
        self.freq = freq.to(u.Hz)
        self.pwr = pwr.to(u.dB(u.mW))

class Ssa3021xTraceSet:
    def __init__(self, meta: dict, traces: Dict[str, str]):
        self.meta = meta
        self.traces = traces

    @staticmethod
    def from_csv(file: str):
        if not os.path.exists(file):
            raise ValueError('unrecognized filepath: %s' % file)
        if re.search(r'\.bz2$', file):
            with open(file, 'rb') as f:
                buf = io.StringIO(bz2.decompress(f.read()).decode('utf-8'))
                lines = [x.rstrip().split(',') for x in buf.readlines()]
        else:
            with open(file, 'r') as f:
                lines = [x.rstrip().split(',') for x in f.readlines()]
        trace_indx = [i for (i, x) in enumerate(lines) if x[0] == 'Trace Data']
        meta = meta_dict(meta_lines=lines[0:trace_indx[0]])
        if meta['Y Axis Unit'] == 'dBm':
            y_units = u.dB(u.mW)
        elif meta['Y Axis Unit'] == 'dBW':
            y_units = u.dB(u.W)
        else:
            raise ValueError('fixme')

        traces = []
        for i in trace_indx:
            for k in range(10):
                if lines[i-k][0] == 'Trace Name':
                    trace_name = lines[i-k][1]
                    trace_meta = meta_dict(meta_lines=lines[i-k:i])
                    break
                if k == 9:
                    raise ValueError('fixme')
            
            k = 1

            freq, val = zip(*[lines[i+1+k] for k in range(meta['Number of Points'])])
            freq = np.array([float(x) for x in freq]) * u.Hz
            val = np.array([float(x) for x in val]) * y_units
            traces.append(Ssa3021xTrace(meta=trace_meta, freq=freq, pwr=val))
        return Ssa3021xTraceSet(meta=meta, traces=traces)