import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
import uuid
from enum import Enum

class ItemKind(Enum):
    Project = "Project"
    Asset = "Asset"
    Category = "Category"
    Component = "Component"
    Collection = "Installation"
    Classification = "Classification"
    Path = "Primitive"



class CollectionItem(AbstractItem):
    def __init__(self, name,kind : ItemKind = ItemKind.Collection , uid=None, parent=None):
        super().__init__()
        self.name = name
        self.kind = kind
        self.parent = parent
        self.children = []
        self.uid = uid
        if uid == None:
            self.uid = str(uuid.uuid4())

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class PathItem(AbstractItem):
    def __init__(self, name,kind : ItemKind = ItemKind.Path, uid=None, parent=None, primPath = None):
        super().__init__()
        self.name = name
        self.kind = kind
        self.parent = parent
        self.uid = uid
        self.primPath = primPath
        self.children = []
        if uid == None:
            self.uid = str(uuid.uuid4())


class ClassificationItem(AbstractItem):
    def __init__(self, name,kind : ItemKind = ItemKind.Project , uid=None, parent=None):
        super().__init__()
        self.name = name
        self.kind = kind
        self.parent = parent
        self.children = []
        self.uid = uid
        if uid == None:
            self.uid = str(uuid.uuid4())

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
       
        
# Model with multiple items
class ClassificationItemModel(AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._root_items = []

        # Example hierarchy
        parent = ClassificationItem("MyPoject")
        self._root_items.append(parent)

    def get_item_children(self, item):
        if item is None:
            return self._root_items
        return item.children

    def get_item_value_model_count(self, item):
        return 2

    def get_item_value_model(self, item, column_id):
        return ui.SimpleStringModel(item.name)
    
    def add_child_to_item(self,kind, parent_item, name):
        new_child = ClassificationItem(name,kind)
        parent_item.add_child(new_child)
        self._item_changed(parent_item)

    def add_collection_to_item(self,kind, parent_item, name, paths):
        new_child = CollectionItem(name)
        parent_item.add_child(new_child)
        self._item_changed(parent_item)
        for path in paths:
            pathsSplit = path.split("/")
            pathName = pathsSplit[len(pathsSplit)-2]
            print(pathName)
            pathItem = PathItem(pathName,primPath=path)
            print(pathItem.primPath)
            new_child.add_child(pathItem)
        self._item_changed(new_child)

    def add_selection_to_item(self,kind, parent_item, name, paths):

        for path in paths:
            pathsSplit = path.split("/")
            pathName = pathsSplit[len(pathsSplit)-2]
            print(pathName)
            pathItem = PathItem(pathName,primPath=path)
            print(pathItem.primPath)
            parent_item.add_child(pathItem)
        self._item_changed(parent_item)