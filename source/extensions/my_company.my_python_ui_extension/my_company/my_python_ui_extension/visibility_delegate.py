import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
from omni.kit.context_menu import ContextMenuExtension
from omni.kit.context_menu import get_instance as get_context_menu


class VisibilityDelegate(ui.AbstractItemDelegate):
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
        # Offset depents on level
        if column_id == 0:
            # > and v symbols depending on the expanded state
            with ui.HStack():
                if level > 0:
                    ui.Spacer(width=8)
                if level == 0:
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
        # Right click is usually 1
        if button == 0:
            print("show menu")
            context_menu = omni.kit.context_menu.get_instance()
            payload = {"item": item.name}  # custom context data
            menu_items = [
                {
                    "name": "Remove",
                    "glyph": "trash.svg",
                    "onclick_fn": lambda _: self.delete_item(item)
                }
            ]

            context_menu.show_context_menu("Forms Visibility Manager", payload, menu_items)


    def delete_item(self, item):
        for parent in self._model._root_items:
            if item in parent.children:
                parent.children.remove(item)
                self._model._item_changed(parent)
                self._model.refresh_visibility()
                break
