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


imgDir      = '/Users/elias/Documents/sem-mapping/main/test_images/DifferentDetector'
resultsPath =  '/Users/elias/Documents/sem-mapping/main/results'
myMap = '/Users/elias/Documents/sem-mapping/main/new_mapSEM.json'

for file in os.listdir(imgDir):
    if file.endswith(".tif"):
        workFlow(os.path.join(imgDir, file), myMap, resultsPath)