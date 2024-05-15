from PyQt6 import QtSql


class Data:
    def __init__(self):
        super(Data, self).__init__()
        self.createConnection()

    def createConnection(self):
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("expensetracker.db")
        db.open()
        query = QtSql.QSqlQuery()
        if not query.exec("CREATE TABLE IF NOT EXISTS expenses ("
                          "id integer PRIMARY KEY AUTOINCREMENT NOT NULL,"
                          "description VARCHAR(32) NOT NULL,"
                          "value REAL NOT NULL,"
                          "category VARCHAR(32) NOT NULL,"
                          "date DATE NOT NULL)"):
            print(query.lastError().text())

    def executeQuery(self, query_text, query_values=None):
        query = QtSql.QSqlQuery()
        query.prepare(query_text)
        if query_values:
            for value in query_values:
                query.addBindValue(value)

        if not query.exec():
            print(query.lastError().text())
        return query

    def insertEntry(self, description, value, category, date):
        query_text = "INSERT INTO expenses (description, value, category, date) VALUES (?, ?, ?, ?)"
        self.executeQuery(query_text, [description, value, category, date])

    def updateEntry(self, description, value, category, date, entry_id):
        query_text = "UPDATE expenses SET description=?, value=?, category=?, date=? WHERE id=?"
        self.executeQuery(query_text, [description, value, category, date, entry_id])

    def deleteEntry(self, entry_id):
        query_text = "DELETE FROM expenses WHERE id=?"
        self.executeQuery(query_text, [entry_id])

    def getBalance(self):
        income_value, outcome_value = 0, 0
        query_text = "SELECT SUM(value) FROM expenses WHERE category='Поступления'"
        query = self.executeQuery(query_text)
        if query.next():
            income_value = query.value(0) or 0

        query_text = "SELECT SUM(value) FROM expenses WHERE category<>'Поступления'"
        query = self.executeQuery(query_text)
        if query.next():
            outcome_value = query.value(0) or 0

        return str(income_value - outcome_value)

    def getTableWithFilters(self, date_cb, category_cb, date, category):
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
