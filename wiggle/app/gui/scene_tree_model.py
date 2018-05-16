from PyQt5.Qt import QAbstractItemModel, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt


# https://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel


class SceneTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__(1, 3)
        self.setHorizontalHeaderLabels(['Item', 'Show', 'Value'])
        # Label
        self.setItem(0, 0, QStandardItem('Antialias'))
        # Visibility checkbox
        checkItem = QStandardItem('')
        checkItem.setCheckable(True)
        checkItem.setCheckState(Qt.Checked)
        self.setItem(0, 1, checkItem)
        # sample count # todo spinbox
        sampleCount = QStandardItem('X')
        self.setItem(0, 2, sampleCount)

