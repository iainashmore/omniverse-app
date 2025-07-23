import carb
import asyncio
import omni.ext
import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core
import carb.events
from omni.ui import AbstractItemModel, AbstractItem
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
from omni.kit.context_menu import ContextMenuExtension
from omni.kit.context_menu import get_instance as get_context_menu
import omni.kit.widget.stage
import omni.kit.context_menu
from .classification_window import ClassificationWindow
from .classification_model import ClassificationItemModel
from .product_form_window import ProductFormWindow
from .logical_form_window import LogicalFormWindow
from .visibility_window import VisibilityWindow

from functools import partial
import asyncio





class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.


    _window_count = 1

    def on_startup(self):
  
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._stage_event_stream = self._usd_context.get_stage_event_stream()

        self._stage_event_sub = self._stage_event_stream.create_subscription_to_pop(
            self._on_stage_event,
            name="My Stage Event Subscription"
        )

        ProductFormWindow(f"Forms Manager ({str(self._window_count)})", openNewWindow_fn=self.openNewWindow, index=0, width=300, height=300)
        self._window_count += 1
        ProductFormWindow(f"Forms Manager ({str(self._window_count)})", openNewWindow_fn=self.openNewWindow, index=1, width=300, height=300)
        VisibilityWindow("Forms Visibility Manager",width=300, height=300)
        self._window_count += 1
        
        def hello_world(objects):
            print(f"Hello Objects: {objects}")

        menu = {'name': 'Assign'}
        self._my_custom_menu = omni.kit.context_menu.add_menu(menu, 'MENU', 'omni.kit.viewport.window')

      

    def on_mouse_event(self, event):
        print("mouse event")


    def build_custom_menu(self):
        return [
            {
                "name": "Hello World!",
                "glyph": "menu_search.svg",  # optional icon
                "onclick": lambda: self.on_click,
            }
        ]

    def on_click(self,df):

        print(f"Assign to {df.GetName()}")


    def openNewWindow(self,index=0):
        print(f"open index {str(index)}")     
        ProductFormWindow(f"Forms Manager ({str(self._window_count)})", openNewWindow_fn=self.openNewWindow,index=index,width=300, height=300)
        self._window_count += 1   

    def on_shutdown(self):
         self.menu_shutdown()

  

       
    def _on_stage_event(self, e):
        if e.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            print("[INFO] Selection changed!")
            self._on_selection_changed()

       
    _assign_menu_ids = []
    def _on_selection_changed(self):
        
        selection = self._selection.get_selected_prim_paths()
        stage = self._usd_context.get_stage()
        print(f"== selection changed with {len(selection)} items")
        if selection and stage:
            #-- set last selected element in property model 
            for selected_path in selection:
                print(f" item {selected_path}:")
            
            designForms = self.find_prims_by_class(stage, "DesignForm")
            #menu_dict = omni.kit.context_menu.get_menu_dict("ADD")
            #print(menu_dict)
            for designForm in designForms:
                mf = designForm.GetName()
                md = { "name": f"To {mf}", "onclick_fn": lambda df=designForm: self.on_click(designForm) }
                menu_id = omni.kit.context_menu.add_menu(md, "ADD", "omni.kit.viewport.window")
                self._assign_menu_ids.append(menu_id)


    def find_prims_by_class(self,stage, class_name: str):

        results = []

        if not stage:
            return results

        for prim in stage.Traverse():
            if not prim.IsActive() or not prim.IsDefined():
                continue

            custom_data = prim.GetCustomData()
            if custom_data.get("class") == class_name:
                results.append(prim)

        return results

    def on_shutdown(self):        
        # cleanup 
        self._window = None
        self._stage_event_sub = None
    