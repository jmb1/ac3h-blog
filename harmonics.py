from astropy import units as u
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import lib.frequency.amateur_bands as amateur_bands
from lib.frequency.band import FrequencyBand


max_harmonic = 8

filter = FrequencyBand(low=1.5 * u.MHz, high=60.0 * u.MHz)
tx_bands = {x:y for (x,y) in amateur_bands.bands.items() if y.intersect(filter)}
tx_harmonics = {}
for (key, value) in tx_bands.items():
    tx_harmonics[key] = [value.harmonic(x) for x in range(2,max_harmonic+1)]

filter = FrequencyBand(low=1.5 * u.MHz, high=500.0 * u.MHz)
rx_bands = tx_bands = {x:y for (x,y) in amateur_bands.bands.items() if y.intersect(filter)}


rx_band_intersections = {}
for (rx_band_id, rx_band) in rx_bands.items():
    for (tx_band_id, harmonics) in tx_harmonics.items():
        band_overlaps = [(i+1, rx_band.intersect(x)) for (i, x) in enumerate(harmonics) if rx_band.intersect(x)]
        if len(band_overlaps) == 0:
            continue
        elif len(band_overlaps) == 1:
            rx_band_intersections[(rx_band_id, tx_band_id, band_overlaps[0][0])] = band_overlaps[0][1]
        else:
            raise ValueError('fixme')
        
uniq_rx_victim_bands = sorted(list({x[0] for x in rx_band_intersections.keys()}))
num_uniq_rx_victim_bands = len(uniq_rx_victim_bands)
uniq_tx_interferer_bands = sorted(list({x[1] for x in rx_band_intersections.keys()}))
num_uniq_tx_interferer_bands = len(uniq_rx_victim_bands)


fig, axs = plt.subplots(round(np.ceil(num_uniq_rx_victim_bands/2)), 2)
axs = axs.ravel()
fig.set_size_inches(5.0, 8.0)
#fig.suptitle('Vertically stacked subplots')
c_map = plt.cm.get_cmap('tab20')
for i, rx_band in enumerate(uniq_rx_victim_bands):
    c_intersects = {x[1:3]:y for (x,y) in rx_band_intersections.items() if x[0] == rx_band}
    for (k, (key, value)) in enumerate(c_intersects.items()):
        xy = (value.low(u.MHz).value, k)
        width = value.bandwidth(u.MHz).value
        height = 1.0
        clr = c_map([i for (i, x) in enumerate(uniq_tx_interferer_bands) if x == key[0]][0])
        axs[i].add_patch( Rectangle(xy, width, height, fc =clr, ec =clr, lw = 1) )
        axs[i].set_xlim([x.value for x in rx_bands[rx_band].tuple(u.MHz)])
        axs[i].set_ylim([0, len(c_intersects)+1])

plt.show()

