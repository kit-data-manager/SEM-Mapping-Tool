import semMapping

mySchema = "SEM_schema.json"
myMap    = 'new_mapSEM.json'
imgDir = '/Users/elias/matwerk/sem-mapping/SEM_TIFF_images/'
resultsPath = '/Users/elias/matwerk/sem-mapping/results'

semMapping.mapSEM('FeMoOx_AntiA_04_1k5x_CN.tif', mySchema, myMap, resultsPath)