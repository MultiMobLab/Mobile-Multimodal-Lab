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
pose2simprjfolder = curfolder + '\\Empty_project_ENVISION_settings'
# here are stored dara
inputfolders = curfolder+'/projectdata/'
# in this folder are all the sessions
sessionstotrack = glob.glob(curfolder+'/projectdata/*')
# get rid of txt files
sessionstotrack = [x for x in sessionstotrack if '.txt' not in x]
sessionstotrack = [x for x in sessionstotrack if '.toml' not in x]

print(sessionstotrack)
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

for i in sessionstotrack:
    # get the data folder
    folderstotrack = glob.glob(i + '/*data*/*', recursive=True)
    # append
    pcnfolders.append(folderstotrack)

# make it just one list, not list of lists
pcnfolders = [item for sublist in pcnfolders for item in sublist]

# get out of pcnfolders all that contains Config and opensim
pcnfolders = [x for x in pcnfolders if 'Config' not in x]
pcnfolders = [x for x in pcnfolders if 'opensim' not in x]
pcnfolders = [x for x in pcnfolders if 'txt' not in x]
pcnfolders = [x for x in pcnfolders if 'toml' not in x]

print('pcnfolders:', pcnfolders)

# set framerate
framerate = 60

# How many xth frame do we extract from the calibration video? 
framepick = 3

# copy a folder in pose2simprjfolder and its contents to folders
source1 = pose2simprjfolder+'/Config.toml'
source2 = pose2simprjfolder+'/opensim/'

#print(folderstotrack)
for i in sessionstotrack:
    print('working on: ', i)

    os.chdir(i)
    trialfolder = glob.glob(i + '/*data*')
    print('trialfolder: ', trialfolder)

    # copy to session folder
    if not os.path.exists(i+'/Config.toml'):
        shutil.copy(source1, i + '/')
        print('source = ' + source1 + ' to destination: ' + i+'/')

    # copy it also to trial folder
    if not os.path.exists(trialfolder[0] + '/Config.toml'):
        shutil.copy(source1, trialfolder[0] + '/')
        print('source = ' + source1 + ' to destination: ' + trialfolder[0]+'/')

    
    if not os.path.exists(trialfolder[0]+'/opensim/'):
        shutil.copytree(source2, trialfolder[0]+'/opensim/')
        print('source = ' + source2 + ' to destination: ' + trialfolder[0]+'/opensim/')

    
    for j in pcnfolders:
        if not os.path.exists(j+'/Config.toml'):
            shutil.copy(source1, j + '/')
            print('source = ' + source1 + ' to destination: ' + j+'/')

    print('Step: Calibration')
    # check if there there is toml file with calibration in the name
    if not os.path.exists(i+'/calibration/Calib_anipose.toml'):
        print('calibration file not found')
        break
     
    # if calibration file exists, then we can skip calibration
    else:
        print('calibration file found')
        print('calibrating via anipose')
        #config = 
        Pose2Sim.calibration()    

    #break
    # our cameras are natively synchronized so we do not need this step
    #print('Step: synchronization')
    #Pose2Sim.synchronization()

    # Person association if there is more people in a video
    #Pose2Sim.personAssociation()

    # print('Step: triangulation')
    #Pose2Sim.triangulation()

    print('Step: filtering')
    #Pose2Sim.filtering()



trctoconvert = []
for j in pcnfolders:
   # check in the pose-3d folder\
    if not os.path.exists(j+'/pose-3d/'):
        os.makedirs(j+'/pose-3d/')
    posefolder = '/pose-3d/'
    # check any .trc files in the folder
    trcfiles = glob.glob(j+posefolder + '*.trc')

    #print(trcfiles)
    # get out from trcfiles all files with LTSM - mistake in formatting
    #trcfiles = [x for x in trcfiles if 'LSTM' not in x]

    # append
    trctoconvert = trctoconvert + trcfiles

   # loop through files and convert to csv
for file in trctoconvert:
    #print(file)
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

