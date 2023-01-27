import sys
import mysql.connector as con
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.uic import loadUi
from passlib.hash import pbkdf2_sha256
from re import fullmatch
from configparser import ConfigParser
from os.path import isfile


class LoginApp(QDialog):
    def __init__(self):
        super(LoginApp, self).__init__()
        loadUi("login-form.ui", self)
        if isfile('MyApp_config.ini'):
            pass
        else:
            config = ConfigParser()
            config["mysql_database"] = {
                "host": "",
                "user": "",
                "password": "",
                "db": ""
            }
            with open('MyApp_config.ini', 'w') as conf:
                config.write(conf)
            QMessageBox.information(self, "MyApp", "Fill in the config file!")
        self.b1.clicked.connect(self.login)
        self.b2.clicked.connect(self.show_reg)

    def login(self):
        un = self.tb1.text()
        pw = self.tb2.text()

        if len(un) < 6:
            QMessageBox.information(self, "MyApp", "The minimum Username length is 6 characters!")
        elif len(un) > 30:
            QMessageBox.information(self, "MyApp", "The maximum Username length is 30 characters!")
        elif len(pw) < 6:
            QMessageBox.information(self, "MyApp", "The minimum Password length is 6 characters!")
        elif len(pw) > 100:
            QMessageBox.information(self, "MyApp", "The maximum Password length is 100 characters!")
        else:
            config = ConfigParser()
            config.read("MyApp_config.ini")
            database = config["mysql_database"]
            db_host = database["host"]
            db_user = database["user"]
            db_password = database["password"]
            db_db = database["db"]
            try:
                db = con.connect(host=f"{db_host}", user=f"{db_user}", password=f"{db_password}", db=f"{db_db}")
                cur = db.cursor()
                cur.execute("select password from users where username='" + un + "'")
                result_pw = cur.fetchone()
                try:
                    if pbkdf2_sha256.verify(pw, str(result_pw[0])):
                        QMessageBox.information(self, "MyApp", "You have successfully logged in!")
                        self.tb1.setText("")
                        self.tb2.setText("")
                        w.setCurrentIndex(2)
                except:
                    QMessageBox.information(self, "MyApp", "Couldn't find an account")
            except:
                QMessageBox.information(self, "MyApp",
                                        "There is no connection to the database, fill in the config file!")

    def show_reg(self):
        w.setCurrentIndex(1)


class RegApp(QDialog):
    def __init__(self):
        super(RegApp, self).__init__()
        loadUi("register-form.ui", self)
        if isfile('MyApp_config.ini'):
            pass
        else:
            config = ConfigParser()
            config["mysql_database"] = {
                "host": "",
                "user": "",
                "password": "",
                "db": ""
            }
            with open('MyApp_config.ini', 'w') as conf:
                config.write(conf)
            QMessageBox.information(self, "MyApp", "Fill in the config file!")
        self.b3.clicked.connect(self.reg)
        self.b4.clicked.connect(self.show_login)

    def reg(self):
        un = self.tb3.text()
        pw = self.tb4.text()
        em = self.tb5.text()

        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if len(un) < 6:
            QMessageBox.information(self, "MyApp", "The minimum Username length is 6 characters!")
        elif len(un) > 30:
            QMessageBox.information(self, "MyApp", "The maximum Username length is 30 characters!")
        elif len(pw) < 6:
            QMessageBox.information(self, "MyApp", "The minimum Password length is 6 characters!")
        elif len(pw) > 100:
            QMessageBox.information(self, "MyApp", "The maximum Password length is 100 characters!")
        elif not fullmatch(regex, em):
            QMessageBox.information(self, "MyApp", "Invalid Email!")
        elif len(em.split("@")[0]) < 5:
            QMessageBox.information(self, "MyApp", "The minimum Email length is 5 characters!")
        elif len(em.split("@")[0]) > 100:
            QMessageBox.information(self, "MyApp", "The maximum Email length is 100 characters!")
        else:
            config = ConfigParser()
            config.read("MyApp_config.ini")
            database = config["mysql_database"]
            db_host = database["host"]
            db_user = database["user"]
            db_password = database["password"]
            db_db = database["db"]
            try:
                db = con.connect(host=f"{db_host}", user=f"{db_user}", password=f"{db_password}", db=f"{db_db}")
                cur = db.cursor()
                cur.execute("select username from users where username='" + un + "'")
                result_un = cur.fetchone()
                if result_un:
                    QMessageBox.information(self, "MyApp", "The user is already registered")
                else:
                    cur.execute("insert into users values('" + un + "', '" +
                                pbkdf2_sha256.hash(pw) + "', '" + em + "')")
                    db.commit()
                    QMessageBox.information(self, "MyApp", "The user has been successfully registered!")
                    self.tb3.setText("")
                    self.tb4.setText("")
                    self.tb5.setText("")
                    w.setCurrentIndex(0)
            except:
                QMessageBox.information(self, "MyApp",
                                        "There is no connection to the database, fill in the config file!")

    def show_login(self):
        w.setCurrentIndex(0)

class SelectApp(QDialog):
    def __init__(self):
        super(SelectApp, self).__init__()
        loadUi("select-form.ui", self)
        self.b5.clicked.connect(self.select_data)

    def select_data(self):
        db_name = self.tb6.text()
        table_name = self.tb7.text()

        config = ConfigParser()
        config.read("MyApp_config.ini")
        database = config["mysql_database"]
        db_host = database["host"]
        db_user = database["user"]
        db_password = database["password"]
        try:
            db = con.connect(host=f"{db_host}", user=f"{db_user}", password=f"{db_password}", db=f"{db_name}")
            cur = db.cursor()
            cur.execute("select * from {}".format(table_name))
            result = cur.fetchall()
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        except:
            QMessageBox.information(self, "MyApp", "Invalid DB or Table name!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QtWidgets.QStackedWidget()
    w.setWindowTitle("MyApp")
    loginform = LoginApp()
    registrationform = RegApp()
    selectform = SelectApp()
    w.addWidget(loginform)
    w.addWidget(registrationform)
    w.addWidget(selectform)
    w.setCurrentIndex(0)
    w.setFixedWidth(400)
    w.setFixedHeight(500)
    w.show()
    sys.exit(app.exec_())
