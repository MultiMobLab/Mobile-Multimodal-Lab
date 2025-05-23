import os
import cv2

# currect folder
curfolder = os.getcwd()
# parent directory
parentfolder = os.path.dirname(curfolder)
print(parentfolder)

# videodata 
videodata = parentfolder + '\\2_PREPROCESSING\\1_XDF_PROCESSING\\video_clipped'
outputfolder = curfolder + '\\projectdata\\'

# collect all videos
videos = []
for file in os.listdir(videodata):
    if file.endswith(".avi"):
        videos.append(os.path.join(videodata, file))

print(videos)

def split_camera_views(input_file, output_files):
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {input_file}")
        return

    num_cameras = 3
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    width_per_camera = int(width // num_cameras)

    if width == 0 or height == 0:
        print(f"Error: Invalid video dimensions in {input_file}")
        cap.release()
        return

    print(f"Processing {input_file} with width: {width}, height: {height}, FPS: {frame_rate}")

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_cam1 = cv2.VideoWriter(output_files[0], fourcc, frame_rate, (width_per_camera, height))
    out_cam2 = cv2.VideoWriter(output_files[1], fourcc, frame_rate, (width_per_camera, height))
    out_cam3 = cv2.VideoWriter(output_files[2], fourcc, frame_rate, (width_per_camera, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        camera1_frame = frame[:, :width_per_camera]
        camera2_frame = frame[:, width_per_camera:2*width_per_camera]
        camera3_frame = frame[:, 2*width_per_camera:]

        out_cam1.write(camera1_frame)
        out_cam2.write(camera2_frame)
        out_cam3.write(camera3_frame)

    cap.release()
    out_cam1.release()
    out_cam2.release()
    out_cam3.release()


# loop over files in folder and split them
for file in videos:
    print("working on file: "+file)
    # Get the name of the file without the extension
    filename = os.path.splitext(os.path.basename(file))[0]
    nameparts = filename.split("_")

    # this is session
    sessionID = filename.split("_")[0] + "_" + filename.split("_")[3] # This is how sessionID is defined

    # this is future filename
    videoname = filename.split("_")[0] + "_" + filename.split("_")[3] + "_" + filename.split("_")[4] + "_" + filename.split("_")[5] + "_" + filename.split("_")[6] 
    print('sessionID: ' + sessionID)

    # if a folder with the sessionIndex does not exist, create it
    if not os.path.exists(os.path.join(outputfolder, sessionID)):
        os.makedirs(os.path.join(outputfolder, sessionID))    

    # create the next folder either in p0 or p1, depending on whether p1/p0 is in the filename
    if 'P1' in filename:
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p1data')):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p1data'))
        # inside this folder, create empty folder 'raw-2d'
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p1data', videoname)):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p1data', videoname))

        # create folder with the name of the file
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p1data', videoname, 'raw-2d')):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p1data', videoname, 'raw-2d'))


        output_files = [
            os.path.join(outputfolder, sessionID, 'p1data', videoname, 'raw-2d', videoname + '_cam1.avi'),
            os.path.join(outputfolder, sessionID, 'p1data', videoname, 'raw-2d', videoname + '_cam2.avi'),
            os.path.join(outputfolder, sessionID, 'p1data', videoname, 'raw-2d', videoname + '_cam3.avi')
        ]

    elif 'P2' in filename:
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p2data')):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p2data'))
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p2data', videoname)):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p2data', videoname))
        if not os.path.exists(os.path.join(outputfolder, sessionID, 'p2data', videoname, 'raw-2d')):
            os.makedirs(os.path.join(outputfolder, sessionID, 'p2data', videoname, 'raw-2d'))

        output_files = [
            os.path.join(outputfolder, sessionID, 'p2data', videoname, 'raw-2d', videoname + '_cam1.avi'),
            os.path.join(outputfolder, sessionID, 'p2data', videoname, 'raw-2d', videoname + '_cam2.avi'),
            os.path.join(outputfolder, sessionID, 'p2data', videoname, 'raw-2d', videoname + '_cam3.avi')
        ]

    else:
        print('Participant not found')

    print(output_files)
    # Split the camera views
    split_camera_views(file, output_files)

