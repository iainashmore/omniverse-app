import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core

from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
import omni.kit.context_menu
from omni.kit.context_menu import ContextMenuExtension
from pxr import Usd, UsdGeom, Sdf

from .product_form_model import ProductFormItemModel
from .product_form_delegate import ProductFormDelegate
from .common import FormKind

import json

class ComboItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.model = ui.SimpleStringModel(text)

class ComboModel(ui.AbstractItemModel):
    def __init__(self,items = [],index=0):
        super().__init__()

        self._current_index = ui.SimpleIntModel(index)

        self._items = [
            ComboItem(text)
            for text in items
        ]

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model


class ProductFormWindow(ui.Window):


    def __init__(self, title: str = None, openNewWindow_fn  = None, index = 0, **kwargs):
        super().__init__(title, **kwargs)
        self._index = index
        self._usd_context = omni.usd.get_context()
        self._stage = omni.usd.get_context().get_stage()
        self._options = ["ProductForm", "LogicalForm","DesignForm"]
        self._name_model = ui.SimpleStringModel(f"New {self._options[self._index]}")
        self._tree_model = ProductFormItemModel(_on_drag_drop_fn=self._on_drag_drop)
        self.frame.set_build_fn(self._build_window)
        self._openNewWindow_fn = openNewWindow_fn
        self.refresh()



    def _on_selected_option_value_changed(self, *args):
        self._index = self._combo_model.get_item_value_model().get_value_as_int()
        print(f"selected {self._index } {self._options[self._index]}")
        self._name_model.set_value(f"New {self._options[self._index]}")
        self.refresh()

    def _build_window(self):

        with ui.VStack():

            with ui.HStack(spacing=10, height=0):
                self._combo_model: ui.AbstractItemModel = ui.ComboBox(0, *self._options).model
                self._combo_model.get_item_value_model().set_value(self._index)
                self._combo_model.add_item_changed_fn(self._on_selected_option_value_changed)
                ui.Button("Open", clicked_fn=self._on_open_button_clicked)

            with ui.HStack(spacing=10, height=0):
                self._nameField = ui.StringField(model=self._name_model)
                ui.Button("Add", clicked_fn=self._on_add_button_clicked)


            with ui.HStack(spacing=10, height=0):
                ui.Button("Refresh", clicked_fn=self._on_refresh_button_clicked)

            self._delegate_widget = ProductFormDelegate(self._tree_model)

            tree_view = ui.TreeView(
                self._tree_model,
                drag_drop=True,
                root_visible=False,
                header_visible=True,
                columns_resizable=True,
                column_widths=[ui.Percent(60),ui.Percent(40)],
                style={'TreeView.Item': {'margin': 4}},
                delegate=self._delegate_widget
                )


    def _on_add_button_clicked(self):
        print("Hello from Omniverse!")
        name = self._name_model.as_string.strip().replace(" ", "_")
        path = Sdf.Path(f"/{name}")
        print(path)
        xform = self.create_tagged_xform(self._stage, path, self._options[self._index])
        self.refresh()

    def _on_open_button_clicked(self):
        print("Open from Omniverse!")
        print(f"Open {self._options[self._index]}")
        self._openNewWindow_fn(self._index)


    def _on_refresh_button_clicked(self):
        self.refresh()

    def _on_drag_drop(self,source,target):
        print("drag drop")

        print(f"_on_drag_drop '{source}' on '{target}'")

        targetName = target.name
        targetPathStr = target.path
        targetTypeName = target.typeName
        print(f"target '{targetName}' '{targetPathStr}' '{targetTypeName}'")

        data = json.loads(source)

        sourceName = data["name"]
        sourcePathStr = data["path"]
        sourceTypeName = data["typename"]

        print(f"source '{sourceName}' '{sourcePathStr}' '{sourceTypeName}'")

        targetPath = Sdf.Path(targetPathStr)
        sourcePath = Sdf.Path(sourcePathStr)

        instanceName = self.get_instance_name(targetPathStr,sourceName)

        instancePath = targetPath.AppendChild(f"{instanceName}")

        #instancePath = targetPath.AppendChild(f"{sourceName}")

        # Get the current USD stage
        stage = omni.usd.get_context().get_stage()

        # Create the instance prim under target
        instance = UsdGeom.Xform.Define(stage, instancePath)

        # Add a reference to the source prim
        instance.GetPrim().GetReferences().AddInternalReference(sourcePath)

        prim = stage.GetPrimAtPath(instancePath)

        prim.SetMetadata("customData", {"class":  "Instance" + sourceTypeName})

        self._tree_model.add_instance(target,prim)



    def get_instance_name(self, source_path_str, base_name):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("No stage loaded")
            return None

        sdf_path = Sdf.Path(source_path_str)
        source_prim = stage.GetPrimAtPath(sdf_path)

        if not source_prim.IsValid():
            print(f"Invalid prim at path: {source_path_str}")
            return None

        # Get all existing child names under the source prim
        child_names = {child.GetName() for child in source_prim.GetChildren()}

        # Start from 1 and keep incrementing until name is not taken
        count = 0
        candidate_name = f"{base_name}"
        while True:
            if candidate_name not in child_names:
                return candidate_name
            count += 1
            candidate_name = f"{base_name}_{count}"



    def refresh(self):
        self._usd_context = omni.usd.get_context()
        stage = self._usd_context.get_stage()
        special_prims = self.find_prims_by_class(stage, self._options[self._index])
        self._tree_model.load(special_prims,self._options[self._index])

    def create_tagged_xform(self,stage, path: str, tag: str):
        stage = self._usd_context.get_stage()
        xform = UsdGeom.Xform.Define(stage, Sdf.Path(path))
        xform.GetPrim().SetMetadata("customData", {"class": tag})
        return xform


    def find_prims_by_class(self,stage: Usd.Stage, class_name: str):
        """Recursively find prims with CustomData['class'] == class_name and collect their children as nested results."""

        def build_tree(prim):
            """Build a recursive structure starting from prim."""
            return {
                "prim": prim,
                "instances": [build_tree(child) for child in prim.GetChildren()]
            }

        results = []

        if not stage:
            return results

        for prim in stage.Traverse():
            if not prim.IsActive() or not prim.IsDefined():
                continue

            custom_data = prim.GetCustomData()
            if custom_data.get("class") == class_name:
                results.append(build_tree(prim))

        return results




    def get_scene_root_prefix(self):
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        pseudo_root = self._stage.GetPseudoRoot()
        top_level_prims = [prim for prim in pseudo_root.GetChildren() if prim.IsValid()]

        system_names = {"Render", "OmniverseKit", "HydraTextures"}
        scene_roots = [p for p in top_level_prims if p.GetName() not in system_names]

        if scene_roots:
            return "/" + scene_roots[0].GetName()

        return "/"
