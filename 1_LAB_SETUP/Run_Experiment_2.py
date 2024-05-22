from psychopy import visual, core, event
import pandas as pd
import random
import csv
from pylsl import StreamInfo, StreamOutlet  
from rusocsci import buttonbox
import os
import json
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import numpy as np

## _________
#PARAMETERS
#Directories
input_dir = r"C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimulus\Data"  # Directory where audio files are stored
output_dir = r"C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimulus\Data\output"  # Directory to save the audio files played 

# List of audio files
audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]

# Conditions & Number of trials
conditions = ["Vision_Movement", "Vision_NoMovement", "NoVision_Movement", "NoVision_NoMovement"]
random.shuffle(conditions)  # Randomize the order of conditions
num_trials = 5

# Audio Files
audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]
num_audio_files = 20 # Total number of audio files
audio_duration = 5 # Total duration of each audio file (in seconds)

# Time between audio presentations (in seconds)
time_between_presentations = 2

# Time for participant singing (in seconds)
singing_duration = 10

# Time for the initial beep (in seconds)
initial_beep_duration = 2

# Time for the pause between initial beep and audio presentation (in seconds)
pause_duration = 1

# Button box configuration
bb = buttonbox.ButtonBox()

# Create LSL outlet
info = StreamInfo('AudioEvents', 'Markers', 1, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)

# Function to play an audio file
def play_audio(filename, condition, trial):
    # Send start of audio presentation event marker
    event_marker = f"{condition}_{trial}_StartAudioPresentation"
    outlet.push_sample([event_marker])

    # Load the audio file
    samplerate, data = read_audio(filename)
    # Play the audio
    sd.play(data, samplerate)
    # Wait until the audio is finished playing
    sd.wait()

# Function to read an audio file
def read_audio(filename):
    samplerate, data = wavfile.read(filename)
    return samplerate, data

# Function to play a beep sound
def play_beep(duration=2):
    # Generate a beep sound
    beep = np.sin(2 * np.pi * 1000 * np.arange(0, duration, 1/sample_rate))
    # Play the beep sound
    sd.play(beep, sample_rate)
    # Wait until the beep sound is finished playing
    sd.wait()

# Main loop for each condition
trial_data = []
for condition in conditions:
    print(f"Condition: {condition}")
    # Wait for button press to start the next condition
    print("Press button A to start the next condition...")
    bb.wait_button_press(buttons=['A'])
    print("Starting next condition...\n")

    for trial in range(1, num_trials + 1):
        print(f"Trial: {trial}")
        trial_info = {'Condition': condition, 'Trial': trial}

        # Send start of trial event marker
        event_marker = f"{condition}_{trial}_StartTrial"
        outlet.push_sample([event_marker])

        # Play initial beep
        play_beep(initial_beep_duration)

        # Pause after initial beep
        time.sleep(pause_duration)

        # Randomly select audio files for this trial
        selected_files = random.sample(audio_files, 5)
        trial_info['AudioFiles'] = selected_files

        # Play each audio file twice
        for idx, filename in enumerate(selected_files):
            for _ in range(2):
                # Play audio file
                play_audio(os.path.join(input_dir, filename), condition, trial)
                # Wait between presentations
                time.sleep(time_between_presentations)

        # Send start of participant singing event marker
        event_marker = f"{condition}_{trial}_StartParticipantSinging"
        outlet.push_sample([event_marker])

        # Play beep signaling start of participant singing
        play_beep()

        # Participant singing
        print("Participant singing...")
        time.sleep(singing_duration)

        # End of participant singing event marker
        event_marker = f"{condition}_{trial}_EndParticipantSinging"
        outlet.push_sample([event_marker])

        # End of trial beep
        play_beep()

        trial_data.append(trial_info)

        # Progress to the next trial after user input
        if trial < num_trials:
            input("Press Enter to start the next trial...")
        else:
            input("Press Enter to progress to the next condition...")

    print("\n")

# Save trial data to Excel
df = pd.DataFrame(trial_data)
df.to_excel(os.path.join(output_dir, 'trial_data.xlsx'), index=False)

print("Experiment finished!")
