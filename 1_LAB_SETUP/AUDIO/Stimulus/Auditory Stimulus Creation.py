import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time
from scipy.io.wavfile import write as write_wav
import csv

# Parameters
total_duration = 5  # Total duration of the melody in seconds
note_duration = 1   # Duration of each note in seconds
sample_rate = 44100  # Sample rate in Hz
num_notes = 5       # Number of notes in the melody
min_pitch = 57      # Minimum MIDI pitch value
max_pitch = 69      # Maximum MIDI pitch value

# Convert MIDI pitch values to frequencies
def midi_to_frequency(midi_pitch):
    return 2 ** ((midi_pitch - 69) / 12) * 440

# Generate random melody notes
def generate_melody():
    return np.random.randint(min_pitch, max_pitch + 1, num_notes)

# Plot melody
def plot_melody(melody_notes):
    plt.figure()
    plt.plot(melody_notes, 'o-')
    plt.xlabel('Note Index')
    plt.ylabel('MIDI Pitch')
    plt.ylim(min_pitch -1, max_pitch+1)
    plt.title('Melody')
    plt.grid(True)
    plt.show(block=False)

# Generate and play back melodies
melodies_data = []
for i in range(1, 4):  # Generate 3 melodies
    print(f"Playing Melody {i}...")
    melody_notes = generate_melody()
    plot_melody(melody_notes)
    melody_waveform = np.zeros(total_duration * sample_rate)
    for j, note in enumerate(melody_notes):
        frequency = midi_to_frequency(note)
        t = np.linspace(0, note_duration, int(note_duration * sample_rate), endpoint=False)
        note_waveform = np.sin(2 * np.pi * frequency * t)
        start_idx = int(j * note_duration * sample_rate)
        end_idx = int((j + 1) * note_duration * sample_rate)
        melody_waveform[start_idx:end_idx] = note_waveform
    melody_waveform /= np.max(np.abs(melody_waveform))  # Normalize waveform
    sd.play(melody_waveform, samplerate=sample_rate)
    sd.wait()

    # Save melody waveform as an MP3 file
    mp3_filename = f"melody_{i}.mp3"
    write_wav(mp3_filename, sample_rate, (melody_waveform * 32767).astype(np.int16))
    print(f"Melody {i} saved as {mp3_filename}")

    # Save melody notes to CSV file
    csv_filename = f"melody_{i}.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Note Index", "MIDI Pitch"])
        for idx, note in enumerate(melody_notes):
            writer.writerow([idx, note])
    print(f"Melody {i} notes saved as {csv_filename}")

    # Append melody data to melodies_data list
    melodies_data.append({"Melody": i, "Notes": melody_notes, "Waveform": melody_waveform})

    # Ask user to replay or advance
    while True:
        choice = input("Press 'r' to replay the sound, or 'c' to continue to the next melody: ").lower()
        if choice == 'r':
            sd.play(melody_waveform, samplerate=sample_rate)
            sd.wait()
        elif choice == 'c':
            break
        else:
            print("Invalid input. Please enter 'r' to replay or 'c' to continue.")

# Save all melodies data as a CSV file
all_melodies_csv_filename = "all_melodies_data.csv"
with open(all_melodies_csv_filename, 'w', newline='') as csvfile:
    fieldnames = ["Melody", "Notes", "Waveform"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for melody_data in melodies_data:
        writer.writerow(melody_data)
print(f"All melodies data saved as {all_melodies_csv_filename}")
