import omni.ui as ui
import omni.kit.menu.utils
import omni.kit.menu.core

from omni.kit.menu.utils import MenuItemDescription
from omni.kit.menu.utils import MenuHelperExtension
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
import omni.kit.context_menu
from omni.kit.context_menu import ContextMenuExtension

from .classification_model import ClassificationItemModel
from .classification_delegate import ClassificationDelegate

class ClassificationWindow(ui.Window):
    def __init__(self, title: str = None, model:ClassificationItemModel=None, **kwargs):
        super().__init__(title, **kwargs)
        self._context_menu = None
        self._model = model
        self.frame.set_build_fn(self._build_window)

    def _build_window(self):
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._delegate_widget = ClassificationDelegate(self._model)
                tree_view = ui.TreeView(
                    self._model,
                    root_visible=False,
                    header_visible=False,
                    columns_resizable=True,
                    column_widths=[ui.Percent(80),ui.Pixel(50)],
                    style={'TreeView.Item': {'margin': 4}},
                    delegate=self._delegate_widget
                    )
                
