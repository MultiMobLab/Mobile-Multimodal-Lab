import os
import pyxdf
import glob
import pandas as pd
import numpy as np
import wave, struct, math, random
from scipy.io import wavfile
import noisereduce as nr
import json
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip #this is the video clipping function
from moviepy.video.io.VideoFileClip import VideoFileClip #alternative for snipping video
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
#identify xdf files in data folder
    #Note this data folder is external to the GITHUB page, because they are enormous files.
    #So just make sure you have a data folder called VENI_data_local
    
dataprocessfolder = './data_processed/' #D:\the_wim_files\xdf\data_raw
experiment_to_process = './data_raw/'

#identify xdf files in data folder or any subfolder
xdf_files = []
for root, dirs, files in os.walk(experiment_to_process):
    for file in files:
        if file.endswith(".xdf"):
             xdf_files.append(os.path.join(root, file))

#audio write
def to_audio(fileloc, timeseries, samplerate = 16000, channels = 1):
    if timeseriestype == 'Mic': 
        obj = wave.open(fileloc,'w')
        obj.setnchannels(channels) # mono
        obj.setsampwidth(2)
        obj.setframerate(float(samplerate))
        for i in timeseries:
            data = struct.pack('<h', int(i[0]))
            obj.writeframesraw( data )
        obj.close()

#loop through xdf files and save the all data
for xdf_file in xdf_files:
    streams, header = pyxdf.load_xdf(xdf_file)
    fnam = os.path.basename(xdf_file)[:-4]
    for stream in streams:
        timeseriestype = stream['info']['name'][0]
        timeseriestype = stream['info']['name'][0]
        samplerate = round(float(stream['info']['nominal_srate'][0]))
        #in the xdf loop over the streams and save it as csv if not yet exists
        channelcount = stream['info']['channel_count'][0]
        print('working on stream: ' + timeseriestype + '  with a channel count of ' + str(channelcount) +'\n and a sampling rate of ' + str(samplerate))
        timevec = stream['time_stamps']
        timeseries = stream['time_series']
        matrix_aux = np.vstack([np.transpose(timevec),np.transpose(timeseries)])
        matrix     = np.transpose(matrix_aux)
        df_lab = pd.DataFrame(matrix)
        df_lab.to_csv(dataprocessfolder+fnam+'_'+timeseriestype+'_nominal_srate'+str(samplerate)+'.csv',index=False)
        if timeseriestype == 'Mic':
            wavloc = dataprocessfolder+fnam+ '.wav'
            to_audio(wavloc, timeseries)
            # load data
            rate, data = wavfile.read(wavloc)
            # perform noise reduction
            reduced_noise = nr.reduce_noise(y=data, sr=rate, n_std_thresh_stationary=1.5,stationary=True)
            wavloc2 = dataprocessfolder+os.path.basename(xdf_file)[:-4] + '_denoised.wav'
            wavfile.write(wavloc2, rate, reduced_noise)
            # now based on audio collect video
            begintime = min(timevec)
            endtime = max(timevec)
            

# now break everything into synchronized chunks
for xdf_file in xdf_files:
    fnam = os.path.basename(xdf_file)[:-4]
    # video name is the folder name of xdf_file + the video name
    foldername = os.path.dirname(xdf_file)
    print('looking for a video in: ', foldername)
    # get video in the same folder
    videolong = glob.glob(foldername + '/*.avi')[0]
    # load in the wav data
    wavdata = pd.read_csv(dataprocessfolder+fnam+'_'+timeseriestype+'_nominal_srate'+str(samplerate)+'.csv')
    #load in the frame data
    framestream = pd.read_csv(dataprocessfolder+fnam+'_'+'MyWebcamFrameStream'+'_nominal_srate'+str(500)+'.csv')
    #determine begin and end time of the wave stream
    begin = min(wavdata['0'])
    end = max(wavdata['0'])
    # new video file name
    vidloc = dataprocessfolder+fnam+'_video_synced.avi'
    # get the frames that are in the trial
    startframe_tot = int(min(framestream['1'])) #what is the first frame that came in during writing?
    indices = (framestream.loc[:,'0'] >= begin) & (framestream.loc[:,'0'] <= end) #only select the framestream which includes trialtime
    sframes = framestream.loc[indices, '1'] #get a framelist that was in trialtime
    print('startframe: ' + str(min(sframes)) + '  endframe: ' + str(max(sframes)))
    startframe = int(min(sframes)) #get the first frame in trial
    endframe = (int(max(sframes))+1) #get the last frame in trial (add 1 so that the range is correct)
    totframes = endframe-startframe
    capture = cv2.VideoCapture(videolong) #load in the videocapture
    frameWidth = capture.get(cv2.CAP_PROP_FRAME_WIDTH) #check frame width
    frameHeight = capture.get(cv2.CAP_PROP_FRAME_HEIGHT) #check frame height
    frate =  capture.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'M','J','P','G') #for different video formats you could use e.g., *'XVID'
    realfps = round((totframes/(end-begin)),3)
    print('original framerate: ' + str(frate) + '  new framerate: ' + str(realfps) + '  total frames: ' + str(totframes))
    out = cv2.VideoWriter(vidloc, fourcc, fps = realfps, frameSize = (int(frameWidth), int(frameHeight)))
    frame_count = 0
    while capture.isOpened():
        #Read the next frame
        ret, frame = capture.read()
        if ret:
        # Increment the frame count
            frame_count += 1
        if frame_count in range(startframe, endframe):
            out.write(frame)
        if frame_count > endframe:
            capture.release()
            out.release() 

# now add the audio to synced video
for xdf_file in xdf_files:
    fnam = os.path.basename(xdf_file)[:-4]
    vidloc = dataprocessfolder+fnam+'_video_synced.avi'
    audloc = dataprocessfolder+os.path.basename(xdf_file)[:-4] + '_denoised.wav'
    # now add the audio under the avi
    videoclip = VideoFileClip(vidloc)
    audioclip = AudioFileClip(audloc)
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(dataprocessfolder+fnam+'_video_synced_audio.avi',codec='png', codec="libx264")
    videoclip.close()
    audioclip.close()
    new_audioclip.close()
    

