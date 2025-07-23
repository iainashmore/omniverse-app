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
from pxr import UsdGeom

class ClassificationContext():

    def __init__(self):
    
        super().__init__()

        self._usd_context = omni.usd.get_context()
        self._stage = omni.usd.get_context().get_stage()


    def splitPath(self,path,backOffset):
        newPath = ""
        paths = path.split("/")
        for i in range(len(paths) + backOffset):
            newPath += paths[i] + "/"
        return newPath[:-1]
    
      
    def getPathParents(self,fullPath):
        paths = []
        pathSteps = fullPath.split("/")
        for i in range(len(pathSteps)):
            path = ""
            for k in range(i):
                path += pathSteps[k] + "/"
            paths.append(path[:-1])
        return paths

    def basePath(self,path):
        return path.split("/")[0]

    def hidePath(self,path):
        self._usd_context = omni.usd.get_context()
        self._stage = omni.usd.get_context().get_stage()
        parentPath = self.splitPath(path,-1)
        prim = self._stage.GetPrimAtPath(parentPath)

        if not prim.IsValid():
            print(f"[ERROR] Prim not found: {self.prim_path}")
            return
        
        prim.SetActive(False)




    def showChildren(self,item):
        for child in item.children:
            if isinstance(child,PathItem):
                self.showPath(child.primPath)
            self.showChildren(child)

    def showPath(self,path):
        self._usd_context = omni.usd.get_context()
        self._stage = omni.usd.get_context().get_stage()
        parentPath = self.splitPath(path,-1)
        prim = self._stage.GetPrimAtPath(parentPath)

        if not prim.IsValid():
            print(f"[ERROR] Prim not found: {self.prim_path}")
            return
        
        prim.SetActive(True)


    def reactivateAllUnder(self, root_path):
        stage = self._usd_context.get_stage()
        for prim in stage.Traverse():
            if prim.GetPath().pathString.startswith(root_path) and not prim.IsActive():
                prim.SetActive(True)


    def isolatePathsByDeactivation(self, root_item):
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()

        #self.deactivateAll()

        self.activate(root_item)

    def get_scene_root_prefix(self):
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        pseudo_root = self._stage.GetPseudoRoot()
        top_level_prims = [prim for prim in pseudo_root.GetChildren() if prim.IsValid()]

        # Filter out known system nodes
        system_names = {"Render", "OmniverseKit", "HydraTextures"}
        scene_roots = [p for p in top_level_prims if p.GetName() not in system_names]

        if scene_roots:
            return "/" + scene_roots[0].GetName()

        return "/"  # fallback if no scene root found


    def deactivateAll(self):
        root_prefix = self.get_scene_root_prefix()

        for prim in self._stage.Traverse():
            path = prim.GetPath().pathString
            print("looking at " + path)
            if path.startswith(root_prefix):
                print("deativating " + path)
                if prim.IsActive():
                   prim.SetActive(False)


    def getPathItems(self,item,pathItems):
        for child in item.children:
            if isinstance(child,PathItem):
               pathItems.append(child)
            self.getPathItems(child,pathItems)

    def activate(self, item):
        self._stage = self._usd_context.get_stage()
        print("Activating from:", item.name)

        # Step 1: Collect selected path items
        path_items = []
        self.getPathItems(item, path_items)

        # Step 2: Build required path set (selected items + all ancestors)
        required_paths = set()
        for path_item in path_items:
            print("Selected item:", path_item.name)
            parts = path_item.primPath.strip("/").split("/")
            for i in range(1, len(parts) + 1):
                path = "/" + "/".join(parts[:i])
                required_paths.add(path)

        # Step 3: Activate all required paths
        for path in required_paths:
            prim = self._stage.GetPrimAtPath(path)
            if prim.IsValid() and not prim.IsActive():
                print("Activating:", path)
                prim.SetActive(True)

        # Step 4: Recursively deactivate non-required sibling trees
        for path in required_paths:
            prim = self._stage.GetPrimAtPath(path)
            if not prim.IsValid():
                continue

            parent = prim.GetParent()
            if not parent or parent.IsPseudoRoot():
                continue

            for sibling in parent.GetChildren():
                sibling_path = sibling.GetPath().pathString
                if sibling_path in required_paths:
                    continue
                if sibling.IsActive():
                    print("Deactivating sibling tree:", sibling_path)
                    self._deactivate_recursive(sibling, required_paths)


    def _deactivate_recursive(self, prim, required_paths):
        if not prim.IsValid():
            return
        path = prim.GetPath().pathString
        if path not in required_paths and prim.IsActive():
            print("Deactivating:", path)
            prim.SetActive(False)
        for child in prim.GetChildren():
            self._deactivate_recursive(child, required_paths)

    def _activate(self,item):
        self._stage = self._usd_context.get_stage()
        print("Activate from.. " + item.name)
        pathItems = []
        self.getPathItems(item,pathItems)
        lineItems = []
        for pathItem in pathItems:
            print(pathItem.name)
            parents = pathItem.primPath.split("/")
            lineItem = []
            for i in range(len(parents)):
                self._insert_at_index(lineItem,i,parents[i])
            lineItems.append(lineItem[1:])

        for i in range(len(lineItems)):
            path = ""
            for j in range(len(lineItems[i])):
                path += lineItems[i][j] + "/"
                print("Checking path","/" + path[:-1])
                prim = self._stage.GetPrimAtPath("/" + path[:-1])
                if prim.IsValid():
                    print(".Found prim:", prim.GetName())
                    parent = prim.GetParent()
                    print("..Found parent", parent.GetName())
                    if parent.GetName() == "/":
                        if prim.IsValid():
                            if not prim.IsActive():
                                prim.SetActive(True)
                    else:
                        childPaths = []
                        for e in range(len(lineItems)):
                            childPath = ""
                            print(lineItems[e])
                            for f in range(j+1):
                                if f <= len(lineItems[e]):
                                    childPath += lineItems[e][f] + "/"
                            childPath = "/" + childPath[:-1]
                            childPaths.append(childPath)
                            print("....selected paths include", childPath)
                            
                        for child in parent.GetChildren():
                            print("...Child path:", child.GetPath().pathString)
                            
                            if child.GetPath().pathString in childPaths:
                                print(".....Is valid path",child.GetPath().pathString)
                                if not child.IsActive():
                                    child.SetActive(True)
                            else:
                                print(".....Is NOT valid path",child.GetPath().pathString)
                                if child.IsActive():
                                    child.SetActive(False)



    def _insert_at_index(self,lst, index, value, fill=None):
        if index >= len(lst):
            lst.extend([fill] * (index - len(lst)))
            lst.append(value)
        else:
            lst.insert(index, value)


    def _reactivatePathItemsUpward(self, item):
        if isinstance(item, PathItem):
            self._reactivateItemAndParents(item)

        for child in item.children:
            self._reactivatePathItemsUpward(child)

    def _reactivateItemAndParents(self, item):
        print("not implemented")


    def _get_branching_root_path(self, item):
        # If this is a leaf node, return its primPath (or root fallback)
        if not hasattr(item, "children") or not item.children:
            return getattr(item, "primPath", "/")

        # If branching (more than one child), this is our root
        if len(item.children) > 1:
            return getattr(item, "primPath", "/")

        # Only one child, keep going deeper
        return self._get_branching_root_path(item.children[0])



    def _get_root_path(self, item):
        for child in item.children:
            if isinstance(child, PathItem):
                path = child.primPath
                return "/" + path.strip("/").split("/")[0]  # Get top-level root
            else:
                return self._get_root_path(child)
        return "/"


    def _showItemAndParents(self, item):
        for child in item.children:
            if isinstance(child, PathItem):
                self._showPathAndParents(child.primPath)
            self._showItemAndParents(child)

    def _showPathAndParents(self, path):
        stage = self._usd_context.get_stage()
        path_parts = path.strip("/").split("/")

        for i in range(1, len(path_parts) + 1):
            subpath = "/" + "/".join(path_parts[:i])
            prim = stage.GetPrimAtPath(subpath)

            if prim.IsValid() and UsdGeom.Imageable(prim):
                UsdGeom.Imageable(prim).MakeVisible()


    def hideChildren(self,item):
        for child in item.children:
            if isinstance(child,PathItem):
                self.hidePath(child.primPath)
            self.hideChildren(child)

    def showChildrenOnly(self,item):
        self.isolatePathsByDeactivation(item)

    def showChildren(self,item):
        for child in item.children:
            if isinstance(child,PathItem):
                self.showPath(child.primPath)
            self.showChildren(child)

    def hideAll(self):
        self.deactivateAll()


    def showAll(self):
        root_prefix = self.get_scene_root_prefix()

        for prim in self._stage.Traverse():
            path = prim.GetPath().pathString
            if not path.startswith(root_prefix):
                continue
            if not prim.IsActive():
                prim.SetActive(True)