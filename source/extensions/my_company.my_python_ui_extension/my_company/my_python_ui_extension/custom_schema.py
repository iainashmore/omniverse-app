import enum
import omni.ui as ui

class CustomSchema:

    def getCustomObjectTypes(self):
        return [
            {
                "name" : "PHYSICAL",
                "singular": "Physical Component",
                "plural": "Physical Components"
            },
            {
                "name" : "LOGICAL",
                "singular": "Logical Component",
                "plural": "Logical Components"
            }
        ]
    def getCustomRelationTypes(self):
        return [
            {
                "name":"RealizedBy",
                "title":"Realized By",
                "kind":"PHYSICAL",
            }
        ]
    
    def getDropDownTitles(self):
        titles = []
        customTypes = self.getCustomObjectTypes()
        for customType in customTypes:
            titles.append(customType['plural'])
        return titles