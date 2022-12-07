import os
import json
from astropy import units as u
from lib.frequency.band import FrequencyBand
from path_data import path_data

def read_bands(file) -> dict:
    with open(file, 'r') as f:
        bands_raw = json.load(f)

    return {x: FrequencyBand(low=y['lowerMhz'] * u.MHz, high=y['upperMhz'] * u.MHz) 
            for (x,y) in bands_raw.items()}
    

bands = read_bands(file=os.path.join(path_data, 'bands.json'))
