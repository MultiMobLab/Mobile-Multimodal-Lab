#!/usr/bin/env python
"""
MOBILE MULTIMODAL LAB (MML): PLOT AUDIO STREAM from LSL
--------------------------------------
This script visualizes real-time data from a LabStreamingLayer (LSL) audio stream
called 'Mic'. It uses PyQtGraph for plotting, and supports both continuous data
(e.g. audio) and marker streams (event annotations).

Key Features:
- Pulls and displays LSL data from the 'Mic' stream.
- Plots multiple channels (if available) in real-time.
- Scrolls the view window to display the latest audio samples.

Requirements:
- pylsl
- numpy
- pyqtgraph

Note:
- This script does NOT record or save data. It is intended for real-time inspection.

Author: Dr. Wim Pouw
Last Edited: 09/05/2025 by Davide Ahmar
"""

import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from typing import List

# === Plot Configuration === #
plot_duration = 5        # seconds of data to display on screen
update_interval = 10     # how often to scroll the plot window (ms)
pull_interval = 10       # how often to pull data from LSL (ms)


class Inlet:
    """Base class for an LSL stream inlet that can be plotted."""
    def __init__(self, info: pylsl.StreamInfo):
        # Connect to LSL stream with dejitter and clock sync enabled
        self.inlet = pylsl.StreamInlet(
            info,
            max_buflen=plot_duration,
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter
        )
        self.name = info.name()
        self.channel_count = info.channel_count()

    def pull_and_plot(self, plot_time: float, plt: pg.PlotItem):
        """Method to be overridden by child classes."""
        pass


class DataInlet(Inlet):
    """Handles continuous numeric LSL data streams for plotting."""
    # Supported data types for each LSL channel format
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        # Pre-allocate a buffer for incoming data (twice plot size for margin)
        bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), info.channel_count())
        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])
        empty = np.array([])
        # Create line objects for each channel
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True)
                       for _ in range(self.channel_count)]
        for curve in self.curves:
            plt.addItem(curve)

    def pull_and_plot(self, plot_time, plt):
        # Pull data from the stream into our buffer
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                                      max_samples=self.buffer.shape[0],
                                      dest_obj=self.buffer)
        if ts:
            ts = np.asarray(ts)
            y = self.buffer[0:ts.size, :]
            this_x = None
            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                old_x, old_y = self.curves[ch_ix].getData()
                if ch_ix == 0:
                    # Only need to process timestamps once for all channels
                    old_offset = old_x.searchsorted(plot_time)
                    new_offset = ts.searchsorted(plot_time)
                    this_x = np.hstack((old_x[old_offset:], ts[new_offset:]))
                # Stack new data after trimming old data
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                self.curves[ch_ix].setData(this_x, this_y)


class MarkerInlet(Inlet):
    """Handles event marker LSL streams (e.g., from button presses or triggers)."""
    def __init__(self, info: pylsl.StreamInfo):
        super().__init__(info)

    def pull_and_plot(self, plot_time, plt):
        # Pull marker strings and timestamps
        strings, timestamps = self.inlet.pull_chunk(0)
        if timestamps:
            for string, ts in zip(strings, timestamps):
                # Add vertical lines for each marker event
                plt.addItem(pg.InfiniteLine(ts, angle=90, movable=False, label=string[0]))


def main():
    inlets: List[Inlet] = []
    print("Looking for LSL streams named 'Mic'...")

    # Resolve only streams with name 'Mic'
    streams = pylsl.resolve_stream('name', 'Mic')

    # Set up the PyQtGraph window
    pw = pg.plot(title='Microphone stream')
    plt = pw.getPlotItem()
    plt.enableAutoRange(x=False, y=True)

    # Create inlet handler objects based on stream type
    for info in streams:
        if info.type() == 'Markers' and info.nominal_srate() == pylsl.IRREGULAR_RATE \
                and info.channel_format() == pylsl.cf_string:
            print('Adding marker inlet: ' + info.name())
            inlets.append(MarkerInlet(info))
        elif info.nominal_srate() != pylsl.IRREGULAR_RATE \
                and info.channel_format() != pylsl.cf_string:
            print('Adding data inlet: ' + info.name())
            inlets.append(DataInlet(info, plt))
        else:
            print("Don't know what to do with stream: " + info.name())

    def scroll():
        """Scroll plot window to keep recent data in view."""
        fudge_factor = pull_interval * 0.002
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - plot_duration + fudge_factor, plot_time - fudge_factor)

    def update():
        """Pull and plot new data from each inlet."""
        mintime = pylsl.local_clock() - plot_duration
        for inlet in inlets:
            inlet.pull_and_plot(mintime, plt)

    # Create timers for scrolling and updating
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(update_interval)

    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(pull_interval)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
