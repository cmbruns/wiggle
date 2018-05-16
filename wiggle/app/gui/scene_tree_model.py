from PyQt5.Qt import QAbstractItemModel
from PyQt5.QtCore import Qt


# https://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel


class SceneNode(object):
    def __init__(self, data, parent, row):
        self.parent = parent
        self.data = data
        self.row = row

    def _get_children(self):
        return [SceneNode(elem, self, index)
                for index, elem in enumerate(self.ref.subelements)]


class SceneTreeModel(QAbstractItemModel):
    def __init__(self, root_elements):
        self.root_elements = root_elements
        super().__init__()
        self.root_nodes = self._get_root_nodes()

    def _get_root_nodes(self):
        return [SceneNode(elem, None, index)
                for index, elem in enumerate(self.root_elements)]

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole and index.column() == 0:
            return node.ref.name
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole \
                and section == 0:
            return 'Name'
        return None

    def rowCount(self, parent):
        return 0
