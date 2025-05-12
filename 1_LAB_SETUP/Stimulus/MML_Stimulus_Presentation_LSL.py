#!/usr/bin/env python
"""
MOBILE MULTIMODAL LAB (MML): Stimulus Presentation LSL
-------------------------------------
This script runs a structured auditory stimulus presentation experiment.
It plays pre-generated audio files (e.g., melodies) organized across experimental conditions and repeated trials
For each condition: 
- User is asked to press a button to start 
For each trial:
- A beep signals the start
- Audio files are presented (each audio file is presented twice)
- LSL markers are sent to synchronize events (e.g., trial start, participant singing)


Outputs:
- An Excel log file of the audio files used in each trial 
- LSL event markers compatible with multimodal setups

Author: Davide Ahmar
Last edited: 10/05/2025
"""

from psychopy import visual, core, event  # PsychoPy visual & timing utilities (GUI optional here)
import pandas as pd  # For saving trial data
import random  # For randomizing trials/audio selection
import csv  # For possible CSV output (not used here)
from pylsl import StreamInfo, StreamOutlet  # LSL marker streaming
from rusocsci import buttonbox  # Button box support (Rusocsci box)
import os  # For file system ops
import json  # (not used in final version)
import sounddevice as sd  # For audio playback
from scipy.io.wavfile import write as write_wav, read as wavfile_read  # Audio file handling
import numpy as np  # For beep tone generation
import time  # For wait intervals

# ---------------- PARAMETERS ---------------- #

# Directories
input_dir = r"C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimuli\Data"  # Directory with stimulus audio
output_dir = r"C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimuli\Data\output"  # Log file output directory

# Get list of available audio files
audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]

# Experimental conditions (randomized)
conditions = ["Vision_Movement", "Vision_NoMovement", "NoVision_Movement", "NoVision_NoMovement"]
random.shuffle(conditions)
num_trials = 5  # Trials per condition

# Audio playback parameters
num_audio_files = 20  # Total available audio files (not used directly)
audio_duration = 5     # Duration of each audio file (sec)
time_between_presentations = 2  # Interval between two presentations (sec)
singing_duration = 10           # Time participant is expected to sing (sec)
initial_beep_duration = 2       # Initial attention beep before trial (sec)
pause_duration = 1              # Pause between beep and tone onset (sec)

# Initialize button box
bb = buttonbox.ButtonBox()

# Create LSL stream for event markers
info = StreamInfo('AudioEvents', 'Markers', 1, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)

# ---------------- HELPER FUNCTIONS ---------------- #

def read_audio(filename):
    """Read a WAV audio file and return its sample rate and data."""
    samplerate, data = wavfile_read(filename)
    return samplerate, data

def play_audio(filename, condition, trial):
    """Play audio file and send start marker to LSL."""
    event_marker = f"{condition}_{trial}_StartAudioPresentation"
    outlet.push_sample([event_marker])
    samplerate, data = read_audio(filename)
    sd.play(data, samplerate)
    sd.wait()

def play_beep(duration=2, frequency=1000, sample_rate=44100):
    """Generate and play a pure tone beep for signaling purposes."""
    beep = np.sin(2 * np.pi * frequency * np.arange(0, duration, 1/sample_rate))
    sd.play(beep, sample_rate)
    sd.wait()

# ---------------- EXPERIMENT LOOP ---------------- #
trial_data = []  # To store trial metadata

# Loop through each randomized condition
for condition in conditions:
    print(f"Condition: {condition}")
    print("Press button A to start the next condition...")
    bb.wait_button_press(buttons=['A'])  # Wait for manual confirmation
    print("Starting next condition...\n")

    for trial in range(1, num_trials + 1):
        print(f"Trial: {trial}")
        trial_info = {'Condition': condition, 'Trial': trial}

        # Send trial start marker
        event_marker = f"{condition}_{trial}_StartTrial"
        outlet.push_sample([event_marker])

        # Signal attention with beep
        play_beep(initial_beep_duration)
        time.sleep(pause_duration)

        # Randomly select 5 audio files from the pool
        selected_files = random.sample(audio_files, 5)
        trial_info['AudioFiles'] = selected_files

        # Each audio is played twice (e.g., for learning/repetition)
        for idx, filename in enumerate(selected_files):
            for _ in range(2):
                full_path = os.path.join(input_dir, filename)
                play_audio(full_path, condition, trial)
                time.sleep(time_between_presentations)

        # Marker: participant should begin singing
        event_marker = f"{condition}_{trial}_StartParticipantSinging"
        outlet.push_sample([event_marker])

        # Beep before singing
        play_beep()

        # Wait during singing phase
        print("Participant singing...")
        time.sleep(singing_duration)

        # Marker: end of singing
        event_marker = f"{condition}_{trial}_EndParticipantSinging"
        outlet.push_sample([event_marker])

        # Beep after singing (e.g., reset signal)
        play_beep()

        # Store trial info
        trial_data.append(trial_info)

        # Prompt user to proceed
        if trial < num_trials:
            input("Press Enter to start the next trial...")
        else:
            input("Press Enter to progress to the next condition...")
    print("\n")

# ---------------- SAVE DATA ---------------- #
df = pd.DataFrame(trial_data)
df.to_excel(os.path.join(output_dir, 'trial_data.xlsx'), index=False)
print("Experiment finished!")
