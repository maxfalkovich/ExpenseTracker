# Модуль для работы с графическим интерфейсом приложения учета расходов с использованием PyQt6.
#
# Класс ExpanseTracker отвечает за:
# - Инициализацию главного окна приложения.
# - Установку соединения с базой данных.
# - Отображение и обновление данных из базы данных.
# - Обработку пользовательских взаимодействий, таких как добавление, редактирование и удаление записей.
# - Открытие окон добавления и редактирования записей.
# - Фильтрацию данных по дате и категории.


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
        """
        Инициализирует главное окно приложения, устанавливает соединение с базой данных,
        отображает актуальные данные и подключает сигналы к слотам.
        """
        super(ExpanseTracker, self).__init__()

        # Инициализация главного окна
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Установка соединения с базой данных
        self.conn = Data()

        # Отображение и обновление данных
        self.viewData()
        self.reloadData()

        # Подключение сигналов к слотам
        self.ui.addButton.clicked.connect(self.openAddEntryWindow)
        self.ui.editButton.clicked.connect(self.openEditEntryWindow)
        self.ui.deleteButton.clicked.connect(self.deleteEntry)
        self.ui.dateCheckBox.stateChanged.connect(self.updateDateCheckBox)
        self.ui.categoryCheckBox.stateChanged.connect(self.updateCategoryCheckBox)
        self.ui.categoryComboBox.currentIndexChanged.connect(self.viewData)
        self.ui.dateEdit.dateChanged.connect(self.viewData)

    def reloadData(self):
        """
        Перезагружает данные баланса.
        """
        self.ui.balanceDynamicLabel.setText(self.conn.getBalance())

    def viewData(self):
        """
        Отображает данные из базы данных с учетом фильтров.
        """
        # Получение и выполнение запроса с фильтрами
        date_cb = self.ui.dateCheckBox.isChecked()
        category_cb = self.ui.categoryCheckBox.isChecked()
        date = self.ui.dateEdit.text()
        category = self.ui.categoryComboBox.currentText()
        query = self.conn.getTableWithFilters(date_cb, category_cb, date, category)
        self.model = QSqlQueryModel(self)
        self.model.setQuery(query)

        # Замена заголовков колонок на русский язык
        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Описание")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Сумма")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Категория")
        self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Дата")
        self.ui.tableView.setModel(self.model)

        # Настройка ширины колонок
        self.ui.tableView.setColumnWidth(1, 400)
        self.ui.tableView.setColumnWidth(0, 66)
        self.ui.tableView.setColumnWidth(2, 120)
        self.ui.tableView.setColumnWidth(3, 210)
        self.ui.tableView.setColumnWidth(4, 110)

    def updateCategoryCheckBox(self):
        """
        Обновляет состояние categoryComboBox в зависимости от состояния categoryCheckBox.
        """
        if self.ui.categoryCheckBox.isChecked():
            self.ui.categoryComboBox.setDisabled(True)
        else:
            self.ui.categoryComboBox.setEnabled(True)
        self.viewData()

    def updateDateCheckBox(self):
        """
        Обновляет состояние dateEdit в зависимости от состояния dateCheckBox.
        """
        if self.ui.dateCheckBox.isChecked():
            self.ui.dateEdit.setDisabled(True)
        else:
            self.ui.dateEdit.setEnabled(True)
        self.viewData()

    def showNoSelectionMessage(self):
        """
        Показывает предупреждение при попытке редактирования записи,
        если ни одна запись не выбрана.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Не выбрана запись")
        msg.setText("Пожалуйста, сначала выберите ID нужной записи")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def openAddEntryWindow(self):
        """
        Открывает окно для добавления новой записи.
        """
        self.window = QtWidgets.QDialog()
        self.addEntryWindow = NewEntryUI()
        self.addEntryWindow.setupUi(self.window)
        self.window.show()
        self.addEntryWindow.saveButton.clicked.connect(self.addEntry)

    def openEditEntryWindow(self):
        """
        Открывает окно для редактирования выбранной записи.
        """
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
        """
        Добавляет новую запись в базу данных.
        """
        description = self.addEntryWindow.descriptionLineEdit.text()
        value = self.addEntryWindow.priceSpinBox.text()
        category = self.addEntryWindow.categoryComboBox.currentText()
        date = self.addEntryWindow.dateEdit.text()

        self.conn.insertEntry(description, value, category, date)
        self.viewData()
        self.reloadData()
        self.window.close()

    def editEntry(self):
        """
        Редактирует выбранную запись в базе данных.
        """
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
        """
        Удаляет выбранную запись из базы данных.
        """
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
