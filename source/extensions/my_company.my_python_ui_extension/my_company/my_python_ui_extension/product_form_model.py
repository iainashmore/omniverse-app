import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
import uuid
import json
from .common import FormKind



class ReferenceItem(AbstractItem):
    def __init__(self, name, path,typeName,uid=None, parent=None):
        super().__init__()
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
        self.uid = uid
        self.typeName = typeName
        if uid == None:
            self.uid = str(uuid.uuid4())

    def add_child_instance(self, child):
        child.parent = self
        self.children.append(child)

class InstanceItem(AbstractItem):
    def __init__(self, name, path,typeName,uid=None, parent=None):
        super().__init__()
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
        self.uid = uid
        self.typeName = typeName
        if uid == None:
            self.uid = str(uuid.uuid4())

    def add_child_instance(self, child):
        child.parent = self
        self.children.append(child)


# Model with multiple items
class ProductFormItemModel(AbstractItemModel):

    def __init__(self,_on_drag_drop_fn):
        super().__init__()
        self._root_items = []
        self._on_drag_drop_fn = _on_drag_drop_fn

    def get_item_children(self, item):
        if item is None:
            return self._root_items
        return item.children

    def _load(self,results,typeName):
        self._root_items = []

        for entry in results:
            print("Tagged Prim:", entry["prim"].GetPath())
            referenceItem = ReferenceItem(entry["prim"].GetName(),entry["prim"].GetPath().pathString,typeName)
            for inst in entry["instances"]:
                print("  → Instance:", inst.GetPath())
                data = inst.GetCustomData()
                instTypename = data.get("class")
                instanceItem = InstanceItem(inst.GetName(),inst.GetPath().pathString,instTypename)
                referenceItem.add_child_instance(instanceItem)
            self._root_items.append(referenceItem)
        self._item_changed(None)

    def add_instance(self,referenceItem,prim):
        data = prim.GetCustomData()
        instTypename = data.get("class")
        instanceItem = InstanceItem(prim.GetName(),prim.GetPath().pathString,instTypename)
        referenceItem.add_child_instance(instanceItem)
        self._item_changed(referenceItem)

    def load(self, results, typeName):
        self._root_items = []

        def build_items(entry):
            prim = entry["prim"]
            data = prim.GetCustomData()
            class_type = data.get("class", "Geometry")

            print("Prim:", prim.GetPath(),class_type)

            item = InstanceItem(prim.GetName(), prim.GetPath().pathString, class_type)

            for child_entry in entry["instances"]:
                child_item = build_items(child_entry)
                item.add_child_instance(child_item)

            return item

        for entry in results:
            root_prim = entry["prim"]
            print("Tagged Root Prim:", root_prim.GetPath())

            reference_item = ReferenceItem(root_prim.GetName(), root_prim.GetPath().pathString, typeName)

            for child_entry in entry["instances"]:
                child_instance = build_items(child_entry)
                reference_item.add_child_instance(child_instance)

            self._root_items.append(reference_item)

        self._item_changed(None)


    def get_item_value_model_count(self, item):
        return 2

    def get_item_value_model(self, item, column_id):
        if column_id == 0:
            return ui.SimpleStringModel(item.name)
        else:
            return ui.SimpleStringModel(item.typeName)


    def get_class_tag_for_instance(stage, instance_prim):
        if not instance_prim.IsValid() or not instance_prim.IsInstance():
            return None

        # Get the referenced (source) prim
        source_prim = instance_prim.GetPrototype()

        if source_prim and source_prim.HasCustomData():
            data = source_prim.GetCustomData()
            return data.get("class")

        return None

    def refresh(self,item):
        self._item_changed(item)

    def get_drag_mime_data(self, item):

        return json.dumps({
                    "name": item.name,
                    "path": item.path,
                    "typename": item.typeName,
                    "uid": item.uid})



    # Called to test if the drop is acceptable
    def drop_accepted(self, target_item, source):
        if isinstance(source,str):
            data = json.loads(source)
            sourceTypeName = data["typename"]
            if "Instance" in sourceTypeName:
                return False
        if not isinstance(target_item, ReferenceItem):

            return False
        print(source)
        print(target_item)
        return True


    # Called when dropping
    def drop(self, target_item, source):
        self._on_drag_drop_fn(source,target_item)
