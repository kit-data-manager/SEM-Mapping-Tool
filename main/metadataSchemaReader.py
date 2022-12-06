import logging

class MetadataSchemaReader():

    def __init__(self, jsonSchema):
        try:
            self.definitions = jsonSchema["$defs"]
        except:
            pass
        self.searchedSchema = self.jsonObjectsearch(jsonSchema)

    def jsonDefinitionSearch(self, definition):
        properties = None
        if "$ref" in definition:
            if definition["$ref"].startswith("#"):
                keyword = definition[1]["$ref"].split("/")[-1:][0]
                subProperties = self.jsonDefinitionSearch(self.definitions[keyword])
                #properties[definition] = [subProperties]
                properties[definition] = subProperties
            else:
                path = definition["$ref"].split("#")[0]
                print(path)
        elif definition["type"] == "array":
            subProperties = self.jsonArraySearch(definition)
            properties = subProperties
        elif definition["type"] == "object":
            subProperties = self.jsonObjectsearch(definition)
            properties = subProperties
        else:
            properties = self.jsonTypeSearch(definition["type"])
        return properties

    def jsonArraySearch(self, property):
        subProperties = None
        if "$ref" in property["items"]:
            if property["items"]["$ref"].startswith("#"):
                keyword = property["items"]["$ref"].split("/")[-1:][0]
                subProperties = self.jsonDefinitionSearch(self.definitions[keyword])
            else:
                path = property["items"]["$ref"].split("#")[0]
                print(path)
        elif "oneOf" in property["items"]:
            for i in property["items"]["oneOf"]:
                if "$ref" in i:
                    if i["$ref"].startswith("#"):
                        keyword = i["$ref"].split("/")[-1:][0]
                        subProperties = self.jsonDefinitionSearch(self.definitions[keyword])
                    else:
                        path = i["$ref"].split("#")[0]
        elif property["items"]["type"] == "array":
            subProperties = [self.jsonArraySearch(property["items"])]
        elif property["items"]["type"] == "object":
            subProperties = self.jsonObjectsearch(property["items"])
        else:
            subProperties = self.jsonTypeSearch(property["items"]["type"])
        return subProperties

    def jsonObjectsearch(self, property):
        properties = {}
        for i in property["properties"].items():
            if "$ref" in i[1]:
                if i[1]["$ref"].startswith("#"):
                    keyword = i[1]["$ref"].split("/")[-1:][0]
                    subProperties = self.jsonDefinitionSearch(
                        self.definitions[keyword])
                    #properties[i[0]] = [subProperties]
                    properties[i[0]] = subProperties
                else:
                    path = i[1]["$ref"].split("#")[0]
                    print(path)
            elif i[1]["type"] == "array":
                subProperties = self.jsonArraySearch(i[1])
                #properties[i[0]] = [subProperties]
                properties[i[0]] = subProperties
            elif i[1]["type"] == "object":
                subProperties = self.jsonObjectsearch(i[1])
                properties[i[0]] = subProperties
            else:
                if i[0] == "value":
                    properties[i[0]] = self.jsonTypeSearch(i[1]["type"])
                #elif i[0] == "unit":
                    #properties[i[0]] = i[1]["default"]
                else:
                    properties[i[0]] = self.jsonTypeSearch(i[1]["type"])
        return properties

    def jsonTypeSearch(self, type):
        if type == "integer":
            return "int"
        elif type == "string":
            return "str"
        elif type == "number":
            return "float"
        elif type == "boolean":
            return "bool"
        elif type == "null":
            return None
        elif isinstance(type, list):
            multipleTypes = []
            for j in type:
                multipleTypes.append(self.jsonTypeSearch(j))
            return tuple(multipleTypes)
        else:
            logging.warning("Type Error")


#readSchema=MetadataSchemaReader("/Users/nicoblum/bwSyncShare/VSCode/NEP Mapping Tool/mriSchmemaV2.json", draftDir="/Users/nicoblum/bwSyncShare/NEP/jsonDrafts/*.json")
# schema=readSchema.searchedSchema
# print(schema)
