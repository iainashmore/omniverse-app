
from .custom_schema import CustomSchema

class CustomData():
        
        nodes = []
        sources = ["Local"]
        def __init__(self):
            self.nodes = ["aa","bb","cc"]
           

        def getNodes(self):
            print("getting nodes...")
            print(self.nodes)
            return self.nodes
        
        def addNode(self,typeName):
            self.nodes.append(typeName)

        def __repr__(self):
            return f'CustomData Sources: "{self.sources}"' 
