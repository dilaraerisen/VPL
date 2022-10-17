#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:08:15 2021

@author: dilara
"""
"""Convert single session data of a single subject to BIDS format

Dependencies:
    - dcm2niix (Freestanding version or MRIcroGL version are both fine)
    - FSL
    - pydeface
Before starting:
    - Create a folder called NSC697 on your computer
    - Create a folder called Temp inside NSC697
    - Put raw data (.zip) of a single session inside Temp
    - Put experimental protocol (.zip) of a single session inside Temp
    - Note that anything in Temp will be eventually deleted
After finished:
    - Run the BIDS validator
    - Hope for the best
This script is written as an assignment NSC672 course in Fall 2021.
I am not a native speaker in Python. If you notice anyhing stupid or
simply have an suggestion to improve the code, 
contact me at dilara.erisen@gmail.com.
"""
## CAUTION ##
# There is something wrong with IntendedFor fields
import os
import sys
import json
import csv
import glob
import zipfile
import shutil
import subprocess
import numpy as np

# Ask for Subject ID and Session
subID = input('Subject ID:')
sesNum = input('Session:')
# Ask for Participant info
sex = input('Sex (F/M):')
yob = input('Year of Birth:')
hand = input('Handedness (R/L/A):')
group = input('Group (Ctrl/Exp):')
partinfo = [('sub-%s' %(subID)), sex, yob, hand, group]
partkeys = {
        "ParticipantID":{
                "Description": "A unique ID for the participant"
                },
        "Sex": {
                "Description": "sex of the participant as reported by the participant",
                "Levels": {"M": "male","F": "female"},
                },
        "YOB":{
                "Description":"Year of Birth"
                },
        "Handedness":{
                "Description":"Handedness of the participant", 
                "Levels":{"R":"right handed", "L":"left handed", "A": "ambidextrous"}
                },            
        "Group":{
                "Description":"Control or experimental group",
                "Levels":{"Ctrl":"Control group","Exp":"Experimental group"}
                }
        }
print('\n Converting data for sub-%s-ses-%s to BIDS format... \n' %(subID, sesNum))
        
### Define the tree data structure ###
toplvl = '/home/dilara/NSC672'  
stuName = 'BlockGLM'
expName = 'VisionMotor'
partdir= ('%s/Participants' %toplvl)
studir= ('%s/study-%s' %(toplvl, stuName))
expdir= ('%s/experiment-%s' %(studir, expName))
dcmdir= ('%s/Dicom' %expdir)
niidir=('%s/Nifti' %expdir)
derivdir=('%s/Derivatives' %expdir)
stimdir=('%s/Stimuli' %expdir)
tempdir = ('%s/Temp' %toplvl)
datadesc = {
        "Name":"Vision and Motor Block Design Experiment", 
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": ["Dilara Erisen", "Huseyin Boyaci"],
        "EthicsApproval": "Bilkent Ethics Committee, Number: 2020_06_01_03"
        }
readme= ('%s/README' %(toplvl))
with open(readme, 'w') as f:
    f.write('This folder contains all the material used in NSC672 course in Fall 2021.' 
            'The material includes participant information, raw DICOM data, analyzed data,'
            'as well as stimulus and analysis code.')
    
#### Build the tree #####
if os.path.isdir(partdir):
    print('Participants folder already exists')
else:
    os.mkdir(partdir)
    print('Participants folder is created')
    
if os.path.isdir(studir):
    print('Study folder already exists')
else:
    os.mkdir(studir)
    print('Study folder is created')
if os.path.isdir(expdir):
    print('Experiment folder already exists')
else:
    os.mkdir(expdir)
    print('Experiment folder is created')
if os.path.isdir(dcmdir):
    print('Dicom folder already exists')
else:
    os.mkdir(dcmdir)
    print('Dicom folder is created')
if os.path.isdir(niidir):
    print('Nifti folder already exists')
else:
    os.mkdir(niidir)
    print('Nifti folder is created')
datajson= ('%s/dataset_description.json' %(niidir))
if os.path.isfile(datajson):
    print('Dataset description file already exists')
else:
    with open (datajson, "w") as f:
        json.dump(datadesc, f, indent=4)
    print('Dataset description file is created')
shutil.copy(readme, niidir)
partlist = ('%s/participants.tsv' %(niidir))
if os.path.isfile(partlist):
    print('Participant list already exists')
    with open(partlist, 'a') as f:
        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(partinfo)
    print('Participant is added to the list')
else: 
    with open(partlist, 'w') as f:
        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(['participant_id', 'sex', 'yob', 'handedness', 'group'])
        tsv_writer.writerow(partinfo)
    print('Participant list is created')
    print('Participant is added to the list')
partjson = ('%s/participants.json' %(niidir))
if not os.path.isfile(partjson):
    with open (partjson, "w") as f:
        json.dump(partkeys, f, indent=4)
if os.path.isdir(derivdir):
    print('Derivatives folder already exists')
else:
    os.mkdir(derivdir)
    print('Derivatives folder is created')
if os.path.isdir(stimdir):
    print('Derivatives folder already exists')
else:
    os.mkdir(stimdir)
    print('Stimuli folder is created')
    
#### Move data from Temp ####
dcmdest = '%s/sub-%s/ses-%s' %(dcmdir, subID, sesNum)
os.makedirs(dcmdest)
rawzip = glob.glob(('%s/NSC672*.zip' %tempdir))
rawzip = ''.join(rawzip) # convert list to string
with zipfile.ZipFile(rawzip, 'r') as zipf:
    zipf.extractall(tempdir)
print('Raw data is unzipped in Temp folder')
rawdir = glob.glob('%s/**/BOYACI*' %(tempdir)) #find the folder with the runs
rawdir = ''.join(rawdir)  # convert list to string
rawFols = os.listdir(rawdir)
for rawFol in rawFols:
    shutil.move(os.path.join(rawdir, rawFol), dcmdest)
print('Raw data is moved to Dicom directory')
prozip = glob.glob(('%s/*ExperimentalProtocol.zip' %tempdir))
prozip = ''.join(prozip) # convert list to string
shutil.copy(prozip, dcmdest)
print('Experimental protocol is copied to Dicom folder')
shutil.copy(prozip, stimdir)
print('Experimental protocol is copied to Stimuli folder')

##### Convert to nii #####
niidest = '%s/sub-%s/ses-%s' %(niidir, subID, sesNum)
os.makedirs(niidest)
os.mkdir('%s/anat' %niidest)
os.mkdir('%s/fmap' %niidest)
os.mkdir('%s/func' %niidest)
# Find paths to dicoms
anatFol = glob.glob('%s/T1_MPR*' %dcmdest)
anatFol = ''.join(anatFol)
wedges = sorted(glob.glob('%s/*HORVER_WEDGE*' %dcmdest)) #alphabetical order
clasps = sorted(glob.glob('%s/*HANDCLASP*' %dcmdest))
fmaps = sorted(glob.glob('%s/TOPUP*' %dcmdest))

# User input is needed for this next part
if not fmaps:
    print('\nNo fmap runs found in this session')
    flag = 1
elif fmaps:
    print(len(fmaps), '\nfmap runs found in this session')
    print('Need a little help sorting these out...\n')
    count=0
    for fmap in fmaps:
        count = count+1
        print(count, '.', fmap.split('/')[-1])
    usrin = input('Put 0 for Wedge and 1 for Handclasp. Please separate by space: ' )
    fmapidx = usrin.split() # converts to a list
    for i in range(len(fmapidx)):
        # convert each item to int type
        fmapidx[i] = int(fmapidx[i])
    # Fieldmaps intended for Wedge runs:
    IFwedge = [j for indx,j in enumerate(fmaps) if not fmapidx[indx]]
    # Fieldmaps intended for Handclasp runs:
    IFclasp = [j for indx,j in enumerate(fmaps) if fmapidx[indx]]
    print('\nThese fmaps are intended for Wedge runs:')
    for i in IFwedge:
        print(i.split('/')[-1])
    print('\nThese fmaps are intended for Handclasp runs:')
    for i in IFclasp:
        print(i.split('/')[-1])
    flag = input('Do you want to proceed? (Yes = 1, No = 0) : ')
    flag = int(flag)

if flag:
    print('Moving on to dcm2nii conversion...')
    # BIDS names
    core = ('sub-%s_ses-%s' %(subID, sesNum))
    wedName = ('%s_task-visual' %core)
    clspName = ('%s_task-motor' %core)
    fixName = ('%s_task-fixation' %core)
    # Convert and deface anatomical image
    print('\nConverting anatomical image...')
    try:
        output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_T1w' %core, '-z',
                             'y', '-o', '%s/anat' %niidest, anatFol])
        print(output.decode(sys.stdout.encoding).strip()) #just for readability
    except subprocess.CalledProcessError as error:
        print(error)
        
    print('\nDefacing anatomical image...')
    print('This can take a couple of minutes')
    try:
        output = subprocess.check_output(['pydeface', '%s/anat/%s_T1w.nii.gz' %(niidest, core),
                             '--outfile', '%s/anat/%s_T1w.nii.gz' %(niidest, core),
                             '--force'])
        print(output.decode(sys.stdout.encoding).strip()) 
    except subprocess.CalledProcessError as error:
        print(error)   
    # Convert functional runs
    print('\nConverting visual runs...')
    wedNo = 1
    for wedge in wedges:
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_run-%s_bold' %(wedName,wedNo), 
                                 '-z', 'y', '-o', '%s/func' %niidest, wedge])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        # Add required fields to json file
        with open ('%s/func/%s_run-%s_bold.json' %(niidest, wedName,wedNo), "r+") as f:
            data = json.load(f)
            data.update({"TaskName": "Visual task"})
            f.seek(0)
            json.dump(data, f, indent=4)
        # Create events.tsv file
        wedEvts = '%s/func/%s_run-%s_events' %(niidest, wedName,wedNo)
        with open('%s.tsv' %wedEvts, 'w') as f:
            tsv_writer = csv.writer(f, delimiter='\t')
            tsv_writer.writerow(['onset', 'duration', 'trial_type', 'stimulus_file'])
            onset =list(range(0,16*17,16))
            onset = [el + 10 for el in onset]
            onset.insert(0,0)
            duration = list(np.ones(16, dtype=int)*16)
            duration.insert(0,10)
            duration.insert(-1,10)
            trial_type =  ['horizontal', 'vertical'] * 8
            trial_type.insert(0, 'rest')
            trial_type.extend(['rest'])
            stim_file = [prozip.split('/')[-1]]
            for i in range(len(onset)):
                tsv_writer.writerow([onset[i], duration[i], trial_type[i], stim_file])
            print('%s.tsv is created' %wedEvts.split('/')[-1])
        # Create events.json file
        wedkeys = {
        "Onset":{
                "Description": "Onset of the stimulus"
                },
        "Duration": {
                "Description": "Duration of the stimulus",
                },
        "TrialType":{
                "Description":"Alternating horizontal and vertical wedges",
                "Levels": {"horizontal": "Two wedges with horizontal orientation",
                           "vertical": "Two wedges with vertical orientation",
                           "rest": "No stimulus"},
                },
        "StimulusFile":{
                "Description":"Zip file the stimulus protocol is archieved"
                },            
        }
        with open ('%s.json' %wedEvts, "w") as f:
            json.dump(wedkeys, f, indent=4)
            print('%s.json is created' %wedEvts.split('/')[-1])
        
        fixEvts = '%s/func/%s_run-%s_events' %(niidest, fixName,wedNo)
        # Find the fixation events in the experimental protocol zipfile
        searchzip = []
        with zipfile.ZipFile(prozip, 'r') as zipf:
            files = zipf.namelist()
            print('Which one is the fixation events for this run?')
            count = 1
            for file in files:
                if file.endswith('.txt'):
                    searchzip.append(file)
                    print(count, '. ', file)
                    count = count +1
            indx = input('%s ?: ' %list(range(1,count)))
            indx = int(indx)-1
            fixTxt = zipf.read(searchzip[indx])
            fixTxt = fixTxt.decode(sys.stdout.encoding) #convert byte string
            fixTxt = fixTxt.replace('\n', ' ').split(' ') #now it is a list
            fixTxt.pop(-1)
            success = fixTxt[0::2]
            rt = fixTxt[1::2]
            onset = np.zeros(len(rt))
            duration = np.zeros(len(rt))
        # Create the events.tsv file
        with open('%s.tsv' %fixEvts, 'w') as f:
            tsv_writer = csv.writer(f, delimiter='\t')
            tsv_writer.writerow(['onset', 'duration', 'success', 'RT'])
            for i in range(len(rt)):
                tsv_writer.writerow([onset[i], duration[i], success[i], rt[i]])
            print('%s is created' %fixEvts.split('/')[-1])
        # Create events.json file
        fixkeys = {
        "Onset":{
                "Description": "Onset of the stimulus"
                },
        "Duration": {
                "Description": "Duration of the stimulus",
                },
        "Success":{
                "Description":"Success of trial",
                "Levels": {"1": "Correct",
                           "0": "Wrong"},
                },
        "ResponseTime":{
                "Description":"Time before key press"
                },            
        }
        with open ('%s.json' %fixEvts, "w") as f:
            json.dump(fixkeys, f, indent=4)
            print('%s.json is created' %fixEvts.split('/')[-1])
        wedNo = wedNo+1    
    
    print('\nConverting motor runs...')
    clspNo = 1
    for clasp in clasps:
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_run-%s_bold' %(clspName,clspNo), 
                                 '-z', 'y', '-o', '%s/func' %niidest, clasp])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        # Add required fields to json file
        with open ('%s/func/%s_run-%s_bold.json' %(niidest, clspName,clspNo), "r+") as f:
            data = json.load(f)
            data.update({"TaskName": "Motor task"})
            f.seek(0)
            json.dump(data, f, indent=4)
        # Create events.tsv file
        clspEvts = '%s/func/%s_run-%s_events' %(niidest, clspName,clspNo)
        with open('%s.tsv' %clspEvts, 'w') as f:
            tsv_writer = csv.writer(f, delimiter='\t')
            tsv_writer.writerow(['onset', 'duration', 'trial_type', 'stimulus_file'])
            onset =list(range(0,16*16,16))
            onset = [el + 10 for el in onset]
            onset.insert(0,0)
            duration = list(np.ones(20, dtype=int)*16)
            duration.insert(0,10)
            duration.insert(-1,10)
            trial_type =  ['left','right', 'both', 'rest'] * 5
            trial_type.insert(0, 'rest')
            trial_type.insert(-1, 'rest')
            stim_file = [prozip.split('/')[-1]]
            for i in range(len(onset)-1):
                tsv_writer.writerow([onset[i], duration[i], trial_type[i], stim_file])
            print('%s is created' %clspEvts.split('/')[-1])
        # Create events.json file
        clspkeys = {
        "Onset":{
                "Description": "Onset of the stimulus"
                },
        "Duration": {
                "Description": "Duration of the stimulus",
                },
        "TrialType":{
                "Description":"Clasp either right, left or both hands",
                "Levels": {"right": "Right handclasp",
                           "left": "Left handclasp",
                           "both": "Clasp both hands",
                           "rest": "No handclasp"},
                },
        "StimulusFile":{
                "Description":"Zip file the stimulus protocol is archieved"
                },            
        }
        with open ('%s.json' %clspEvts, "w") as f:
            json.dump(clspkeys, f, indent=4)
            print('%s.json is created' %clspEvts.split('/')[-1])
        clspNo = clspNo+1
    # Now the fieldmaps
    if os.listdir('%s/fmap' %niidest):
        print('\nConverting fieldmap runs...')
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_dir-AP_run-1_epi' %core, 
                                     '-z', 'y', '-o', '%s/fmap' %niidest, IFwedge[0]])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_dir-PA_run-1_epi' %core, 
                                     '-z', 'y', '-o', '%s/fmap' %niidest, IFwedge[1]])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_dir-AP_run-2_epi' %core, 
                                     '-z', 'y', '-o', '%s/fmap' %niidest, IFclasp[0]])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        try:
            output = subprocess.check_output(['dcm2niix', '-9','-f', '%s_dir-PA_run-2_epi' %core, 
                                     '-z', 'y', '-o', '%s/fmap' %niidest, IFclasp[1]])
            print(output.decode(sys.stdout.encoding).strip())
        except subprocess.CalledProcessError as error:
            print(error)
        # Add required fields to json files
        with open ('%s/fmap/%s_dir-AP_run-1_epi.json' %(niidest,core), "r+") as f:
            data = json.load(f)
            data.update({"IntendedFor": ['%s_run-1_bold' %wedName, '%s_run-2_bold' %wedName]})
            f.seek(0)
            json.dump(data, f, indent=4)
        with open ('%s/fmap/%s_dir-PA_run-1_epi.json' %(niidest,core), "r+") as f:
            data = json.load(f)
            data.update({"IntendedFor": ['%s_run-1_bold' %wedName, '%s_run-2_bold' %wedName]})
            f.seek(0)
            json.dump(data, f, indent=4)
        with open ('%s/fmap/%s_dir-AP_run-2_epi.json' %(niidest,core), "r+") as f:
            data = json.load(f)
            data.update({"IntendedFor": ['%s_run-1_bold' %clspName, '%s_run-2_bold' %clspName]})
            json.dump(data, f, indent=4)
        with open ('%s/fmap/%s_dir-PA_run-2_epi.json' %(niidest,core), "r+") as f:
            data = json.load(f)
            data.update({"IntendedFor": ['%s_run-1_bold' %clspName, '%s_run-2_bold' %clspName]})
            f.seek(0)
            json.dump(data, f, indent=4)
    # Delete Temp folder
    shutil.rmtree(tempdir) 
    ### DONE
    print('Time to run the BIDS validator') 
elif not flag:
    print('Ok, bye then!')
else:
    raise Exception('It was a simple yes or no question.')