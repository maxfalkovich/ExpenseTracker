# Модуль для работы с базой данных расходов с использованием PyQt6 и SQLite.
#
# Класс Data предоставляет методы для создания соединения с базой данных,
# выполнения SQL-запросов и управления записями в таблице расходов.


from PyQt6 import QtSql


class Data:
    def __init__(self):
        """
        Инициализирует объект Data и создает соединение с базой данных.
        """
        super(Data, self).__init__()
        self.createConnection()

    def createConnection(self):
        """
        Создает соединение с базой данных и создает таблицу расходов, если она не существует.
        """
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("expensetracker.db")
        db.open()
        query = QtSql.QSqlQuery()
        if not query.exec("CREATE TABLE IF NOT EXISTS expenses ("
                          "id integer PRIMARY KEY AUTOINCREMENT NOT NULL,"
                          "description VARCHAR(32) NOT NULL,"
                          "value integer NOT NULL,"
                          "category VARCHAR(32) NOT NULL,"
                          "date DATE NOT NULL)"):
            print(query.lastError().text())

    def executeQuery(self, query_text, query_values=None):
        """
        Выполняет подготовленный SQL-запрос.

        Args:
            query_text (str): Текст SQL-запроса.
            query_values (list, optional): Список значений для подстановки в запрос.

        Returns:
            QtSql.QSqlQuery: Объект QtSql.QSqlQuery с результатами выполнения запроса.
        """
        query = QtSql.QSqlQuery()
        query.prepare(query_text)
        if query_values:
            for value in query_values:
                query.addBindValue(value)

        if not query.exec():
            print(query.lastError().text())
        return query

    def insertEntry(self, description, value, category, date):
        """
        Вставляет новую запись в таблицу расходов.

        Args:
            description (str): Описание расхода.
            value (int): Сумма расхода.
            category (str): Категория расхода.
            date (str): Дата расхода.
        """
        query_text = "INSERT INTO expenses (description, value, category, date) VALUES (?, ?, ?, ?)"
        self.executeQuery(query_text, [description, value, category, date])

    def updateEntry(self, description, value, category, date, entry_id):
        """
        Обновляет существующую запись в таблице расходов.

        Args:
            description (str): Описание расхода.
            value (int): Сумма расхода.
            category (str): Категория расхода.
            date (str): Дата расхода.
            entry_id (int): Идентификатор записи для обновления.
        """
        query_text = "UPDATE expenses SET description=?, value=?, category=?, date=? WHERE id=?"
        self.executeQuery(query_text, [description, value, category, date, entry_id])

    def deleteEntry(self, entry_id):
        """
        Удаляет запись из таблицы расходов.

        Args:
            entry_id (int): Идентификатор записи для удаления.
        """
        query_text = "DELETE FROM expenses WHERE id=?"
        self.executeQuery(query_text, [entry_id])

    def getBalance(self):
        """
        Возвращает баланс доходов и расходов.

        Returns:
            str: Баланс доходов и расходов.
        """
        income_value, outcome_value = 0, 0
        query_text = "SELECT SUM(value) FROM expenses WHERE category='Поступления'"
        query = self.executeQuery(query_text)
        if query.next():
            income_value = query.value(0) or 0

        query_text = "SELECT SUM(value) FROM expenses WHERE category<>'Поступления'"
        query = self.executeQuery(query_text)
        if query.next():
            outcome_value = query.value(0) or 0

        return str(int(income_value - outcome_value))

    def getTableWithFilters(self, date_cb, category_cb, date, category):
        """
        Возвращает записи из таблицы расходов с применением фильтров по дате и категории.

        Args:
            date_cb (bool): Флаг использования фильтра по дате.
            category_cb (bool): Флаг использования фильтра по категории.
            date (str): Дата для фильтра в формате 'YYYY-MM-DD'.
            category (str): Категория для фильтра.

        Returns:
            QtSql.QSqlQuery: Объект QtSql.QSqlQuery с результатами выполнения запроса.
        """
        query_text = "SELECT * FROM expenses"
        query_values = []
        conditions = []

        if date_cb == False:
            conditions.append("date=?")
            query_values.append(date)
        if category_cb == False:
            conditions.append("category=?")
            query_values.append(category)

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)
        query = self.executeQuery(query_text, query_values)

        return query
