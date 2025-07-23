
import omni.ui as ui
from .custom_schema import CustomSchema
from .custom_treeview import CustomModel

class CustomWindow(ui.Window):

    indexChange_fn = None
    openNewWindow_fn = None

    def __init__(self, title: str, delegate=None, **kwargs):
    

        super().__init__(title, **kwargs)

        self.indexChange_fn = kwargs.get("indexChange_fn", None)
        self.openNewWindow_fn = kwargs.get("openNewWindow_fn", None)
        self.frame.set_build_fn(self._build_fn)

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        with ui.ScrollingFrame():
             ui.Label("Hello Window")


    def build(self,indexChange_fn=None,openNewWindow_fn=None):
        print("build")
        w = ui.Window(self._title, width=400, height=400)
        self.w = w
 
        print("new func",indexChange_fn)

        with w.frame:
            with ui.VStack():

                combo_model: ui.AbstractItemModel = ui.ComboBox(0, *self.options).model
  
                def _on_left_value_changed(self, *args):
                    index = combo_model.get_item_value_model().get_value_as_int()
                    print(w)
                    print(index)
                    indexChange_fn(index)

                combo_model.add_item_changed_fn(_on_left_value_changed)

                        
                def onClick():
                    print("onClick")
                    openNewWindow_fn("abc")

                ui.Button("Add", clicked_fn=onClick)


                ExploreWidget()

        return w