

import os
#from moviepy.editor import VideoFileClip, concatenate_videoclips
import cv2

curfolder = os.getcwd()
# parent directory
parentfolder = os.path.dirname(curfolder)
print(parentfolder)
# get one folder above the parentfolder
mainfolder = os.path.dirname(parentfolder)
print(mainfolder)
calibInfolder = mainfolder + '\\data\\raw_data\\1\\Calibration\\checker_intrinsic\\'
#calibfolder = curfolder + '\\test_calib\\'
calibOutfolder = curfolder + '\\calib_output\\'
# outputfolder = curfolder + '\\output_test_calib\\'

# load in the calibration videos (avi)
videos = []
for file in os.listdir(calibInfolder):
    if file.endswith(".avi"):
        videos.append(os.path.join(calibInfolder, file))

# keep only those that have 6 in name
#videos = [x for x in videos if '0' in x]


# def split_camera_views(input_file, output_files):
#     video = VideoFileClip(input_file)

#     # Get the width and height of each camera view
#     width_per_camera = video.w // 3
#     height = video.h

#     # Split the video into three clips, one for each camera view
#     camera1_clip = video.subclip(0, video.duration).crop(x1=0, y1=0, x2=width_per_camera, y2=height)
#     camera2_clip = video.subclip(0, video.duration).crop(x1=width_per_camera, y1=0, x2=2 * width_per_camera, y2=height)
#     camera3_clip = video.subclip(0, video.duration).crop(x1=2 * width_per_camera, y1=0, x2=3 * width_per_camera, y2=height)

#     # Save each camera clip as a separate video file
#     camera1_clip.write_videofile(output_files[0], codec='rawvideo') #raw video is least prone to error when calibrating
#     camera2_clip.write_videofile(output_files[1], codec='rawvideo')
#     camera3_clip.write_videofile(output_files[2], codec='rawvideo')

#     # Close the video objects
#     video.reader.close()

def split_camera_views(input_file, output_files):
    cap = cv2.VideoCapture(input_file)

    # Get the width and height of each camera view
    num_cameras = 3
    width_per_camera = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // num_cameras
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # Create VideoWriters for each camera
    fourcc = cv2.VideoWriter_fourcc(*'RGBA')
    out_cam1 = cv2.VideoWriter(output_files[0], fourcc, frame_rate, (width_per_camera, height))
    out_cam2 = cv2.VideoWriter(output_files[1], fourcc, frame_rate, (width_per_camera, height))
    out_cam3 = cv2.VideoWriter(output_files[2], fourcc, frame_rate, (width_per_camera, height))

    while True:
        ret, frame = cap.read()

        # Check if the frame is None (end of video)
        if frame is None:
            break

        # Break the frame into three parts
        camera1_frame = frame[:, :width_per_camera, :]
        camera2_frame = frame[:, width_per_camera:2*width_per_camera, :]
        camera3_frame = frame[:, 2*width_per_camera:, :]

        # Display each camera view separately (optional)
        cv2.imshow('Camera 1', camera1_frame)
        cv2.imshow('Camera 2', camera2_frame)
        cv2.imshow('Camera 3', camera3_frame)

        # Write frames to video files
        out_cam1.write(camera1_frame)
        out_cam2.write(camera2_frame)
        out_cam3.write(camera3_frame)

        if cv2.waitKey(1) == 27:
            break

    # Release VideoWriters and VideoCapture
    out_cam1.release()
    out_cam2.release()
    out_cam3.release()
    cap.release()
    cv2.destroyAllWindows()


# loop over files in folder and split them
for file in videos:
    # Get the name of the file without the extension
    filename = os.path.splitext(os.path.basename(file))[0]

    sessionID = filename.split("_")[1] + "_" + filename.split("_")[2]
    # sessionID = filename.split("_")[2]

    # create an empty folder with name of the sessionIndex
    os.makedirs(os.path.join(calibOutfolder, sessionID))
    # inside this folder, create empty folder 'calibration'
    os.makedirs(os.path.join(calibOutfolder, sessionID, 'calibration'))
    # inside, make three folders: cam1, cam2, cam3
    os.makedirs(os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics', 'cam1')) # change to intrinsics if needed
    os.makedirs(os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics','cam2'))
    os.makedirs(os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics','cam3'))
    
    # Create the output file names
    output_files = [
        os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics','cam1', filename + '_cam1.avi'),
        os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics','cam2', filename + '_cam2.avi'),
        os.path.join(calibOutfolder, sessionID, 'calibration', 'extrinsics','cam3', filename + '_cam3.avi')
    ]
    # Split the camera views
    split_camera_views(file, output_files)