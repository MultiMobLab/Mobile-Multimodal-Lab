#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-
#!/usr/bin/env python

"""
MOBILE MULTIMODAL LAB (MML): AUDIO STREAMING SCRIPT FOR LSL
------------------------------------------------------
This script captures live audio using ALSA (Linux-only) and streams it to
Lab Streaming Layer (LSL), where it can be synchronized with other modalities
(e.g., video, physiology) in multimodal experiments.

Typical use case:
- Each participant wears a head-mounted mic
- MINIX Linux device auto-runs this script on boot
- Audio stream appears in LSL for recording/visualization

Requirements:
- Python 3
- pyalsa (alsaaudio), pylsl, numpy
- Linux OS with ALSA audio system

About the first lines (shebang):
- The line `#!/usr/bin/env python3` is called a shebang.
- It tells the operating system to run this script using Python 3 when launched directly from the terminal (e.g., `./script.py`).
- If commented out, it has no effect — the script can still be run via `python3 script.py`, but not directly.

Author: Technical Support Group (TSG), Donders Institute
Modified with full comments for educational/reproducibility purposes
Last Edited: 09/10/2025 by Davide Ahmar
"""

import alsaaudio  # For audio input from the ALSA system
import numpy as np  # To convert byte data into numerical arrays
import threading  # To run a background task for user input
import time  # For controlling loop speed
from pylsl import StreamInfo, StreamOutlet, local_clock  # LSL streaming

# ------------- CONFIGURATION SECTION ------------- #
# Stream parameters
STREAM_NAME = 'Mic'  # Name of the audio stream as it will appear in LSL
STREAM_TYPE = 'voice'  # Stream type for classification
CHANNEL_COUNT = 1  # Mono audio
SAMPLING_RATE = 16000  # Audio sampling rate in Hz
UNIQUE_SOURCE_ID = 'Microphone_stream'  # Unique ID to identify the stream
PERIOD_SIZE = 160  # Number of audio frames per read (~10ms of audio at 16kHz)

# ------------- LSL STREAM INITIALIZATION ------------- #
# Define metadata for the stream to be broadcast
info = StreamInfo(name=STREAM_NAME,
                  type=STREAM_TYPE,
                  channel_count=CHANNEL_COUNT,
                  nominal_srate=SAMPLING_RATE,
                  source_id=UNIQUE_SOURCE_ID)

# Create the LSL outlet for sending data chunks
outlet = StreamOutlet(info)

# ------------- AUDIO INPUT SETUP ------------- #
# Open default audio capture device in NON-BLOCKING mode
# This means the script will not pause if no audio is ready
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

# Set recording parameters
inp.setchannels(CHANNEL_COUNT)  # Mono channel
inp.setrate(SAMPLING_RATE)  # Set sample rate to 16 kHz
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)  # 16-bit little-endian format
inp.setperiodsize(PERIOD_SIZE)  # Frames per read

# ------------- THREAD TO STOP STREAMING ------------- #
running = True  # Global flag to control the loop

def ask_user():
    """
    Background thread that waits for user to press ENTER.
    When pressed, it stops the main loop.
    """
    global running
    input("Press ENTER to stop audio streaming...\n")
    running = False

# Start the user-input thread
threading.Thread(target=ask_user).start()

# ------------- MAIN LOOP ------------- #
# Continuously read audio chunks and send them over LSL
while running:
    # Read from the audio device
    length, data = inp.read()  # length = number of frames read, data = raw bytes
    timestamp = local_clock()  # LSL timestamp for the chunk

    if length:
        # Convert byte data to NumPy array of 16-bit integers
        audio_array = np.frombuffer(data, dtype=np.int16)

        # Push the audio chunk to LSL with timestamp
        outlet.push_chunk(audio_array, timestamp=timestamp)

    # Sleep briefly to avoid maxing out the CPU
    time.sleep(0.001)

# ------------- END OF SCRIPT ------------- #
print("Audio streaming stopped.")
