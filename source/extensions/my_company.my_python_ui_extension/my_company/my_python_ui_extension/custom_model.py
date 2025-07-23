import omni.ui as ui
import omni.kit.menu.core

class XItem(ui.AbstractItem):
    def __init__(self, title,x):
        super().__init__()
        self.title = title
        self.x = x

    def __repr__(self):
        return f'"{self.title} {self.x}"'

class CustomModel(ui.AbstractItemModel):

    customSchema = None
    customData = None
    _filter = False
    _children = []
    def __init__(self, customData=None, customSchema=None, filter = True):
        super().__init__()
        self.customData = customData
        self.customSchema = customSchema
        self._children = []
        a = self.addCustomItem("hello")
        self._children.append(a)
        self._filter = filter
        self.load()
         # emit data changed

    def load(self):
        nodes = self.customData.getNodes()
        for node in nodes:
            c = XItem(node,"x")
            c = self.addCustomItem(node)
            self._children.append(c)

        self._item_changed(None)

    def get_item_children(self, item):
        self.refresh()
        print("get_item_children")
        items = []

        if item is not None:
            return []

        return self._children

    def addNewObjectType(self,index):
        print("addNewObjectType", str(index))
        typeName = self.customSchema.getCustomObjectTypes()[index]["name"]
        print("Trying to add:" + typeName)
        self.customData.addNode(typeName)
        a = XItem(typeName,"x")
        self._item_changed(None)
        return a

    def addCustomItem(self,title):
        print("adding " + title)
        a = XItem(title,"x")
        self._item_changed(a)
        return a

    def addNewCustomItem(self,title):
        a = self.addCustomItem(title)
        self._children.append(a)

    def refresh(self):
        ##self._item_changed(None)
        print("refreshing tree")
        return
        self._children = []
        nodes = self.customData.getNodes()
        for node in nodes:
            c = XItem(node,"x")
            c = self.addCustomItem(node)
            self._children.append(c)

        self._item_changed(None)

        #self.addNode()
        #self.get_item_children(None)

    def addNode(self):
        print("custom model add node")
        #item = self.append_child_item(CustomItem("d"))



    def get_item_value_model_count(self, item):
        return 1  # Adjust if you need more columns

    def get_item_value_model(self, item, column_id):
        print(item)
        if item and isinstance(item, XItem):

            x = ui.SimpleStringModel("x"+item.title)
            return x
        else:
            return ui.SimpleStringModel(item.title)