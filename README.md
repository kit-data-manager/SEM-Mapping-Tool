# Metadata Extraction Tool for Scanning Electron Microscopy

This python based tool extracts metadata from machine generated scanning microscopy images in the TIFF format. Currently only metadata from SEMs manufactured by Zeiss, and acquired by their own software is supported. In future, metadata from machines developed by other manufacturers, and produced by other softwares would also be included. Ideally the tool would be integrated with an interface which enables the user to select the manufacturer and software, and upload the SEM image(s) in TIFF format. Other formats could also be included in the future. The output of the tool will be a json file with the extracted metadata which follows the SEM JSON schema available at [KIT Data Manager/ Metadata Schemas for Materials Science](https://github.com/kit-data-manager/Metadata-Schemas-for-Materials-Science) on GitHub. It is also stored in this repository under the name [SEM_schema.json](SEM_schema.json). This schema is constantly under development based on the feedback that we receive from users. It was first published at [CEUR Workshop Proceedings](https://ceur-ws.org/Vol-3036/paper21.pdf).

## How to use the tool

* Clone the repository on your local device and open the jupyter notebook titled working_example.ipynb. 

* In the last code block, replace the path assigned to > imgDir with the path of the folder containing the SEM TIFF images whose metadata is to be extracted. Similarly replace the path resultsPath with the folder where you want the JSON metadata documents to be saved.

The schema and the map containing the terms in the metadata of the TIFF image and the terms in the schema, are stored respectively under mySchema and myMap, respectively.

* Now run the working_example.ipynb jupyter notebook from the beginning. At the end, after running the last code block, the reulsts will be stored under the path given under resultspath.
 
