import omni.ui as ui
from omni.ui import AbstractItemModel, AbstractItem
import uuid
import json
import omni
from pxr import UsdGeom

class VisibilityItem(AbstractItem):
    def __init__(self, name, path,typeName,uid=None):
        super().__init__()
        self.name = name
        self.path = path
        self.uid = uid
        self.typeName = typeName
        if uid == None:
            self.uid = str(uuid.uuid4())

class RootItem(AbstractItem):
    def __init__(self, name,uid=None):
        super().__init__()
        self.name = name
        self.children = []
        self.uid = uid
        self.typeName = "Visibility"
        if uid == None:
            self.uid = str(uuid.uuid4())

class VisibilityItemModel(AbstractItemModel):


    def __init__(self):
        super().__init__()
        self._root_hide = RootItem("Hide")
        self._root_show = RootItem("Show")
        self._root_items = [self._root_hide,self._root_show]

    def get_item_children(self, item):
        if item is None:
            return self._root_items
        return item.children

    def get_item_value_model_count(self, item):
        return 2

    def get_item_value_model(self, item, column_id):
        if column_id == 0:
            return ui.SimpleStringModel(item.name)
        else:
            return ui.SimpleStringModel(item.typeName)

    def get_drag_mime_data(self, item,location):
        return item.name # Simple text for demo

    # Called to test if the drop is acceptable
    def can_drop(self, target_item, source):
        if isinstance(target_item,RootItem):
            return True
        return False

    # Called when dropping
    def drop(self, item_target, item_source):

        data = json.loads(item_source)

        sourceName = data["name"]
        sourcePathStr = data["path"]
        sourceTypeName = data["typename"]

        print(f"Dropped '{item_source}' on '{item_target.name}'")
        item_target.children.append(VisibilityItem(sourceName,sourcePathStr,sourceTypeName))
        self._item_changed(item_target)
        self.refresh_visibility()



    def refresh_visibility(self):
        stage = omni.usd.get_context().get_stage()

        # Hide listed prims
        for item in self._root_hide.children:
            path = item.path
            print(f'hide {path}')
            prim = stage.GetPrimAtPath(path)
            if prim.IsValid() and UsdGeom.Imageable(prim):
                UsdGeom.Imageable(prim).MakeInvisible()

        # Show listed prims
        for item in self._root_show.children:
            path = item.path
            print(f'show {path}')
            prim = stage.GetPrimAtPath(path)
            if prim.IsValid() and UsdGeom.Imageable(prim):
                UsdGeom.Imageable(prim).MakeVisible()
