import sys
import json
import os
import copy
from attributeMapping import AttributeMapping
import datetime as dt
from dateutil import parser
import zipfile
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
    
    try:
        if mappedDict['entry.instrument.FIB.angleToEBeam.unit'] == '\u00b0':
            mappedDict['entry.instrument.FIB.angleToEBeam.unit'] = 'degree'
        if mappedDict['entry.instrument.stage.stageTiltAngle.unit'] == '\u00b0':
            mappedDict['entry.instrument.stage.stageTiltAngle.unit'] = 'degree'
    except KeyError:
        print('The tiltAngle key was not found.')
    
      
    return {key: value for key, value in sorted(mappedDict.items())}

# Function to "walk" the nested dictionary and create the metadata document accordingly
def modVal(dic, keys, val):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = val
    return None

# Main function which reads the tiff and creates the json metadata document
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
    cleanDict = cleanData(workingDict)
        
    # Creating the nested dictionary according to schema
    outputFile = dict()
    for i, key in enumerate(cleanDict):
        modVal(outputFile, key.split('.'), cleanDict[key])
            
    # Output file to .json
    outputFileName = resultsPath + os.path.basename(src)[:-4] + '.json'
    print(outputFileName)
    with open(outputFileName, 'w') as f:
        json.dump(outputFile, f)

    return outputFile

# This function creates the output zip file.
def process_zip(input_zip_path, myMap, output_zip_path):
    # Create a temporary directory to store the JSON files
    tmp_dir = 'tmp'
    os.makedirs(tmp_dir, exist_ok=True)

    # Open the input zip file and loop through its TIFF files
    with zipfile.ZipFile(input_zip_path, 'r') as input_zip:
        for file_name in input_zip.namelist():
            if file_name.endswith('.tif') or file_name.endswith('.tiff'):
                # Extract the TIFF file to a temporary location
                input_file_path = input_zip.extract(file_name, tmp_dir)

                # Run the Workflow function on the TIFF file
                output_file_name = os.path.splitext(file_name)[0] + '.json'
                output_file_path = os.path.join(tmp_dir, output_file_name)
                workFlow(input_file_path, myMap, output_file_path)

    # Create the output zip file by zipping all the JSON files
    with zipfile.ZipFile(output_zip_path, 'w') as output_zip:
        for root, dirs, files in os.walk(tmp_dir):
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(root, file_name)
                    output_zip.write(file_path, arcname=file_name)

    # Delete the temporary directory and its contents
    os.system('rm -rf {}'.format(tmp_dir))


myMap  = '/Users/elias/Desktop/SEM-Mapping-Tool/main/map.json'
input_zip_path = '/Users/elias/Desktop/SEM-Mapping-Tool/main/test_images/DifferentDetector/Archive.zip'
output_zip_filename = 'output.zip'
output_zip_path = os.path.join('/Users/elias/Desktop/SEM-Mapping-Tool/main/results/', output_zip_filename)

process_zip(input_zip_path, myMap, output_zip_path)
