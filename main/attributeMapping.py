import json


class AttributeMapping():

    def __init__(self, metadataAttributes, mapJson, mapObject):
       for i, j in mapJson[mapObject].items():
        temp = {j: metadataAttributes[i]}
        #print(temp)
        self.__dict__.update(temp)

    def updateMap(self, **args):
       self.__dict__.update(args)
