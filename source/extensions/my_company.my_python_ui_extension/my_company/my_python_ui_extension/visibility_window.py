import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core

from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
import omni.kit.context_menu
from omni.kit.context_menu import ContextMenuExtension
from pxr import Usd, UsdGeom, Sdf

from .visibility_delegate import VisibilityDelegate
from .visibility_model import VisibilityItemModel

class VisibilityWindow(ui.Window):

    def __init__(self, title: str = None, **kwargs):
        super().__init__(title, **kwargs)
        self._tree_model = VisibilityItemModel()
        self.frame.set_build_fn(self._build_window)

    def _build_window(self):

        with ui.VStack():
            with ui.HStack(spacing=10, height=0):
                ui.Button("Refresh", clicked_fn=self._on_refresh_button_clicked)
            self._delegate_widget = VisibilityDelegate(model=self._tree_model)
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
    def _on_refresh_button_clicked(self):
       print("refresh visibility")
       self._tree_model.refresh_visibility()
