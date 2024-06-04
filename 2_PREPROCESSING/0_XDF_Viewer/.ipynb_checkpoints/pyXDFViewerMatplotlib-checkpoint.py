import pyxdf
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tkinter import filedialog
import numpy as np

# Load the XDF file
#data, header = pyxdf.load_xdf('lightsensorPlux.xdf')
file_path = filedialog.askopenfilename(title="Select an XDF file", filetypes=[("XDF Files", "*.xdf")])
data, header  = pyxdf.load_xdf(
    file_path,
    select_streams=None,
    on_chunk=None,
    synchronize_clocks=True,
    handle_clock_resets=False,
    dejitter_timestamps=True,
    jitter_break_threshold_seconds=1,
    jitter_break_threshold_samples=500,
    clock_reset_threshold_seconds=5,
    clock_reset_threshold_stds=5,
    clock_reset_threshold_offset_seconds=1,
    clock_reset_threshold_offset_stds=10,
    winsor_threshold=0.0001,
    verbose=None)

# Create a list of colors using the jet colormap
n_lines = len(data)
colors = plt.cm.jet(np.linspace(0, 1, n_lines))

# Create the plot
fromPercentage = 0
toPercentage   = 100 
print(len(data))
plotNr = 0
fig, axs = plt.subplots(len(data), 1, sharex=True, sharey=False, figsize=(10, 3*len(data)))
plt.subplots_adjust(hspace=.0)

for i, stream in enumerate(data):
    print(stream['info'])
    print(i)
    axs[plotNr].grid(linestyle="--",alpha=0.5)
    if 'Markers' in stream['info']['type']:
        print("markers")
        timeSlice = stream['time_stamps']
        dataSlice = np.transpose(stream['time_series'])[i]
        axs[plotNr].plot (timeSlice, dataSlice, color='r', linestyle=':',marker='8', linewidth=0.5)
        #axs[i].text(timeSlice, axs[i].get_ylim()[1], dataSlice, rotation=90, va='top', ha='center')
    else: 
        for c in range(int(stream['info']['channel_count'][0])):
            #fromSlice = int(len(stream['time_stamps'])/(100/fromPercentage))
            #toSlice   = int(len(stream['time_stamps'])/(100/toPercentage))
            fromSlice = 0
            toSlice   = int(len(stream['time_stamps'])/(100/toPercentage))
            try:    
                timeSlice = stream['time_stamps'][fromSlice:toSlice]
                dataSlice = np.transpose(stream['time_series'])[i][fromSlice:toSlice]
            except:
                timeSlice = stream['time_stamps'][fromSlice:toSlice]
                dataSlice = stream['time_series'][fromSlice:toSlice]
            axs[plotNr].grid(linestyle="--",alpha=0.5)
            axs[plotNr].plot(timeSlice, dataSlice, color=colors[i], linewidth=0.5)
            axs[plotNr].set_title(stream['info']['name'][0])
    if 'units' in stream['info']:
        axs[plotNr].set_ylabel(stream['info']['units'][0])
    plotNr += 1
    
plt.xlabel('Time (s)')

# Add the slider
axcolor = 'lightgoldenrodyellow'
axslider = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor=axcolor)
slider = Slider(axslider, 'Time', data[0]['time_stamps'][0], data[0]['time_stamps'][-1], valinit=data[0]['time_stamps'][0])

# Update the plot when the slider is changed
def update(val):
    for i, stream in enumerate(data):
        time_min = max(val, data[i]['time_stamps'][0])
        time_max = min(val + 1, data[i]['time_stamps'][-1])
        axs[i].set_xlim(time_min, time_max)  # Set the time axis based on the slider value
    fig.canvas.draw_idle()

slider.on_changed(update)
plt.show()

'''
================    ===============================
character           description
================    ===============================
   -                solid line style
   --               dashed line style
   -.               dash-dot line style
   :                dotted line style
   .                point marker
   ,                pixel marker
   o                circle marker
   v                triangle_down marker
   ^                triangle_up marker
   <                triangle_left marker
   >                triangle_right marker
   1                tri_down marker
   2                tri_up marker
   3                tri_left marker
   4                tri_right marker
   s                square marker
   p                pentagon marker
   *                star marker
   h                hexagon1 marker
   H                hexagon2 marker
   +                plus marker
   x                x marker
   D                diamond marker
   d                thin_diamond marker
   |                vline marker
   _                hline marker
================    ===============================
'''