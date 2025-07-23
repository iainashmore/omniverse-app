
import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
from omni.ui import AbstractItemModel, AbstractItem
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
from omni.kit.context_menu import ContextMenuExtension
from omni.kit.context_menu import get_instance as get_context_menu
from .classification_model import ItemKind
from .classification_model import ClassificationItem
from .classification_model import CollectionItem
from .classification_model import PathItem
from .classification_context import ClassificationContext

class ClassificationDelegate(ui.AbstractItemDelegate):
    """
    Delegate is the representation layer. TreeView calls the methods
    of the delegate to create custom widgets for each item.
    """
    _model = None
    _context = ClassificationContext()
    def __init__(self, model):
        super().__init__()
        self._model = model

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        # Offset depents on level
        if column_id == 0:
            text = "     " * (level + 1)
            # > and v symbols depending on the expanded state
            with ui.HStack():
                for i in range(0,level + 1):
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

    def didCheck(self, item):
        print(f"Checkbox toggled for {item.name} => {item._is_editing.get_value()}")
        # Force the TreeView to refresh the row for this item
        self._model._item_changed(item)

    def build_widget(self, model, item, column_id, level, expanded):

        self._model = model   

        if not hasattr(item, "_is_editing"):
            print("defaulting to not editing")
            item._is_editing = ui.SimpleBoolModel(False)
        
        is_editing = item._is_editing
      

        if column_id == 0:
            value_model = model.get_item_value_model(item, column_id)

            with ui.HStack():
                # Spacer for tree indent
                for _ in range(level):
                    ui.Spacer(width=4)

                with ui.HStack():

                    if item._is_editing.get_value_as_bool():
                        field = ui.StringField(value_model, width=120)

                        def on_string_change(model):
                            new_name = model.get_value_as_string()
                            item.name = new_name 

                        value_model.add_value_changed_fn(on_string_change)

                    else:
                        label = ui.Label(item.name + " (" + item.kind.value + ")")

        else:
            with ui.HStack():
                checkbox = ui.CheckBox(width=0)
                checkbox.model = item._is_editing
                checkbox.model.add_value_changed_fn(
                    lambda model: self.checkedEditing(model,item)
                )
                ui.Spacer(width=10)
                ui.Button("", image_url="settings.svg", width=20, height=20, tooltip="More actions",
                          clicked_fn=lambda: self._show_menu_for_item(item))

    def checkedEditing(self,model,item):
        item._is_editing = model
        self._model._item_changed(item)

    def _show_menu_for_item(self, item):
        self._usd_context = omni.usd.get_context()
        selection = self._usd_context.get_selection()
        selectionPaths = selection.get_selected_prim_paths()

        print(selection)
        menu = get_context_menu()

        menuItems = []
        
        menuItems.append({"name": f"Hide All", "onclick_fn": lambda _: self.hideAll(item)})
        menuItems.append({"name": f"Show All", "onclick_fn": lambda _: self.showAll(item)})
        menuItems.append({"name": f"Hide", "onclick_fn": lambda _: self.hide(item)})
        menuItems.append({"name": f"Show", "onclick_fn": lambda _: self.show(item)})
        menuItems.append({"name": f"Only show", "onclick_fn": lambda _: self.showOnly(item)})

        if not isinstance(item,PathItem) and not isinstance(item,CollectionItem):
            menuItems.append(
            {"name": f"Add {ItemKind.Classification.value}", "onclick_fn": lambda _: self.say_hello(item,ItemKind.Classification)},
            )
        if isinstance(item,ClassificationItem):
            menuItems.append(  
            {"name": f"Add selection {ItemKind.Collection.value} ({len(selectionPaths)})", "onclick_fn": lambda _: self.addCollection(item,selectionPaths)}
            )
        if isinstance(item,CollectionItem):
            menuItems.append(  
            {"name": f"Add selection ({len(selectionPaths)})", "onclick_fn": lambda _: self.addSelection(item,selectionPaths)}
            )



        if isinstance(item,PathItem):
            menuItems.append({"name": f"Hide", "onclick_fn": lambda _: self.hideItemPath(item)})
            menuItems.append({"name": f"Show", "onclick_fn": lambda _: self.showItemPath(item)})

        if menu:
            menu.show_context_menu(
                "mymenu",
                {"item": item.name},
                menuItems
            )


    def hideAll(self,item):
        self._context.hideAll()
        
    def showAll(self,item):
        self._context.showAll()

    def hide(self,item):
        self._context.hideChildren(item)
        
    def show(self,item):
        self._context.showChildren(item)

    def showOnly(self,item):
        self._context.isolatePathsByDeactivation(item)

    def say_hello(self,item,kind):
        print(f"Hello {item.name}!")
        self._model.add_child_to_item(kind,item,f"New {kind.value}")

    def addCollection(self,item,paths):
        kind = ItemKind.Collection
        self._model.add_collection_to_item(kind,item,f"New {kind.value}",paths)

    def addSelection(self,item,paths):
        kind = ItemKind.Collection
        self._model.add_selection_to_item(kind,item,f"New {kind.value}",paths)

    def hideItemPath(self,item):
        self._context.hidePath(item.primPath)

    def showItemPath(self,item):
        self._context.showPath(item.primPath)

    def delete_item(self,item):
        print(f"Delete {item.name}")




    def build_header(self, column_id):
        """Build the header"""
        ui.Label("Header", tooltip="Header", height=25)