import omni.ui as ui
from .custom_schema import CustomSchema
from enum import Enum
    
class Kind(Enum):
    Project = "Project"
    Instance = "Instance"
    Root = "Root"
    Relation = "Relation"
   
class CustomRelationship():
    def __init__(self, parentID, childID, name):
        super().__init__()
        self.name = name
        self.parentID = parentID
        self.childID = childID


class CustomItemInstance(ui.AbstractItem):
    def __init__(self, customItem,customRelationship,relationshipType):
        super().__init__()
        self.kind = Kind.Instance
        self.name = relationshipType['name']
        self.relationship = customRelationship
        self.customType = customItem.customType
        self.title = "Instance of " + customItem.title
        self.relationshipType = relationshipType
        self.objectID = customItem.title

    def __repr__(self):
        return f'"{self.customType} {self.title}"'

class CustomItem(ui.AbstractItem):
    def __init__(self, customType, title,id,):
        super().__init__()
        self.kind = Kind.Reference
        self.customType = customType
        self.title = title
        self.objectID = id

    def __repr__(self):
        return f'"{self.customType} {self.title}"' 
    
class RootItem(ui.AbstractItem):
    def __init__(self, customType, title):
        super().__init__()
        self.kind = Kind.Root
        self.customType = customType
        self.title = title

    def __repr__(self):
        return f'"{self.customType} {self.title}"'
    
    def __repr__(self):
        return f'"{self.customType} {self.title}"'

class NameValueItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text, value):
        super().__init__()
        self.title = "_" + text
        self.name_model = ui.SimpleStringModel(text)
        self.value_model = ui.SimpleStringModel(value)

    def __repr__(self):
        return f'"{self.title} {self.name_model.as_string} {self.value_model.as_string}"' 


class CustomModel(ui.AbstractItemModel):

    def __init__(self):
        super().__init__()
        self._relations = []
        self._instances = []
        self._nodes = []
        self._rootNodes = []
        self._relationsNode = []
        self.customSchema = CustomSchema()
        self.customTypes = self.customSchema.getCustomObjectTypes()
        self.customRelations = self.customSchema.getCustomRelationTypes()
        a = self.addCustomItem(self.customTypes[1],"Log001","Log001")
        b = self.addCustomItem(self.customTypes[0],"Prd002","Prd002")
        c = self.addCustomItem(self.customTypes[0],"Prd003","Prd003")

        self.addRelationship(a,b,self.customRelations[0])
        self.addRelationship(a,c,self.customRelations[0])

        for customType in self.customTypes:
            rootNode = RootItem(customType,customType["plural"])
            self._rootNodes.append(rootNode)
        
        self._nodes.append(a)
        self._nodes.append(b)
        self._nodes.append(c)

    def addCustomItem(self,customType,title,ID):
        print("adding " + title)
        a = CustomItem(customType,title,ID)
        self._item_changed(None) # emit data changed 
        return a

    def addRelationship(self,parentItem,childItem,relationshipType):
        r = CustomRelationship(parentItem.objectID,childItem.objectID,relationshipType)
        self._relations.append(r)
        inst = CustomItemInstance(childItem,r,relationshipType)
        self._instances.append(inst)
        self._item_changed(None) # emit data changed 

    def drop(self, item_target, item_source, drop_location: int = -1) -> None:
   
        print("did drop at"  + str(drop_location))
        print(item_target)

    def drop_accepted(self, item_target, item_source, drop_location: int = -1) -> bool:
   
        print("did drop at"  + str(drop_location))
        return True
    
    def get_item_children(self,item):
        """Returns all the children when the widget asks it."""

        if item is not None:
       
            if item.kind == Kind.Root:
                
                children = self.getAllItem(item.customType)
            if item.kind == Kind.Reference:
                for instance in self._instances:
                    if instance.relationship.parentID == item.objectID:
                        print("Instance found " + instance.title)
                        children.append(instance)
            return children

        return []
    
    def getAllItem(self,customType):
        items = []
        for node in self._nodes:
            if node.customType['name'] == customType['name']:
                items.append(node)
        return items
    
    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 3
    
    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel for the first column
        and second column.
        """
        if item.kind == Kind.Root:
            if column_id == 0:
                return ui.SimpleStringModel(item.title)
            else:
                return ui.SimpleStringModel("-") 
        else:
            if column_id == 0:
                if item.kind == Kind.Instance:
                    return ui.SimpleStringModel(item.relationshipType["title"])
                else:
                   return ui.SimpleStringModel(item.title) 
            if column_id == 1:
                if item.kind == Kind.Instance:
                    return ui.SimpleStringModel(item.title)  
            else:
                return ui.SimpleStringModel(str(type(item))) 