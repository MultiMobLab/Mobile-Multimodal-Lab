## THREE_WEBCAMS_LSL
        # Author: sarkadava     
        # Last date modified: 01-04-2024
   
    # SUMMARY            
        # Python code that allows real-time capture and streaming of video data from three different cameras, 
        # along with integration with LabStreamingLayer (LSL) for synchronization and data streaming.
    
    # Before running the code: 
        # Ensure that all the libraries have been installed. To do so, Open Conda Prompt and navigate to the code's directory (where there should be a requirements.txt file). Once there, use the following command: conda install --yes --file requirements.txt
        # In the PARAMETERS, adjust the following: 
        #      cams: specify the correct camera IDs based on your system configuration.
        #      freq: depending on your acquisition frequency 
        #      frame_rate: "
        #      vidloc: output file location
    
       

## IMPORTING LIBRARIES & MODULES
import cv2  # cv2 library (old OpenCV) for handling video capture and processing
import datetime  # datetime module for timestamping
from pylsl import StreamInfo, StreamOutlet, local_clock  # Functions from pylsl for LabStreamingLayer (LSL)
import threading  # threading module for multithreading
import time  # time module for time-related functions
import ctypes  # ctypes module for C data types and calling functions in DLLs
import sys  # Import sys module for system-specific parameters and functions
import os  # Import os module for interacting with the operating system
import ffmpegcv  # Import ffmpegcv module for video writing
import tqdm  # Import tqdm module for progress bars


## PARAMETERS 
cams = [3, 2, 0] # change if cameras don't work

#LABSTREAMLAYER:
# stream the framenumbers to the LSL (see webcam LSL script)
# run for hour
print(sys.version)
#set sleep to 1ms accuracy
winmm = ctypes.WinDLL('winmm')
winmm.timeBeginPeriod(1)

#LABSTREAMLAYER: Setup streaming capture device
# def sendLSLFrames(camera_thread):
def sendLSLFrames(camera_thread):
    stamp = local_clock()
    while camera_thread.is_alive():
        time.sleep(0.001)
        while local_clock() < stamp:
            pass
        stamp = local_clock() + (1.0/freq)
        outlet.push_sample([frame_counter1])#, local_clock())

#log info

def log_combined_frames_info(combined_frames):
    print(f"Shape: {combined_frames.shape}")


# Opens the three cameras and returns as variables
def open_cameras():
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

# Main camera function
def getWebcamData(cap1, cap2, cap3, video_writer):
    global frame_counter1
    global frame_counter2
    global frame_counter3

    prev = 0
    framecounter_fr = 0
    running_framerate = 0
    # Main camera loop
    while True:
        # Read frames from each webcam stream
        frames = read_frames(cap1, cap2, cap3)
        if len(frames) == 1: # If read_frames returned error code, break main loop
            break
        frame1, frame2, frame3 = frames
        
        # Added to make sure that cams are synchronized
        time_elapsed = time.time() - prev
        if time_elapsed > 1. / frame_rate:
            prev = time.time()
            #LABSTREAMLAYER:
            frame_counter1 += 1
            frame_counter2 += 1
            frame_counter3 += 1
            
            # Estimate the frame rate after some initial ramp up phase
            if frame_counter1 == 1000:
                framecounter_fr += 1
                timegetfor_fr = time.time()
            elif frame_counter1 >= 1001:
                framecounter_fr += 1
                timepassed_fr = timegetfor_fr - time.time()
                running_framerate = abs(round(framecounter_fr / timepassed_fr, 2))

            # Combine frames for display and VideoWriter
            combined_frames, combined_frames_dis = combine_frames(frame1, frame2, frame3, running_framerate)

            # log_combined_frames_info(combined_frames)

            # Write combined frames to the VideoWriter
            video_writer.write(combined_frames)
   
            # Display the combined frames
            cv2.imshow('Webcam Streams', combined_frames_dis)

            # print(video_writer.ffmpeg_cmd)

            # Check for the 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video_writer.release()

    # Release the webcam resources
    cap1.release()
    cap2.release()
    cap3.release()

    # Close the display window
    cv2.destroyAllWindows()


# Read frames from 3 cameras, returns list of either frames or error code
def read_frames(cap1, cap2, cap3):
    ret1, frame1 = cap1.read() # Read frame camera one
    if not ret1:
        print("Can't receive frame from camera one. Exiting...")
        return [-1]
    ret2, frame2 = cap2.read() # Read frame camera two
    if not ret2:
        print("Can't receive frame from camera two. Exiting...")
        return [-1]
    ret3, frame3 = cap3.read() # Read frame camera three
    if not ret3:
        print("Can't receive frame from camera three. Exiting...")
        return [-1]
    return [frame1, frame2, frame3]


# Combines frames to instances for display and video writer, returns instances
def combine_frames(frame1, frame2, frame3, framerate):
    # Rotate the frames
    frame1 = cv2.rotate(frame1, cv2.ROTATE_90_CLOCKWISE) # Rotate image
    frame2 = cv2.rotate(frame2, cv2.ROTATE_90_CLOCKWISE) # Rotate image
    frame3 = cv2.rotate(frame3, cv2.ROTATE_90_CLOCKWISE) # Rotate image

    # Add info to show on screen
    cv2.putText(frame1, str(frame_counter1), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    cv2.putText(frame2, str(frame_counter2), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    cv2.putText(frame3, str(frame_counter3), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    # Show FPS after initial ramp up phase
    if frame_counter1 >= 1001:
        cv2.putText(frame1, 'fps: '+ str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame2, 'fps: '+str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame3, 'fps: '+str(framerate), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    
    # Resize the frames for display
    frame1_dis = cv2.resize(frame1, (240, 426), interpolation=cv2.INTER_LINEAR) # this resize results in the highest fps
    frame2_dis = cv2.resize(frame2, (240, 426), interpolation=cv2.INTER_LINEAR)
    frame3_dis = cv2.resize(frame3, (240, 426), interpolation=cv2.INTER_LINEAR)

    # Combine frames horizontally
    combined_frames = cv2.hconcat([frame1, frame2, frame3])
    combined_frames_dis = cv2.hconcat([frame1_dis, frame2_dis, frame3_dis])

    return combined_frames, combined_frames_dis

################ LABSTREAMLAYER INPUTS ################
freq = 500
frame_rate = 200.0 # when it's set on 60, the max fps we get is around 40, if on 200, we get to 60
# frame_width = 2160
# frame_height = 1280
data_size = 20
stream_info = StreamInfo(name='MyWebcamFrameStream', type='frameNR', channel_count=1, channel_format='int32', nominal_srate = freq, source_id='MyWebcamFrameStream')
outlet = StreamOutlet(stream_info)  # Broadcast the stream. 

################ Execute LSL threading ################
# Initialize global frame counters
frame_counter1, frame_counter2, frame_counter3 = 1, 1, 1

# Open the default webcam devices
print("Starting LSL webcam")
cap1, cap2, cap3 = open_cameras()


# Specify file location of output
pcn_id = input('Enter ID: ')
time_stamp = datetime.datetime.now().strftime('%Y-%m-%d')
file_name = pcn_id + '_' + time_stamp + '_output.avi'
vidloc = os.getcwd() + '\\data\\' + file_name # Specify output location
print('Data saved in: ' + vidloc)

# Set up the VideoWriter
video_writer = ffmpegcv.VideoWriter(vidloc, 'rawvideo', 60) # other settings 'rawvideo' lowres 60 highres 55 'h264' 45 highres 60 lowres 
#video_writer  = ffmpegcv.noblock(ffmpegcv.VideoWriter, vidloc, 'h264', 60)

# Initialize the LSL threads
camera_thread = threading.Thread(target=getWebcamData, args=(cap1, cap2, cap3, video_writer))
camera_thread.start()
sendLSLFrames(camera_thread)


# Notify when program has concluded
print("Stop")