import os
import subprocess
import glob


curfolder = os.getcwd()

#  openpose demo.exe location
openposefol = curfolder+'/openpose/'
openpose_demo_loc = openposefol + '/bin/OpenPoseDemo.exe'

# this is the model to employ
model_to_employ = 'BODY_135'

# list folders in a main folder
folderstotrack = glob.glob(curfolder +'/projectdata/*')
# ignore txt files
folderstotrack = [x for x in folderstotrack if '.txt' not in x]
print(folderstotrack)

def runcommand(command):
    # run the command using subprocess for OPENPOSE TRACKING
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with error code {e.returncode}")
    except FileNotFoundError:
        print("The OpenPoseDemo.exe executable was not found.")

# initiate empty list
pcnfolders = []

for i in folderstotrack:
    # get the data folder
    folderstotrack = glob.glob(i + '/*data*/*', recursive=True)
    # append
    pcnfolders.append(folderstotrack)

# make it just one list, not list of lists
pcnfolders = [item for sublist in pcnfolders for item in sublist]
print(pcnfolders)


pcnfolders = [x for x in pcnfolders if 'Config' not in x]
pcnfolders = [x for x in pcnfolders if 'opensim' not in x]
pcnfolders = [x for x in pcnfolders if 'txt' not in x]

for i in pcnfolders:
    os.chdir(openposefol)
    print('working on ' + i)
    # identify all avi files in folder
    direc = glob.glob(i + '/raw-2d/' +'*.avi')

    # 3 cameras
    video0 = direc[0]
    video1 = direc[1]
    video2 = direc[2]

    videolist = [video0, video1, video2]
    
    # make a new directory if it doesn't exist
    if not os.path.exists(i+'/pose/'):
        os.makedirs(i+'/pose/')
    if not os.path.exists(i+'/pose/pose_cam1_json/'):
        os.makedirs(i+'/pose/pose_cam1_json/')
    if not os.path.exists(i+'/pose/pose_cam2_json/'):
        os.makedirs(i+'/pose/pose_cam2_json/')
    if not os.path.exists(i+'pose/pose_cam3_json/'):
        os.makedirs(i+'/pose/pose_cam3_json/')

    # also make directory for openpose videos (pose-2d-trackingvideos)
    # make a new directory if it doesn't exist
    if not os.path.exists(i+'/pose-2d-trackingvideos/'):
        os.makedirs(i+'/pose-2d-trackingvideos/')

    # initialize the pose2 folder
    outputfol1 = i+'/pose/pose_cam1_json/'
    outputfol2 = i+'/pose/pose_cam2_json/'
    outputfol3 = i+'/pose/pose_cam3_json/'

    outputfollist = [outputfol1, outputfol2, outputfol3]

    for it, j in enumerate(outputfollist):
        #first track with openpose vid1
        openposelocation = ' ' + openpose_demo_loc + ' '
        model = '--model_pose' + ' ' + model_to_employ + ' '
        video = '--video ' + videolist[it] + ' '
        todo = '--write_json '
        outputfol = j + ' '
        videoadd = '--write_video '
        videopath = i+'/pose-2d-trackingvideos/' + 'video'+str(it)+'.avi' + ' '
        command = r' '+openposelocation+model+video+todo+outputfol+videoadd+videopath
        print('were going to send this to command prompt: ' + command)
        runcommand(command)
    


 