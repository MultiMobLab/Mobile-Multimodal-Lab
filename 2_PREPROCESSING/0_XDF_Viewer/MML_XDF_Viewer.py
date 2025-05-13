"""
MOBILE MULTIMODAL LAB (MML): XDF Stream Visualizer

Description:
------------
This script provides a graphical visualization of all streams contained in an XDF (Extensible Data Format) file 
recorded using LabStreamingLayer (LSL). It is designed to help researchers perform an initial inspection of 
the multimodal data recorded via MML. It allows for temporal navigation and stream-specific inspection of data via interactive sliders and multi-axis plotting, 

Key Features:
-------------
- Loads and visualizes all streams (audio, video, markers, etc.) from an XDF file.
- Uses distinct subplots per stream with color-coded plotting.
- Automatically distinguishes marker streams and plots them with appropriate symbols.
- Interactive time navigation via slider (1-second moving window).
- Supports de-jittering and time alignment of asynchronous LSL streams.

Requirements:
--------------
- Python 3.x
- pyxdf
- matplotlib
- numpy
- tkinter (usually included with Python installations)

Usage:
-------
Run the script in a Python environment. A GUI will prompt you to select an `.xdf` file.
All available streams will be loaded and plotted. Use the slider to inspect different time windows.


Author: Pascal de Water, Technical Support Group, Donders Institute for Brain, Cognition and Behaviour, Radboud University Nijmegen, The Netherlands
Last Modified: 12/10/2025 by Davdie Ahmar
"""


import pyxdf
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tkinter import filedialog
import numpy as np


# === File Selection ===
# Open a file dialog to select the XDF file (instead of hardcoding the path)
file_path = filedialog.askopenfilename(
    title="Select an XDF file", 
    filetypes=[("XDF Files", "*.xdf")]
)

# === Load the XDF file ===
# pyxdf.load_xdf loads all streams and metadata from the selected XDF file
data, header = pyxdf.load_xdf(
    file_path,
    select_streams=None,                   # Load all streams
    on_chunk=None,
    synchronize_clocks=True,              # Apply time correction between streams
    handle_clock_resets=False,            # Do not reset on clock glitches
    dejitter_timestamps=True,             # Apply jitter correction for uneven timestamps
    jitter_break_threshold_seconds=1,
    jitter_break_threshold_samples=500,
    clock_reset_threshold_seconds=5,
    clock_reset_threshold_stds=5,
    clock_reset_threshold_offset_seconds=1,
    clock_reset_threshold_offset_stds=10,
    winsor_threshold=0.0001,              # Winsorization to suppress extreme values
    verbose=None
)

# === Create Color Map ===
# Generate a color for each stream using the 'jet' colormap
n_lines = len(data)
colors = plt.cm.jet(np.linspace(0, 1, n_lines))

# === Time Window Selection ===
fromPercentage = 0    # Start at 0% of the signal
toPercentage   = 100  # End at 100% of the signal

print(len(data))      # Print the number of streams
plotNr = 0            # Initialize subplot counter

# === Setup Subplots ===
fig, axs = plt.subplots(len(data), 1, sharex=True, sharey=False, figsize=(10, 3*len(data)))
plt.subplots_adjust(hspace=.0)  # Minimize vertical spacing between plots

# === Loop Over Each Stream ===
for i, stream in enumerate(data):
    print(stream['info'])  # Print stream metadata
    print(i)
    
    axs[plotNr].grid(linestyle="--", alpha=0.5)  # Add dashed grid lines to each subplot

    # === Marker Stream Visualization ===
    if 'Markers' in stream['info']['type']:
        print("markers")
        timeSlice = stream['time_stamps']
        dataSlice = np.transpose(stream['time_series'])[i]
        axs[plotNr].plot(
            timeSlice, 
            dataSlice, 
            color='r', 
            linestyle=':', 
            marker='8', 
            linewidth=0.5
        )

    # === Continuous Signal Stream Visualization ===
    else:
        for c in range(int(stream['info']['channel_count'][0])):
            fromSlice = 0
            toSlice = int(len(stream['time_stamps']) / (100 / toPercentage))

            try:
                timeSlice = stream['time_stamps'][fromSlice:toSlice]
                dataSlice = np.transpose(stream['time_series'])[i][fromSlice:toSlice]
            except:
                # Fallback in case transposition fails (single channel case)
                timeSlice = stream['time_stamps'][fromSlice:toSlice]
                dataSlice = stream['time_series'][fromSlice:toSlice]

            axs[plotNr].grid(linestyle="--", alpha=0.5)
            axs[plotNr].plot(
                timeSlice, 
                dataSlice, 
                color=colors[i], 
                linewidth=0.5
            )
            axs[plotNr].set_title(stream['info']['name'][0])  # Add stream name as title

    # === Y-axis Label: Units if present ===
    if 'units' in stream['info']:
        axs[plotNr].set_ylabel(stream['info']['units'][0])

    plotNr += 1

plt.xlabel('Time (s)')  # Shared X-axis label

# === Slider Setup ===
# Add a horizontal slider to allow temporal navigation (window = 1 second)
axcolor = 'lightgoldenrodyellow'
axslider = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor=axcolor)
slider = Slider(
    axslider, 
    'Time', 
    data[0]['time_stamps'][0], 
    data[0]['time_stamps'][-1], 
    valinit=data[0]['time_stamps'][0]
)

# === Slider Update Function ===
def update(val):
    for i, stream in enumerate(data):
        time_min = max(val, data[i]['time_stamps'][0])
        time_max = min(val + 1, data[i]['time_stamps'][-1])  # Show a 1-second window
        axs[i].set_xlim(time_min, time_max)
    fig.canvas.draw_idle()

slider.on_changed(update)  # Bind the slider to the update function
plt.show()  # Display the interactive plot window

# === Marker Style Reference ===
# (Useful for customizing the marker appearance in plots)
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