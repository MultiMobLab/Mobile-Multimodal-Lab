# Created by Sarka Kadava and Wim Pouw 


import cv2
import datetime
from pylsl import StreamInfo, StreamOutlet, local_clock
import threading
import time
import ctypes
import sys
import os
import ffmpegcv
# import signal
import tqdm

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


# def signal_handler(sig, frame):
#     print('Interrupt received. Stopping threads and releasing resources.')
#     camera_thread.join()
#     sys.exit(0)

# if __name__ == "__main__":
#     # Set up a signal handler to gracefully handle interrupt (Ctrl+C)
#     signal.signal(signal.SIGINT, signal_handler)

#     # Initialize the LSL threads
#     camera_thread = threading.Thread(target=getWebcamData, args=(cap1, cap2, cap3, video_writer))
#     camera_thread.start()

#     try:
#         sendLSLFrames(camera_thread)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Release the webcam resources
#         cap1.release()
#         cap2.release()
#         cap3.release()

#         # Close the display window
#         cv2.destroyAllWindows()


# recompress


# # Read the written video
# cap = cv2.VideoCapture(vidloc)

# # Get video information
# fps = cap.get(cv2.CAP_PROP_FPS)
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# # Specify the codec and create VideoWriter object for compressed video
# fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can change the codec as needed
# compressed_file_name = vidloc.replace('.avi', '_compr.avi')
# compressed_video_writer = cv2.VideoWriter(compressed_file_name, fourcc, fps, (frame_width, frame_height))

# # Display progress bar using tqdm
# for _ in tqdm.tqdm(range(total_frames), desc="Compressing Video", unit="frames"):
#     ret, frame = cap.read()
#     if not ret:
#         break
#     # Compress the frame (you can apply additional compression settings if needed)
#     compressed_frame = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)
#     # Write the compressed frame to the VideoWriter
#     compressed_video_writer.write(compressed_frame)

# # Release the VideoCapture and VideoWriter resources
# cap.release()
# compressed_video_writer.release()

# # Close the display window
# cv2.destroyAllWindows()