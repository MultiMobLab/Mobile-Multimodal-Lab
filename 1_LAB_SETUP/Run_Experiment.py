### Loading PACKAGES ###
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
from pylsl import StreamInfo, StreamOutlet  
from rusocsci import buttonbox



## _________
#PARAMETERS
#Directories
input_dir = "C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimulus\Data"  # Directory where audio files are stored
output_dir = "C:\Users\ahmar\OneDrive\Documents\GitHub\Mobile-Multimodal-Lab\1_LAB_SETUP\Stimulus\Data\output"  #Directory to save the audio files played 

# List of audio files
audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]

# Conditions & Number of trials
conditions = ["Vision_Movement", "Vision_NoMovement", "NoVision_Movement", "NoVision_NoMovement"]
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


## BUTTON BOX
# initiate button box
bb = buttonbox.Buttonbox()


## FUNCTIONS 
# Function to play an audio file
def play_audio(filename):
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
for condition in conditions:
    print(f"Condition: {condition}")
    for trial in range(1, num_trials + 1):
        print(f"Trial: {trial}")

        # Play initial beep
        play_beep(initial_beep_duration)

        # Pause after initial beep
        time.sleep(pause_duration)

        # Randomly select audio files for this trial
        selected_files = random.sample(audio_files, 5)

        # Play each audio file twice
        for filename in selected_files:
            for _ in range(2):
                # Play audio file
                play_audio(os.path.join(input_dir, filename))
                # Wait between presentations
                time.sleep(time_between_presentations)

        # Play beep signaling start of participant singing
        play_beep()

        # Participant singing
        print("Participant singing...")
        time.sleep(singing_duration)

        # End of trial beep
        play_beep()

        # Progress to the next trial after user input
        if trial < num_trials:
            input("Press Enter to start the next trial...")
        else:
            input("Press Enter to progress to the next condition...")

    print("\n")

print("Experiment finished!")


