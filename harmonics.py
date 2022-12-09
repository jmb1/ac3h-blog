import os
from astropy import units as u
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import lib.frequency.amateur_bands as amateur_bands
from lib.frequency.band import FrequencyBand
from path_data import path_output

save_dir = os.path.join(path_output, 'harmonics')
max_harmonic = 12

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
        band_overlaps = [(i+2, rx_band.intersect(x)) for (i, x) in enumerate(harmonics) if rx_band.intersect(x)]
        if len(band_overlaps) == 0:
            continue
        elif len(band_overlaps) == 1:
            rx_band_intersections[(rx_band_id, tx_band_id, band_overlaps[0][0])] = band_overlaps[0][1]
        else:
            raise ValueError('fixme')
        
uniq_rx_victim_bands = sorted(list({x[0] for x in rx_band_intersections.keys()}),
                              key=lambda x: rx_bands[x].center().value,
                              reverse=True)
num_uniq_rx_victim_bands = len(uniq_rx_victim_bands)
uniq_tx_interferer_bands = sorted(list({x[1] for x in rx_band_intersections.keys()}),
                                  key=lambda x: tx_bands[x].center().value)
num_uniq_tx_interferer_bands = len(uniq_rx_victim_bands)

num_vert_bars = []
for rx_band in uniq_rx_victim_bands:
    c_intersects = {x[1:3]:y for (x,y) in rx_band_intersections.items() if x[0] == rx_band}
    num_vert_bars.append(len(c_intersects))
num_vert_bars = max(num_vert_bars)
bar_height = 0.9

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

fig, axs = plt.subplots(round(np.ceil(num_uniq_rx_victim_bands/2)), 2)
fig.tight_layout()
axs = axs.ravel()
fig.set_size_inches(7.0, 5.0)
#fig.suptitle('Cross-Band Harmonic Overlap')
c_map = plt.cm.get_cmap('tab20')
for i, rx_band in enumerate(uniq_rx_victim_bands):
    c_intersects = {x[1:3]:y for (x,y) in rx_band_intersections.items() if x[0] == rx_band}
    c_intersects = sorted(c_intersects.items(), key=lambda x: x[1].bandwidth().value, reverse=True)
    c_intersects = {x:y for (x,y) in c_intersects}
    for (k, (key, value)) in enumerate(c_intersects.items()):
        xy = (value.low(u.MHz).value, k + (1-bar_height)/2)
        width = value.bandwidth(u.MHz).value
        clr = c_map([i for (i, x) in enumerate(uniq_tx_interferer_bands) if x == key[0]][0])
        axs[i].add_patch( Rectangle(xy, width, bar_height, fc =clr, ec =clr, lw = 0) )
        axs[i].text(xy[0] + width/2, k + 0.5, '%s' % key[1], horizontalalignment='center', 
                    verticalalignment='center', fontsize='xx-small')
    axs[i].set_xlim([x.value for x in rx_bands[rx_band].tuple(u.MHz)])
    axs[i].set_ylim([0, num_vert_bars])
    axs[i].set_yticks([])
    axs[i].set_title(rx_band, fontsize=8)
    axs[i].tick_params(axis='both', which='major', labelsize=5)
    axs[i].grid(axis='x', linestyle=':')
axs[-1].remove()
for i, b in enumerate(uniq_tx_interferer_bands):
    clr = c_map(i)
    axs[num_uniq_rx_victim_bands-1].add_patch( Rectangle((0,0), 1, 1, fc =clr, ec =clr, lw = 0, label=b))
legend = plt.legend(fontsize='x-small', ncol=3, bbox_to_anchor=(2.0, 1.5), title="Harmonic Bands")
plt.setp(legend.get_title(),fontsize='x-small')
file_save = os.path.join(save_dir, 'harmonic-overlap.png')
plt.savefig(file_save, dpi=250)
plt.show()

