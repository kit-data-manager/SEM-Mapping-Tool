import tkinter as tk
from tkinter import filedialog

main_win = tk.Tk()
Title= tk.Label(main_win,text = "SEM Metadata Extractor")
Title.config(font =("Courier", 24))
Title.pack()

main_win.geometry("600x500")
main_win.sourceFolder = ''
main_win.sourceFile = ''
main_win.sourceImageFolder = ''
main_win.sourceResultsFolder = ''
main_win.mapFilePath = ''

LabelImageDir = tk.Label(main_win,text = "No Image directory chosen yet")
LabelImageDir.place(x = 60, y = 300)
LabelResultDir = tk.Label(main_win,text = "No Result directory chosen yet")
LabelResultDir.place(x = 60, y = 340)

def chooseImgDir():
    main_win.sourceImageFolder =  filedialog.askdirectory(parent = main_win, initialdir = "/", title = 'Please select a directory')
    LabelImageDir.config(text="Chosen Image directory:  " + main_win.sourceImageFolder)

def chooseResDir():
    main_win.sourceResultsFolder =  filedialog.askdirectory(parent = main_win, initialdir = "/", title = 'Please select a directory')
    LabelResultDir.config(text="Chosen Result directory:  " + main_win.sourceResultsFolder)

b_chooseDir = tk.Button(main_win, text = "Choose Image Folder", width = 20, height = 3, command = chooseImgDir)
b_chooseDir.place(x = 50, y = 80)
b_chooseDir.width = 100

b_chooseFile = tk.Button(main_win, text = "Choose Result Folder", width = 20, height = 3, command = chooseResDir)
b_chooseFile.place(x = 300, y = 80)
b_chooseFile.width = 100

quit = tk.Button(main_win, text = "Exit", width = 20, height = 3, command=main_win.destroy)
quit.place(x = 350, y = 400)
quit.width = 100

import json
import os
import copy
from attributeMapping import AttributeMapping
import datetime as dt
from dateutil import parser

# view all the metadata stored in the ZEISS TIFF file
# from https://github.com/ks00x/zeiss_tiff_meta.git
import zeiss_tiff_meta.zeisstiffmeta as zm

def cleanData(mappedDict):
    # Make endTime var as ISO 8601
    endTime = mappedDict['entry.endTime.Date'] + ' ' + mappedDict['entry.endTime.Time']
    mappedDict['entry.endTime'] = parser.parse(endTime).isoformat()
    
    # Remove separate date and time vars
    mappedDict.pop('entry.endTime.Date')
    mappedDict.pop('entry.endTime.Time')
    
    # Split pixel sizes into x and y
    imgSize = [float(s.strip()) for s in mappedDict['entry.instrument.imaging.numberOfPixels.xPixels'].split('*')]
    mappedDict['entry.instrument.imaging.numberOfPixels.xPixels'] = imgSize[0]
    mappedDict['entry.instrument.imaging.numberOfPixels.yPixels'] = imgSize[1]
    
    # Format tilt correction
    
    tiltCorr = mappedDict['entry.instrument.imaging.tiltCorrection']
    if tiltCorr: 
        mappedDict['entry.instrument.imaging.tiltCorrection'] = ''
    else:
        mappedDict['entry.instrument.imaging.tiltCorrection'] = 'None'
        
    # Deg symbol to "degree"
    if mappedDict['entry.instrument.FIB.angleToEBeam.unit'] == '\u00b0':
        mappedDict['entry.instrument.FIB.angleToEBeam.unit'] = 'degree'
    if mappedDict['entry.instrument.stage.tiltAngle.unit'] == '\u00b0':
        mappedDict['entry.instrument.stage.tiltAngle.unit'] = 'degree'
    
      
    return {key: value for key, value in sorted(mappedDict.items())}

def modVal(dic, keys, val):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = val
    return None

# if complete path in Nicolas' mapping file, will this func work as well?

def workFlow(sourceImg, mapSEM, resultsPath):
    src = sourceImg
    md = zm.zeiss_meta(src)
    del md[0]
    resultDictionary = {**dict((x1+"_value",x2) for x0, x1, x2, x3 in md) , **dict((x1+"_unit",x3) for x0, x1, x2, x3 in md)}
    resultDictionary_filtered = {k: v for k, v in resultDictionary.items() if v != ''}
    metadataDict = dict(sorted(resultDictionary_filtered.items()))
    
    # Open and load map
    with open(mapSEM, 'r') as m:
        newmapSEM = json.load(m)
        
    # Map the metadata dictionary
    Map = AttributeMapping(metadataDict, newmapSEM, 'mappedTerms')
    workingDict = Map.__dict__
    # print(workingDict)
    
    # Clean up the metadata
    cleanDict = cleanData(workingDict)
        
    # Creating the nested dictionary according to schema
    outputFile = dict()
    for i, key in enumerate(cleanDict):
        modVal(outputFile, key.split('.'), cleanDict[key])
        
    # Output file to .json
    outputFilename = os.path.join(resultsPath, os.path.basename(src[:-4] + '.json'))
    print(f'Writing results file {os.path.basename(outputFilename)} ...')
    with open(outputFilename, 'w') as f:
        json.dump(outputFile, f)
        
    return outputFile

# imgDir      = '/Users/elias/Documents/sem-mapping/main/test_images/DifferentDetector'
# resultsPath =  '/Users/elias/Documents/sem-mapping/main/results'

def execute():
    imgDir      = main_win.sourceImageFolder
    resultsPath =  main_win.sourceResultsFolder
    myMap = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'map.json')

    for file in os.listdir(imgDir):
        if file.endswith(".tif"):
            workFlow(os.path.join(imgDir, file), myMap, resultsPath)

    tk.messagebox.showinfo('Info', f'Success! The processed files are now in {resultsPath}.')


exec = tk.Button(main_win, text = "Execute", width = 20, height = 3, command = execute)
exec.place(x = 170, y = 200)
exec.width = 100
main_win.mainloop()