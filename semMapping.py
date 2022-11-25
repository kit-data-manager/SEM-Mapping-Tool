import json
import os
import copy
from metadataSchemaReader import MetadataSchemaReader
from attributeMapping import AttributeMapping
import datetime as dt
from dateutil import parser
import zeiss_tiff_meta.zeisstiffmeta as zm

def cleanData(mappedDict):
    # Convert endTime var into ISO 8601
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
      
    return {key: value for key, value in sorted(mappedDict.items())}

def modVal(dic, keys, val):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = val
    return None

def mapSEM(sourceImg, schema, mapSEM, resultsPath):
    src = sourceImg
    md = zm.zeiss_meta(src)
    del md[0]
    resultDictionary = {**dict((x1+"_value",x2) for x0, x1, x2, x3 in md) , **dict((x1+"_unit",x3) for x0, x1, x2, x3 in md)}
    resultDictionary_filtered = {k: v for k, v in resultDictionary.items() if v != ''}
    metadataDict = dict(sorted(resultDictionary_filtered.items()))
    
    # Open and load schema
    with open(schema, 'r') as f:
        jsonSchema = json.load(f)
    
    readSchema = MetadataSchemaReader(jsonSchema)
    schema = readSchema.searchedSchema
    
    # Open and load map
    with open(mapSEM, 'r') as m:
        newmapSEM = json.load(m)
        
    # Map the metadata dictionary
    Map = AttributeMapping(metadataDict, newmapSEM, 'mappedTerms')
    workingDict = Map.__dict__
    
    # Clean up the metadata
    cleanDict = cleanData(workingDict)
        
    # Modify schema file
    outputFile = dict()
    for i, key in enumerate(cleanDict):
        modVal(outputFile, key.split('.'), cleanDict[key])
        
    # Output file to .json
    outputFilename = os.path.join(resultsPath, src[:-4] + '.json')
    with open(outputFilename, 'w') as f:
        json.dump(outputFile, f)
        
    return outputFile