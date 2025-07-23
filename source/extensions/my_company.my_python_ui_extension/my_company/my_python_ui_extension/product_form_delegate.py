
import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
from omni.kit.context_menu import ContextMenuExtension
from omni.kit.context_menu import get_instance as get_context_menu

from .common import FormKind

class ProductFormDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """
    _model = None

    def __init__(self, model):
        super().__init__()
        self._model = model

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""

        if column_id == 0:

            with ui.HStack():
                for i in range(0,level):
                    ui.Spacer(width=8)
                if len(item.children) > 0:
                    if expanded:
                            img = ui.Image(width=12, height=12,alignment=ui.Alignment.LEFT)
                            img.source_url = "menu_minus.svg"
                            ui.Spacer(width=8)
                    else:
                            img = ui.Image(width=12, height=12,alignment=ui.Alignment.LEFT)
                            img.source_url = "menu_create.svg"
                            ui.Spacer(width=8)
                else:
                    ui.Spacer(width=20)


    def build_widget(self, model, item, column_id, level, expanded):

        value_model = model.get_item_value_model(item, column_id)
        label = ui.Label(value_model.as_string)
        label.set_mouse_released_fn(lambda widget, x, y, button: self.on_mouse_released(item, x, y, button))


    def build_header(self, column_id):
        """Build the header"""
        if column_id == 0:
            ui.Label("Name", tooltip="Name", height=25)
        else:
            ui.Label("Type", tooltip="Type", height=25)


    def on_mouse_released(self, item, x, y, button):
        print("Mouse released button:", button)

        if button == 0:
            print("show menu")
            context_menu = omni.kit.context_menu.get_instance()
            payload = {"item": item.name}
            menu_items = [
                {
                    "name": "Delete",
                    "glyph": "trash.svg",
                    "onclick_fn": lambda _: self.delete_item(item)
                }
            ]

            context_menu.show_context_menu("Viewport", payload, menu_items)


    def delete_item(self, item):
        if item in self._model._root_items:
            self._model._root_items.remove(item)
            self._model._item_changed(None)
        for parent in self._model._root_items:
            if item in parent.children:
                parent.children.remove(item)
                self._model._item_changed(parent)
        self.delete_prim_by_path(item.path)

    def delete_prim_by_path(self,path_str):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("No stage loaded")
            return

        prim = stage.GetPrimAtPath(path_str)
        if not prim.IsValid():
            print(f"Prim at path '{path_str}' is not valid.")
            return

        stage.RemovePrim(path_str)
        print(f"Deleted prim at: {path_str}")
