<div align="center">
  <h1>MOBILE MULTIMODAL LAB</h1>
  <h3><i>An Open-Source, Low-Cost and Portable Laboratory for the study of Multimodal Human Behavior</i></h3>
  <img src="Donders_MML_LOGO.png" alt="Mobile Multimodal Lab Logo">
</div>



**MML releases:**
- [] **v0.1** Published paper
- [] **v0.2** Published code

------

<br>

## Contents

1. [Introduction](#introduction)
2. [Currently supported (tutorialed) equipment](#currently-supported-tutorialed-equipment)
3. [Repository structure](#repository-structure)
4. [How to get started](#how-to-get-started)
4. [How to cite](#how-to-cite)
5. [How to contribute](#how-to-contribute)

<br>

## Introduction

**MobileMultimodalLab (MML)** is a project initiated by researchers at Donders Center for Cognition. It aims to provide a lab setup for anyone interested in studying multimodal interactive behaviour - including acoustics, body movement, muscle activity, eye movements, and so on.

To achieve this, we are working on a comprehensive coding library, accompanied by a practical manual, that shall help researchers to build their own MobileMultimodalLab. Our guiding principles are:
- **Open-source resources** - All code and documentation is freely available to everyone
- **Low-cost equipment** - We want to build the setup with as little monetary cost as possible (i.e., less than 10K)
- **Portable setup** - The setup should be easily transportable across locations

The MML setup originally consists of
- **multiple frame-synced 2D cameras** that allow for 3D motion tracking
- **multiple microphones** for acoustic analysis
- **multiple physiological sensors** for measuring heart rate, muscle activity, and respiration


To ensure that all the signals are synchronized, we use the **Lab streaming layer** (https://github.com/sccn/labstreaminglayer), a software that synchronizes different data streams with sub-millisecond precision, crucially simplifying the data collection process and subsequent processing.

Additionally, the setup is build in a **modular** way, so that anyone can add or remove equipment and recording from the default setup as long as these devices are LSL compatible

---
<br>

<div align="center">
  <img src="Setup_scheme.png" alt="Setup scheme" width="1200">
  <h3><i>Figure 1: Schematic representation of the default MML setup</i></h3>
  <p style="line-height: 1.6; font-weight: normal;">
    The figure shows the original setup of the MML employed in our proof-of-concept experiment. Two interactants are facing each other. 
    Synchronous multimodal recordings are made using the Lab Streaming Layer (LSL, green). <br>
    Audio (red): each interactant is wearing a cheek microphone, which feeds to an amplifier and 
    Linux device before streaming to the LSL. <br>
    Video (blue): each interactant is recorded by three 
    arch-mounted cameras, feeding their frame-synced videos to a Windows PC, which then 
    streams the three videos to the LSL. <br>
    Physiology (purple): each interactant is wearing 
    electrocardiogram (ECG), electromyography (EMG) and respiration (RSP) sensors, which 
    send their data wirelessly (Bluetooth) to the PCs, finally streaming to the LSL.
  </p>
</div>

<br>


## Currently scripted (tutorialed) equipment & software

- Two microphones for audio recording (with amplifier)
- Three cameras per participant (6 in total) for motion tracking
- Two Biosignal PLUX devices (ECG, EMG and respiration)
- Two Neon Eye-tracking devices
- Lab streaming layer for synchronization

<br>

## Repository structure

<pre><b>Github repository</b><br>                
├── 1_LAB_SETUP                 # Scripts used in the experiment setup, to receive and send each multimodal timeseries using LSL 
│   ├── AUDIO       # Python code to stream the Audio signal from  Linux-based device to the LSL
|   ├── VIDEO       # Python code that allows real-time capture and streaming of video data from three different cameras, along with LSL integration for synchronization and data streaming.
|   ├── PHYSIOLOGY  # Documentation about OpenSignal PLUX and LSL integration    

├── 2_PREPROCESSING             # Scripts used in the preprocessing of XDF file, to visualize, extract and clip different data streams   
│   ├── 0_XDF_Viewer        # Python code to visualize xdf data 
│   ├── 1_XDF_PROCESSING    # Python code to extract streams from XDF file 
│   ├── 2_AudioVideo_Sync   # Python scripts to work with audios and videos, including video segmentation, video splitting and audiovideo synchronization 
│
├── 3_MOTION_TRACKING          # Scritps used for motion tracking of mutliple videos using Freemocap 
│   ├── 1_Video_Segmentation # Python code to segment videos according to LSL times 
│   ├── 2_Video_Calibration  # Puthon code to calibrate Checker or Charuco board videos using ANIPOSE 
│   ├── 3_freemocap          # data repository for freemocap motion tracking outputs 
│  
├── 3a_MT_OpenPose_Pose2Sim    # Scripts used for motion tracking alterantive using OpenPose and Pose2Sim
│
├──4_DATA_ANALYSIS             # Scripts used for multiperson, multimodal synchrony estimation 
│
├──5_ANIMATIONS                # Scripts used to create multimodal animations of 2D and 3D motion tracking videos alongside audio and physiological signals

</pre>

## How to get started

For the moment, see the ENVISIONBOX information on how to get started with creating the environments and installing the necessary packages https://envisionbox.org/gettingstarted.html
<br>

## How to cite

Ahmar, D., Šárka, K., Pouw, W. (2024). MOBILE MULTIMODAL LAB: An Open-Source, Low-Cost and Portable Laboratory for the study of Multimodal Human Behavior. _In Prep_

<br>

## How to contribute
For the moment, you can get in touch by sending an email to one of the authors: 
Davide Ahmar: davide.ahmar@ru.nl
Šárka Kadavá: sarka.kadava@donders.ru.nl
Wim Pouw wim.pouw@donders.ru.nl


More information will be posted. 
