import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core

from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
import omni.kit.context_menu
from omni.kit.context_menu import ContextMenuExtension
from pxr import Usd, UsdGeom, Sdf

from .logical_form_model import LogicalFormItemModel
from .logical_form_delegate import LogicalFormDelegate
from .common import FormKind

class LogicalFormWindow(ui.Window):
    def __init__(self, title: str = None, **kwargs):
        super().__init__(title, **kwargs)
        self._usd_context = omni.usd.get_context()
        self._stage = omni.usd.get_context().get_stage()
        self._name_model = ui.SimpleStringModel(f"New {FormKind.Logical.value}")
        self._tree_model = LogicalFormItemModel()
        self.frame.set_build_fn(self._build_window)

    def _build_window(self):
        with ui.VStack( height=0):
            with ui.HStack(spacing=10, height=0):
                ui.StringField(model=self._name_model)
                ui.Button("Add", clicked_fn=self._on_add_button_clicked)
            
           
            self._delegate_widget = LogicalFormDelegate(self._tree_model)
            ui.Button("Refresh", clicked_fn=self._on_refresh_button_clicked)
            tree_view = ui.TreeView(
                self._tree_model,
                drag_drop=True,
                root_visible=False,
                header_visible=True,
                columns_resizable=True,
                column_widths=[ui.Percent(70),ui.Percent(30)],
                style={'TreeView.Item': {'margin': 4}},
                    delegate=self._delegate_widget
                )
            
    def _on_add_button_clicked(self):
        print("Hello from Omniverse!")
        name = self._name_model.as_string.strip().replace(" ", "_")
        path = Sdf.Path(f"/{name}")
        print(path)
        xform = self.create_tagged_xform(self._stage, path, FormKind.Logical.value)
        self.refresh()

    def _on_refresh_button_clicked(self):
        self.refresh()

    def refresh(self):
        self._usd_context = omni.usd.get_context()
        stage = self._usd_context.get_stage()
        special_prims = self.find_prims_by_class(stage, FormKind.Logical.value)
        self._tree_model.load(special_prims)
        print("Found:", [p.GetPath() for p in special_prims]) 

    def create_tagged_xform(self,stage, path: str, tag: str):
        stage = self._usd_context.get_stage()
        xform = UsdGeom.Xform.Define(stage, Sdf.Path(path))
        xform.GetPrim().SetMetadata("customData", {"class": tag})
        return xform
    
    def find_prims_by_class(self,stage, class_name: str):
        results = []
        for prim in stage.Traverse():
            if prim.HasCustomData():
                data = prim.GetCustomData()
                if data.get("class") == class_name:
                    results.append(prim)
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


                