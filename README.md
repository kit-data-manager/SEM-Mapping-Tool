# Metadata Extraction Tool for Scanning Electron Microscopy

This python based tool extracts metadata from machine generated scanning microscopy images in the TIFF format. Currently only metadata from SEMs manufactured by Zeiss, and acquired by their own software is supported. In future, metadata from machines developed by other manufacturers, and produced by other softwares would also be included. Ideally the tool would be integrated with an interface which enables the user to select the manufacturer and software, and upload the SEM image(s) in TIFF format. Other formats could also be included in the future. The output of the tool will be a json file with the extracted metadata which follows the SEM JSON schema available at [KIT Data Manager/ Metadata Schemas for Materials Science](https://github.com/kit-data-manager/Metadata-Schemas-for-Materials-Science) on GitHub. It is also stored in this repository under the name [SEM_schema.json](SEM_schema.json). This schema is constantly under development based on the feedback that we receive from users. It was first published at [CEUR Workshop Proceedings](https://ceur-ws.org/Vol-3036/paper21.pdf).

## How to use the tool

### Prerequisites

* Python 3

### Instructions

* Clone this repository on your local device and open the file titled `semTool.py`. Alternatively, simply download this repository as a zip file.

* Using your favourite IDE, simply run the script `semTool.py`. Alternatively, it can also be done using a terminal or command line interface by simply navigating to the location of the script on your machine and running `python3 path/to/repository/main/semTool.py`

* A graphical interface will open up. Simply select the directory where your sample images are located, and where you would like the resulting json files to appear by using the dialog which opens up, then click execute.

* The program will run and you should get a message indicating it was successful. When you then navigate to the directory you chose as your results directory, the resulting json files will be there. These can then be uploaded to our external interface and further edited.

 
## The details

* The metadata from the images which are of TIFF format are read using [zeiss_tiff_meta module](https://github.com/ks00x/zeiss_tiff_meta).

* The metadata read from the image is then made into a flat list which has values and units of each parameter in the form parameter_value, and parameter_unit, repsectively.
 
* Next, using the class `AttributeMapping`, the parameters are mapped to the corresponding terms with their complete hierarchy as in the SEM Schema using the map stored as a json file passed through `myMap`.
 
* Thereafter, some of the mapped parameters are cleaned to reflect the Schema definition using the function `cleanData`.
 
* Then, a new nested dictionary is created with the metadata values following the path as given on the `myMap`.
 
* Finally, the new nested dictionary is converted into a JSON document using the `json` module and saved in the folder specified by `resultspath`.
 


