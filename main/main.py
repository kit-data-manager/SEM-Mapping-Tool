import semMapping
import os

imgDir      = 'test_images/DifferentDetector/'
resultsPath =  'results/'

myMap = 'new_mapSEM.json'
for file in os.listdir(imgDir):
    if file.endswith(".tif"):
        semMapping.workFlow(os.path.join(imgDir, file), myMap, resultsPath)