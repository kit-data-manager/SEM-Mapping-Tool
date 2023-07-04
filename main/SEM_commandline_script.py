import sys
import json
import os
import copy
from attributeMapping import AttributeMapping
import datetime as dt
from dateutil import parser
import logging
import hyperspy.api as hs
if sys.version_info >= (3, 6):
    import zipfile
else:
    import zipfile36 as zipfile

myMap = sys.argv[1]
imgDir = sys.argv[2]
resultsLoc = sys.argv[3]


# view all the metadata stored in the ZEISS TIFF file
# from https://github.com/ks00x/zeiss_tiff_meta.git
import zeiss_tiff_meta.zeisstiffmeta as zm

def cleanData(mappedDict):
    try:
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

    
    except:
        print("Problem with keys in cleanData...")
        return None

def modVal(dic, keys, val):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = val
    return None

# if complete path in Nicolas' mapping file, will this func work as well?

def workFlow(sourceImg, mapSEM, resultsPath = 'defResults.json'):
    src = sourceImg
    print(f'\nReading metadata for {os.path.basename(src)}...')
    md = zm.zeiss_meta(src)
    del md[0]
    resultDictionary = {**dict((x1+"_value",x2) for x0, x1, x2, x3 in md) , **dict((x1+"_unit",x3) for x0, x1, x2, x3 in md)}
    resultDictionary_filtered = {k: v for k, v in resultDictionary.items() if v != ''}
    metadataDict = dict(sorted(resultDictionary_filtered.items()))
    
    # Open and load map
    with open(mapSEM, 'r') as m:
        newmapSEM = json.load(m)
        
    # Map the metadata dictionary
    try:
        Map = AttributeMapping(metadataDict, newmapSEM, 'mappedTerms')
        workingDict = Map.__dict__
    except:
        print('One or more of the required parameters was not found.')
    
    # Clean up the metadata
    # cleanDict = cleanData(workingDict)
    cleanDict = workingDict
        
    # Creating the nested dictionary according to schema
    outputFile = dict()
    for i, key in enumerate(cleanDict):
        modVal(outputFile, key.split('.'), cleanDict[key])
            
    # Output file to .json
    outputFilename = os.path.basename(src[:-4]) + '.json'
    
    logging.info('Writing results file outputFilename...')
    logging.info(os.path.join(resultsPath, outputFilename))

    with open(resultsPath, 'w') as f:
        json.dump(outputFile, f)

    return outputFile

workFlow(imgDir, myMap, resultsLoc)
