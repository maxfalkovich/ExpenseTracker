import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtSql import QSqlQueryModel
from PyQt6.QtCore import Qt

from ui_main import Ui_MainWindow
from new_entry import Ui_Dialog as NewEntryUI
from edit_entry import Ui_Dialog as EditEntryUI
from connection import Data


class ExpanseTracker(QMainWindow):
    def __init__(self):
        super(ExpanseTracker, self).__init__()
        self.column_names = {
                            "id": "ID",
                            "description": "Описание",
                            "value": "Стоимость",
                            "category": "Категория",
                            "date": "Дата"
                            }
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.conn = Data()
        self.viewData()
        self.reloadData()

        self.ui.addButton.clicked.connect(self.openAddEntryWindow)
        self.ui.editButton.clicked.connect(self.openEditEntryWindow)
        self.ui.deleteButton.clicked.connect(self.deleteEntry)
        self.ui.dateCheckBox.stateChanged.connect(self.updateDateCheckBox)
        self.ui.categoryCheckBox.stateChanged.connect(self.updateCategoryCheckBox)
        self.ui.categoryComboBox.currentIndexChanged.connect(self.viewData)
        self.ui.dateEdit.dateChanged.connect(self.viewData)

    def reloadData(self):
        self.ui.balanceDynamicLabel.setText(self.conn.getBalance())

    def viewData(self):
        date_cb = self.ui.dateCheckBox.isChecked()
        category_cb = self.ui.categoryCheckBox.isChecked()
        date = self.ui.dateEdit.text()
        category = self.ui.categoryComboBox.currentText()
        query = self.conn.getTableWithFilters(date_cb, category_cb, date, category)
        self.model = QSqlQueryModel(self)
        self.model.setQuery(query)

        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Описание")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Сумма")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Категория")
        self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Дата")
        self.ui.tableView.setModel(self.model)

        self.ui.tableView.setColumnWidth(1, 400)
        self.ui.tableView.setColumnWidth(0, 66)
        self.ui.tableView.setColumnWidth(2, 120)
        self.ui.tableView.setColumnWidth(3, 210)
        self.ui.tableView.setColumnWidth(4, 110)

    def updateCategoryCheckBox(self):
        if self.ui.categoryCheckBox.isChecked():
            self.ui.categoryComboBox.setDisabled(True)
        else:
            self.ui.categoryComboBox.setEnabled(True)
        self.viewData()

    def updateDateCheckBox(self):
        if self.ui.dateCheckBox.isChecked():
            self.ui.dateEdit.setDisabled(True)
        else:
            self.ui.dateEdit.setEnabled(True)
        self.viewData()

    def showNoSelectionMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Ничего не выделено")
        msg.setText("Пожалуйста, сначала выделите ID нужной записи")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def openAddEntryWindow(self):
        self.window = QtWidgets.QDialog()
        self.addEntryWindow = NewEntryUI()
        self.addEntryWindow.setupUi(self.window)
        self.window.show()
        self.addEntryWindow.saveButton.clicked.connect(self.addEntry)

    def openEditEntryWindow(self):
        selected_indexes = self.ui.tableView.selectedIndexes()
        if selected_indexes and selected_indexes[0].column() == 0:
            self.window = QtWidgets.QDialog()
            self.editEntryWindow = EditEntryUI()
            self.editEntryWindow.setupUi(self.window)
            self.window.show()
            self.editEntryWindow.saveButton.clicked.connect(self.editEntry)
        else:
            self.showNoSelectionMessage()

    def addEntry(self):
        description = self.addEntryWindow.descriptionLineEdit.text()
        value = self.addEntryWindow.priceSpinBox.text()
        category = self.addEntryWindow.categoryComboBox.currentText()
        date = self.addEntryWindow.dateEdit.text()

        self.conn.insertEntry(description, value, category, date)
        self.viewData()
        self.reloadData()
        self.window.close()

    def editEntry(self):
        index = self.ui.tableView.selectedIndexes()[0]
        id = str(self.ui.tableView.model().data(index))

        description = self.editEntryWindow.descriptionLineEdit.text()
        value = self.editEntryWindow.priceSpinBox.text()
        category = self.editEntryWindow.categoryComboBox.currentText()
        date = self.editEntryWindow.dateEdit.text()

        self.conn.updateEntry(description, value, category, date, id)
        self.viewData()
        self.reloadData()
        self.window.close()

    def deleteEntry(self):
        selected_indexes = self.ui.tableView.selectedIndexes()
        if selected_indexes and selected_indexes[0].column() == 0:
            id = str(self.ui.tableView.model().data(selected_indexes[0]))
            self.conn.deleteEntry(id)
            self.viewData()
            self.reloadData()
        else:
            self.showNoSelectionMessage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpanseTracker()
    window.show()

    sys.exit(app.exec())
