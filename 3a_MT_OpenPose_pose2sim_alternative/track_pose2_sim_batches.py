from Pose2Sim import Pose2Sim
import os
import subprocess
import glob
import pandas as pd
from trc import TRCData
import os
import pandas as pd
import shutil
import cv2
import numpy as np
import toml

curfolder = os.getcwd()
# what is the folder structure
pose2simprjfolder = r'C:\Users\kadava\Documents\GitHub\FLESH_3Dtracking_new\Pose2Sim\Empty_project_ENVISION_settings'
# here are stored dara
inputfolders = curfolder+'/projectdata/'
# in this folder are all the sessions
folderstotrack = glob.glob(curfolder+'/projectdata/*')

print(folderstotrack)
# keep only Session_0_1
#folderstotrack = [x for x in folderstotrack if 'Session_0_1' in x]

# toml handling function

def load_toml(file_path):
    with open(file_path, 'r') as file:
        return toml.load(file)

def save_toml(data, file_path):
    with open(file_path, 'w') as file:
        toml.dump(data, file)

def update_participant_info(toml_data, height, mass):
    if 'markerAugmentation' in toml_data:
        toml_data['markerAugmentation']['participant_height'] = height
        toml_data['markerAugmentation']['participant_mass'] = mass
    else:
        raise KeyError("The key 'markerAugmentation' is not present in the TOML data.")
    return toml_data


# test only first video
# folderstotrack = folderstotrack[0]

# Now we need to gather both participants in our one session

# initiate empty list
pcnfolders = []

for i in folderstotrack:
    # get the data folder
    pcnfolder = glob.glob(i + '/*data*/*')
    pcnfolder = [x for x in pcnfolder if 'Config' not in x]
    pcnfolder = [x for x in pcnfolder if 'opensim' not in x]
    print(pcnfolder)
    # append
    pcnfolders.append(pcnfolder[0])


# get out of pcnfolders all that contains Config and opensim
pcnfolders = [x for x in pcnfolders if 'Config' not in x]
pcnfolders = [x for x in pcnfolders if 'opensim' not in x]
# get rid of all potential folders/files that might be confusing
# pcnfolders = [x for x in pcnfolders if 'xml' not in x]
# pcnfolders = [x for x in pcnfolders if 'ResultsInverseDynamics' not in x]
# pcnfolders = [x for x in pcnfolders if 'ResultsInverseKinematics' not in x]
# pcnfolders = [x for x in pcnfolders if 'sto' not in x]
pcnfolders = [x for x in pcnfolders if 'txt' not in x]

print('pcnfolders:', pcnfolders)

# set framerate
framerate = 60

# How many xth frame do we extract from the calibration video? 
framepick = 3

# copy a folder in pose2simprjfolder and its contents to folders
source1 = pose2simprjfolder+'/Config.toml'
source2 = pose2simprjfolder+'/opensim/'

print(folderstotrack)
for i in folderstotrack:
    print('working on: ', i)

    os.chdir(i)
    trialfolder = glob.glob(i + '/*data*')
    print('trialfolder: ', trialfolder)

    # copy to session folder
    #if not os.path.exists(i+'/Config.toml'):
    shutil.copy(source1, i + '/')

    print('source = ' + source1 + ' to destination: ' + i+'/')

    # copy it also to trial folder
    shutil.copy(source1, trialfolder[0] + '/')

    print('source = ' + source1 + ' to destination: ' + trialfolder[0]+'/')

    
    if not os.path.exists(i+'/opensim/'):
        shutil.copytree(source2, trialfolder[0]+'/opensim/')

    print('source = ' + source2 + ' to destination: ' + trialfolder[0]+'/opensim/')

    # input_toml = load_toml(i+'/Config.toml')

    # # update the p0 info
    # mass_p0 = i + '/P0/mass.txt'
    # height_p0 = i + '/P0/height.txt'
    # with open(mass_p0, 'r') as file:
    #     mass_p0 = float(file.read())
    # with open(height_p0, 'r') as file:
    #     height_p0 = float(file.read())

    # updated_toml_p0 = update_participant_info(input_toml, height_p0, mass_p0)

    # update p1 info
    # mass_p1 = i + '/P1/mass.txt'
    # height_p1 = i + '/P1/height.txt'
    # with open(mass_p1, 'r') as file:
    #     mass_p1 = float(file.read())
    # with open(height_p1, 'r') as file:
    #     height_p1 = float(file.read())
    # updated_toml_p1 = update_participant_info(input_toml, height_p1, mass_p1)
    
    # save the updated TOML data
    # save_toml(updated_toml_p0, i+'/P0/Config.toml')
    # save_toml(updated_toml_p1, i+'/P1/Config.toml')

    # p0_source = i+'/P0/Config.toml'
    # p1_source = i+'/P1/Config.toml'

    # # copy to participant folder
    # if not os.path.exists(i+'P1/Config.toml'):
    #         shutil.copy(source1, i + '/P1/')

    # if not os.path.exists(i+'P2/Config.toml'):
    #         shutil.copy(source1, i + '/P2/')
    
    for j in pcnfolders:
        #if 'P0' in j:
            #if not os.path.exists(j+'/Config.toml'):
        shutil.copy(source1, j + '/')

        print('source = ' + source1 + ' to destination: ' + j+'/')

        # if 'P1' in j:
        #     #if not os.path.exists(j+'/Config.toml'):
        #     shutil.copy(p1_source, j + '/')

        #     print('source = ' + source1 + ' to destination: ' + j+'/')
        
        # if not os.path.exists(j+'/Config.toml'):
        #     shutil.copy(p0_source, j + '/')

        #print('source = ' + source1 + ' to destination: ' + j+'/')

    # if not os.path.exists(i+'/P0/opensim/'):
    #         shutil.copytree(source2, i+'/P0/opensim/')

    # print('source = ' + source2 + ' to destination: ' + i+'/P0/opensim/')

    # if not os.path.exists(i+'/P1/opensim/'):
    #         shutil.copytree(source2, i+'/P1/opensim/')

    # print('source = ' + source2 + ' to destination: ' + i+'/P1/opensim/')

    # for j in pcnfolders:
    #     os.chdir(i)

        # # copy the user and opensim folder, but only if they don't exist
        # if 'P1' in j:
        #     if not os.path.exists(j+'/Config.toml'):
        #         for toml_file in glob.glob(i+ '/P1/Config.toml'):
        #             shutil.copy(toml_file, j + '/')
        #     print('source = ' + source_p0 + ' to destination: ' + j+'/')
        # else:
        #     if not os.path.exists(j+'/Config.toml'):
        #         for toml_file in glob.glob(i+ '/P2/Config.toml'):
        #             shutil.copy(toml_file, j + '/')
        #     print('source = ' + source_p1 + ' to destination: ' + j+'/')

    print('Step: Calibration')
    # check if there there is toml file with calibration in the name
    if not os.path.exists(i+'/calibration/calibration_anipose.toml'):
    #if not os.path.exists(i+'/calibration/Calib_board.toml'):

    # loop through the calibration folders with a video
    # then save every 10thm frame to an image in that folder 
        print('calibration file not found')
        calib_folders = glob.glob(i+'/calibration/*/*')
        print(calib_folders)
        for c in calib_folders:
            # if extrinsics in calib_folder, then skip
            if 'extrinsics' in c:
                # check if there are at least 100 png files
                pngfiles = glob.glob(c+'/*.png')
                if len(pngfiles) > 100:
                    continue
                else:
                    print(c)
                    # get all avi files in the folder
                    avifiles = glob.glob(c+'/*.avi')
                    print(avifiles)
                    # split the path into its components
                    split = c.split(os.path.sep)
                    camIndex = split[-1]
                    input_video = avifiles[0]
                    print(input_video)
                    cap = cv2.VideoCapture(input_video)
                
                    # check if the video file was opened successfully
                    if not cap.isOpened():
                        print("Error: Couldn't open the video file.")
                        exit()
                    output_dir = c+'/'
                
                    # frame counter
                    frame_count = 0
                    print('We are now saving frames extracted from calibration videos')
                    while True:
                    # read the next frame
                        ret, frame = cap.read()
                        # Convert BGR to RGB
                        #if ret:
                        #   frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        if not ret:
                            break  # break the loop if we reach the end of the video
                            
                        frame_count += 1
            
                        # save every 10th frame
                        if frame_count % framepick == 0:
                            frame_filename = f"{output_dir}frame_{frame_count}.png"
                            cv2.imwrite(frame_filename, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                            # 0 compression for best quality
                            #print(f"Saved frame {frame_count}")
            
                    # release the video capture object and close the video file
                    cap.release()
                    cv2.destroyAllWindows()
            else:
                # check if there are at least 100 png files
                pngfiles = glob.glob(c+'/*.png')
                if len(pngfiles) > 100:
                    continue
                else:
                    print(c)
                    # get all avi files in the folder
                    avifiles = glob.glob(c+'/*.avi')
                    print(avifiles)
                    # split the path into its components
                    split = c.split(os.path.sep)
                    camIndex = split[-1]
                    input_video = avifiles[0]
                    print(input_video)
                    cap = cv2.VideoCapture(input_video)
                
                    # check if the video file was opened successfully
                    if not cap.isOpened():
                        print("Error: Couldn't open the video file.")
                        exit()
                    output_dir = c+'/'
                
                    # frame counter
                    frame_count = 0
                    print('We are now saving frames extracted from calibration videos')
                    while True:
                    # read the next frame
                        ret, frame = cap.read()
                        # Convert BGR to RGB
                        #if ret:
                        #   frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        if not ret:
                            break  # break the loop if we reach the end of the video
                            
                        frame_count += 1
            
                        # save every 10th frame
                        if frame_count % framepick == 0:
                            frame_filename = f"{output_dir}frame_{frame_count}.png"
                            cv2.imwrite(frame_filename, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                            # 0 compression for best quality
                            #print(f"Saved frame {frame_count}")
            
                    # release the video capture object and close the video file
                    cap.release()
                    cv2.destroyAllWindows()
    
        print('calibration file does not exist, calibrating...')
        Pose2Sim.calibration() # calibrate with checkerboard

        # get the last element of the i
        # split = i.split(os.path.sep)
        # last = split[-1]
        # # and get the last element of the last split
        # file_parts = last.split('_')
        # session_id = file_parts[1]
        # session_part = file_parts[-1]
        # # if session_part is 1, we copy trc and calib file to the session that has some id, but part 2
        # if session_part == '1':
        #     # copy the calibration file to the session with the same id, but part 2
        #     # get the session id
        #     session_id = file_parts[1]
        #     # get the session part
        #     copy_to_part = '2'
        #     # get the new folder name
        #     new_folder = 'Session_'+session_id+'_'+copy_to_part
        #     # get the new folder path
        #     new_folder_path = inputfolders + new_folder
        #     # get the calibration file path
        #     calib_file = i + '/calibration/Calib_board.toml'
        #     # copy the calibration file to the new folder
        #     shutil.copy(calib_file, new_folder_path + '/calibration/')
        #     # get the trc file path
        #     trc_file = i + '/calibration/Object_points.trc'
        #     # copy the trc file to the new folder
        #     shutil.copy(trc_file, new_folder_path + '/calibration/')
        # # otherwise continue to next code
        # else:
        #     continue

        
    # if calibration file exists, then we can skip calibration
    else:
        print('calibration file found')   


    # our cameras are natively synchronized so we do not need this step
    #print('Step: synchronization')
    #Pose2Sim.synchronization()

    # Person association if there is more people in a video
    #Pose2Sim.personAssociation()

    # print('Step: triangulation')
    Pose2Sim.triangulation()

    print('Step: filtering')
    Pose2Sim.filtering()

   ### TODO : fix issue with MarkerAugmenter - some weird error
    #note that augmentation works only for model 25 and 25b
    ##try augmentation, if value error, skip the file
    # try :
    #     print('Step: marker augmentation')
    #     Pose2Sim.markerAugmentation()
    # except ValueError:
    #     print('Value error, skipping the file')
    #     continue

trctoconvert = []
for j in pcnfolders:
   # check in the pose-3d folder\
    if not os.path.exists(j+'/pose-3d/'):
        os.makedirs(j+'/pose-3d/')
    posefolder = '/pose-3d/'
    # check any .trc files in the folder
    trcfiles = glob.glob(j+posefolder + '*.trc')

    print(trcfiles)
    # get out from trcfiles all files with LTSM - mistake in formatting
    #trcfiles = [x for x in trcfiles if 'LSTM' not in x]

    # append
    trctoconvert = trctoconvert + trcfiles

   # loop through files and convert to csv
for file in trctoconvert:
    print(file)
    if 'LSTM' not in file:
        # now convert trc data to csv
        mocap_data = TRCData()
        mocap_data.load(os.path.abspath(file))
        num_frames = mocap_data['NumFrames']
        markernames = mocap_data['Markers'] # the marker names are not

        # convert movap_data to pandas dataframe
        mocap_data_df = pd.DataFrame(mocap_data, columns=mocap_data['Markers'])
        # each value within the dataframe consists a list of x,y,z coordinates, we want to seperate these out so that each marker and dimension has its own column
         # first we create a list of column names
        colnames = []
        for marker in markernames:
            colnames.append(marker + '_x')
            colnames.append(marker + '_y')
            colnames.append(marker + '_z')

        # Create a new DataFrame to store separated values
        new_df = pd.DataFrame()

        # Iterate through each column in the original DataFrame
        for column in mocap_data_df.columns:
            # Extract the x, y, z values from each cell
            xyz = mocap_data_df[column].tolist()
            # Create a new DataFrame with the values in the cell separated into their own columns
            xyz_df = pd.DataFrame(xyz, columns=[column + '_x', column + '_y', column + '_z'])
            # Add the new columns to the new DataFrame
            new_df = pd.concat([new_df, xyz_df], axis=1)

        # add a new time column to the new dataframe assuming the framerate was 60fps
        time = []
        ts = 0
        for i in range(0, int(num_frames)):
            ts = ts + 1/framerate
            time.append(ts)
        # add the time column to the new dataframe
        new_df['Time'] = time
        #write pd dataframe to csv
        new_df.to_csv(file+'.csv', index=False)

    else:
        continue
            # df = pd.read_csv(file, sep='\t', skiprows=3)
            # print(df)
            # # edit all cols except the first two
            # colstoedit = df.columns[2:]
            # print(colstoedit)
            # # Combine the first and second rows to form a single header
            # new_columns = [f"{str(df.iloc[0, i])}_{str(df.iloc[1, i])}" for i in range(len(df.columns))]
            # # add Frame, Time to beginning
            # #new_columns = ['Frame', 'Time'] + new_columns
            # # Assign the new header to the DataFrame
            # df.columns = new_columns
            # # drop the first two rows
            # df = df.drop([0, 1])
            # # Reset the index
            # df.reset_index(drop=True, inplace=True)
            # print(df)
            # break

