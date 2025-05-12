#!/usr/bin/env python
"""
MOBILE MULTIMODAL LAB (MML): VIDEO STREAMING 3 CAMERAS to LSL
------------------------------------------------------
This script captures synchronized video from **three webcams** and performs:

1. Live **frame combination and preview** using OpenCV.
2. **Real-time recording** of combined frames to disk using `ffmpegcv`.
3. **Streaming of frame counters** to Lab Streaming Layer (LSL) for precise synchronization with other modalities (e.g., audio, physiology).

Typical use case:
- The webcams are mounted on an arch around a participant.
- This script runs on a Windows PC, opening three camera devices.
- It saves a compressed `.avi` video file and simultaneously streams frame numbers at a fixed frequency to LSL.

Key Features:
- Video frame synchronization across cameras using `grab()`/`retrieve()` for increased frame stability.
- Real-time LSL frame counter streaming using the stream name: `'MyWebcamFrameStream'`.
- GUI preview of the live video using OpenCV (`cv2.imshow`).
- User is asked to enter their ID via terminal input. This is used to name the output file.
- The video is saved automatically in a subfolder called `data/` located in the current working directory.
- Recording can be terminated by pressing the **'q' key** during the preview.

Requirements:
- Python 3
- OpenCV (`cv2`), ffmpegcv, pylsl, tqdm (optional for compression)
- Windows OS (uses `cv2.CAP_DSHOW` and `ctypes.WinDLL`)

Note:
- Audio is **not** recorded.
- Camera indices may need to be adjusted manually in `cams = [3, 2, 0]`.

Authors: Dr. Wim Pouw & Šárka Kadavá
Last Edited: 10/05/2025 by Davide Ahmar
    * this script uses the stabilized version of read_frames function with grab/retrieve to avoid frame drops

"""

import cv2  # OpenCV for video capture and display
import datetime  # For timestamping the video file
from pylsl import StreamInfo, StreamOutlet, local_clock  # LSL functions for streaming frame count
import threading  # For running simultaneous LSL stream in parallel
import time  # To manage sleep timing
import ctypes  # Required to improve Windows timer resolution
import sys  # To access system info (like Python version)
import os  # To construct file paths
import ffmpegcv  # Fast video recording with ffmpeg backend
# import signal  # Optional clean-up on interrupt
import tqdm  # Optional: progress bar for video recompression

# --- Camera configuration --- #
cams = [3, 2, 0]  # Device indices for the three cameras (may vary by system)

# Improve sleep accuracy to 1ms on Windows
# This helps with timing precision when looping at high frequency
winmm = ctypes.WinDLL('winmm')
winmm.timeBeginPeriod(1)


# Ask user for participant ID and build output filename
pcn_id = input('Enter ID: ')   # used to personalize the video file name
time_stamp = datetime.datetime.now().strftime('%Y-%m-%d')  # Get current date in the format YYYY-MM-DD (used for timestamping)
file_name = pcn_id + '_' + time_stamp + '_output.avi'      # Construct the filename using ID and date, e.g., "P001_2025-05-10_output.avi"
vidloc = os.getcwd() + '\\data\\' + file_name              # Build the full path for saving the video inside a "data" folder in the current working directory
print('Data will be saved in: ' + vidloc)


# --- LSL setup --- #
freq = 500  # Number of LSL samples (frame counters) sent per second
frame_rate = 200.0  # Target frame rate for video acquisition (~60 fps max)
frame_counter1, frame_counter2, frame_counter3 = 1, 1, 1  # Initialize counters for each camera stream

# Create the LSL stream outlet for broadcasting frame counters
stream_info = StreamInfo(name='MyWebcamFrameStream', type='frameNR', channel_count=1,
                         channel_format='int32', nominal_srate=freq, source_id='MyWebcamFrameStream')
outlet = StreamOutlet(stream_info)

# --- Open cameras --- #
def open_cameras():
    """Opens three webcam devices using DirectShow backend."""
    cap1 = cv2.VideoCapture(cams[0], cv2.CAP_DSHOW)
    # cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Camera 1 opened")
    cap2 = cv2.VideoCapture(cams[1], cv2.CAP_DSHOW)
    # cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Camera 2 opened")
    cap3 = cv2.VideoCapture(cams[2], cv2.CAP_DSHOW)
    # cap3.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Camera 3 opened")
    return cap1, cap2, cap3

# --- Read synchronized frames from 3 cameras --- # (this grab/retrive method is used to avoid frame drops)
def read_frames(cap1, cap2, cap3):
    """Grabs and retrieves synchronized frames from all three cameras."""
    # Camera 1
    grabbed = cap1.grab()
    if grabbed:
        ret1, frame1 = cap1.retrieve()
        if not ret1:
            print("Can't receive frame from camera one. Exiting...")
            return [-1]

    # Camera 2
    grabbed = cap2.grab()
    if grabbed:
        ret2, frame2 = cap2.retrieve()
        if not ret2:
            print("Can't receive frame from camera two. Exiting...")
            return [-1]

    # Camera 3
    grabbed = cap3.grab()
    if grabbed:
        ret3, frame3 = cap3.retrieve()
        if not ret3:
            print("Can't receive frame from camera three. Exiting...")
            return [-1]

    return [frame1, frame2, frame3]

# --- Combine frames and overlay counters and framerate --- #
def combine_frames(frame1, frame2, frame3, framerate):
    """Rotates, annotates, resizes, and combines video frames for display and saving."""
    # Rotate each frame vertically (portrait mode)
    frame1 = cv2.rotate(frame1, cv2.ROTATE_90_CLOCKWISE)
    frame2 = cv2.rotate(frame2, cv2.ROTATE_90_CLOCKWISE)
    frame3 = cv2.rotate(frame3, cv2.ROTATE_90_CLOCKWISE)

    # Overlay frame number text
    cv2.putText(frame1, str(frame_counter1), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    cv2.putText(frame2, str(frame_counter2), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    cv2.putText(frame3, str(frame_counter3), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

    # Add FPS estimate once enough frames have passed
    if frame_counter1 >= 1001:
        cv2.putText(frame1, 'fps: ' + str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame2, 'fps: ' + str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame3, 'fps: ' + str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

    # Resize frames for display window (smaller version)
    frame1_dis = cv2.resize(frame1, (240, 426), interpolation=cv2.INTER_LINEAR)
    frame2_dis = cv2.resize(frame2, (240, 426), interpolation=cv2.INTER_LINEAR)
    frame3_dis = cv2.resize(frame3, (240, 426), interpolation=cv2.INTER_LINEAR)

    # Combine full-resolution and display-sized frames side by side
    combined_frames = cv2.hconcat([frame1, frame2, frame3])
    combined_frames_dis = cv2.hconcat([frame1_dis, frame2_dis, frame3_dis])

    return combined_frames, combined_frames_dis

# --- Capture and record video while displaying and updating counters --- #
def getWebcamData(cap1, cap2, cap3, video_writer):
    """Main loop that reads frames, overlays metadata, displays, and saves video."""
    global frame_counter1, frame_counter2, frame_counter3
    prev = 0
    framecounter_fr = 0  # Used to estimate framerate
    running_framerate = 0

    while True:
        # Read frames from all three cameras
        frames = read_frames(cap1, cap2, cap3)
        if len(frames) == 1:
            break  # Exit if error reading any camera
        frame1, frame2, frame3 = frames

        # Throttle frame rate
        time_elapsed = time.time() - prev
        if time_elapsed > 1. / frame_rate:
            prev = time.time()

            # Increment frame counters
            frame_counter1 += 1
            frame_counter2 += 1
            frame_counter3 += 1

            # Estimate FPS after warm-up
            if frame_counter1 == 1000:
                framecounter_fr += 1
                timegetfor_fr = time.time()
            elif frame_counter1 >= 1001:
                framecounter_fr += 1
                timepassed_fr = timegetfor_fr - time.time()
                running_framerate = abs(round(framecounter_fr / timepassed_fr, 2))

            # Overlay text and concatenate frames
            combined_frames, combined_frames_dis = combine_frames(frame1, frame2, frame3, running_framerate)

            # Save and display
            video_writer.write(combined_frames)
            cv2.imshow('Webcam Streams', combined_frames_dis)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release hardware and close windows
    video_writer.release()
    cap1.release()
    cap2.release()
    cap3.release()
    cv2.destroyAllWindows()

# --- LSL thread that sends frame counters --- #
def sendLSLFrames(camera_thread):
    """
    Continuously streams the current frame counter (frame_counter1) to LSL
    at the rate defined by `freq`, until the main camera thread ends.
    """
    stamp = local_clock()  # initialize first LSL timestamp
    while camera_thread.is_alive():  # keep streaming until main video thread ends
        time.sleep(0.001)  # sleep briefly to avoid busy-waiting
        while local_clock() < stamp:
            pass  # wait until next target timestamp
        stamp = local_clock() + (1.0 / freq)  # set time for next frame
        outlet.push_sample([frame_counter1])  # send the frame counter

# --- Start Script Execution --- #
print(sys.version)  # Print Python version for diagnostics
print("Starting LSL webcam")
print("Press 'q' to stop recording")
cap1, cap2, cap3 = open_cameras()  # Open the cameras


# Initialize the video writer
video_writer = ffmpegcv.VideoWriter(vidloc, 'rawvideo', 60)  # 'rawvideo' or 'h264'
#video_writer  = ffmpegcv.noblock(ffmpegcv.VideoWriter, vidloc, 'h264', 60)  # optional non-blocking mode

# Start recording and LSL in parallel threads
camera_thread = threading.Thread(target=getWebcamData, args=(cap1, cap2, cap3, video_writer))
camera_thread.start()
sendLSLFrames(camera_thread)  # start LSL push loop

print("Stop")

# --- Optional Ctrl+C interrupt handler (commented) --- #
# def signal_handler(sig, frame):
#     print('Interrupt received. Stopping threads and releasing resources.')
#     camera_thread.join()
#     sys.exit(0)
#
# if __name__ == "__main__":
#     signal.signal(signal.SIGINT, signal_handler)
#     camera_thread = threading.Thread(target=getWebcamData, args=(cap1, cap2, cap3, video_writer))
#     camera_thread.start()
#     try:
#         sendLSLFrames(camera_thread)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         cap1.release()
#         cap2.release()
#         cap3.release()
#         cv2.destroyAllWindows()

# --- Optional: Recompression section (commented) --- #
# cap = cv2.VideoCapture(vidloc)
# fps = cap.get(cv2.CAP_PROP_FPS)
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# compressed_file_name = vidloc.replace('.avi', '_compr.avi')
# compressed_video_writer = cv2.VideoWriter(compressed_file_name, fourcc, fps, (frame_width, frame_height))
# for _ in tqdm.tqdm(range(total_frames), desc="Compressing Video", unit="frames"):
#     ret, frame = cap.read()
#     if not ret:
#         break
#     compressed_frame = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)
#     compressed_video_writer.write(compressed_frame)
# cap.release()
# compressed_video_writer.release()
# cv2.destroyAllWindows()
