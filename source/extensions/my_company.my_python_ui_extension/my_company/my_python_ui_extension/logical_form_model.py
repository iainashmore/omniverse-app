import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
import uuid

from .common import FormKind


class LogicalFormItem(AbstractItem):
    def __init__(self, name, path,uid=None, parent=None):
        super().__init__()
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
        self.uid = uid
        self.typeName = FormKind.Logical.value
        if uid == None:
            self.uid = str(uuid.uuid4())

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        
# Model with multiple items
class LogicalFormItemModel(AbstractItemModel):
    def __init__(self):
        super().__init__()
        self._root_items = []

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
    
    def load(self,primitives):
        self._root_items = []
        for p in primitives:
            new_child = LogicalFormItem(p.GetName(),p.GetPath().pathString)
            print(new_child)
            self._root_items.append(new_child)
        self._item_changed(None)

    def get_drag_mime_data(self, item,location):
        return item.name # Simple text for demo

    # Called to test if the drop is acceptable
    def can_drop(self, target_item, source):
        return True

    # Called when dropping
    def drop(self, item_tagget, item_source):
        print(f"Dropped '{item_source}' on '{item_tagget.name}'")
        # Example: Add a new item under target

