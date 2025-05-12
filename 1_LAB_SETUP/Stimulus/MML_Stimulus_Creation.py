"""
MOBILE MULTIMODAL LAB (MML): AUDITORY STIMULUS CREATION SCRIPT
----------------------------------
This script generates synthetic auditory melodies composed of random MIDI notes.
Each melody:
- Is played back using `sounddevice`
- Is visualized as a plot of MIDI pitches
- Is saved as a `.wav` file (previously mislabeled as `.mp3`)
- Is logged in a `.csv` file including its note composition

The user can interactively replay each melody or continue to the next.

Our use:
- Generated stimuli to be used in our interpersonal singing experiment

Author: Davide Ahmar
Last edited: 10/05/2025
"""

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time
from scipy.io.wavfile import write as write_wav
import csv
import os

# ---------------------- PARAMETERS ---------------------- #
total_duration = 5        # Total melody duration in seconds
note_duration = 1         # Duration of each note (in seconds)
sample_rate = 44100       # Audio sampling rate (in Hz)
num_notes = 5             # Number of notes in each melody
min_pitch = 57            # Minimum MIDI pitch (A3)
max_pitch = 69            # Maximum MIDI pitch (A4)
output_dir = "generated_melodies"  # Folder where stimuli will be saved

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# -------------------- UTILITY FUNCTIONS ------------------ #

def midi_to_frequency(midi_pitch):
    """Convert a MIDI note value to frequency in Hz."""
    return 2 ** ((midi_pitch - 69) / 12) * 440

def generate_melody():
    """Generate a random melody of MIDI notes."""
    return np.random.randint(min_pitch, max_pitch + 1, num_notes)

def plot_melody(melody_notes, melody_id):
    """Plot MIDI note values as a line graph."""
    plt.figure()
    plt.plot(melody_notes, 'o-', label=f"Melody {melody_id}")
    plt.xlabel('Note Index')
    plt.ylabel('MIDI Pitch')
    plt.ylim(min_pitch - 1, max_pitch + 1)
    plt.title(f'Melody {melody_id}')
    plt.grid(True)
    plt.legend()
    plt.show(block=False)

# ------------------ GENERATE MELODIES ------------------- #
melodies_data = []

for i in range(1, 4):  # Generate 3 melodies
    print(f"\nGenerating Melody {i}...")
    melody_notes = generate_melody()  # Create random melody
    plot_melody(melody_notes, i)      # Show pitch sequence

    # Initialize an empty waveform
    melody_waveform = np.zeros(int(total_duration * sample_rate))

    # Generate waveform note by note
    for j, note in enumerate(melody_notes):
        frequency = midi_to_frequency(note)
        t = np.linspace(0, note_duration, int(note_duration * sample_rate), endpoint=False)
        note_waveform = np.sin(2 * np.pi * frequency * t)
        start_idx = int(j * note_duration * sample_rate)
        end_idx = int((j + 1) * note_duration * sample_rate)
        melody_waveform[start_idx:end_idx] = note_waveform

    # Normalize waveform to prevent clipping
    melody_waveform /= np.max(np.abs(melody_waveform))

    # Play back the melody
    sd.play(melody_waveform, samplerate=sample_rate)
    sd.wait()

    # ----------------- SAVE MELODY FILES ------------------ #
    wav_filename = os.path.join(output_dir, f"melody_{i}.wav")
    csv_filename = os.path.join(output_dir, f"melody_{i}.csv")

    # Save waveform as .wav (16-bit PCM)
    write_wav(wav_filename, sample_rate, (melody_waveform * 32767).astype(np.int16))
    print(f"Saved audio to: {wav_filename}")

    # Save MIDI notes to CSV
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Note Index", "MIDI Pitch"])
        for idx, note in enumerate(melody_notes):
            writer.writerow([idx, note])
    print(f"Saved note data to: {csv_filename}")

    # Append for metadata export
    melodies_data.append({"Melody": i, "Notes": list(melody_notes)})

    # ------------- USER INTERACTION (Replay/Continue) ------------- #
    while True:
        choice = input("Press 'r' to replay the sound, or 'c' to continue to the next melody: ").lower()
        if choice == 'r':
            sd.play(melody_waveform, samplerate=sample_rate)
            sd.wait()
        elif choice == 'c':
            break
        else:
            print("Invalid input. Please enter 'r' to replay or 'c' to continue.")

# --------------- SAVE METADATA ACROSS MELODIES --------------- #
metadata_csv = os.path.join(output_dir, "all_melodies_data.csv")
with open(metadata_csv, 'w', newline='') as csvfile:
    fieldnames = ["Melody", "Notes"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for melody_data in melodies_data:
        writer.writerow(melody_data)
print(f"\nAll metadata saved to: {metadata_csv}")

