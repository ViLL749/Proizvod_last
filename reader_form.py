from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from db_manager import get_db_connection

class ReaderForm(QDialog):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("Читатель")
        self.resize(300,200)
        self.user_id = user_id  # None = новый читатель

        layout = QVBoxLayout(self)

        # ФИО
        self.fio_input = QLineEdit()
        layout.addWidget(QLabel("ФИО:"))
        layout.addWidget(self.fio_input)

        # Логин
        self.login_input = QLineEdit()
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)

        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)

        # Кнопка сохранить
        btn_ok = QPushButton("Сохранить")
        btn_ok.setStyleSheet("background:#28a745; color:white; padding:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.save)
        layout.addWidget(btn_ok)

        if user_id:
            self.load_existing()

    def load_existing(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT FIO, Login FROM Users WHERE UserID=?", (self.user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            fio, login = row
            self.fio_input.setText(fio)
            self.login_input.setText(login)

    def save(self):
        fio = self.fio_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not fio or not login:
            QMessageBox.warning(self, "Ошибка", "ФИО и логин обязательны")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if self.user_id:
                # редактирование
                if password:
                    cur.execute("UPDATE Users SET FIO=?, Login=?, Password=? WHERE UserID=?",
                                (fio, login, password, self.user_id))
                else:
                    cur.execute("UPDATE Users SET FIO=?, Login=? WHERE UserID=?",
                                (fio, login, self.user_id))
            else:
                # добавление нового читателя
                cur.execute("SELECT RoleID FROM Roles WHERE RoleName='Reader'")
                role_id = cur.fetchone()[0]
                cur.execute("INSERT INTO Users (FIO, Login, Password, RoleID) VALUES (?, ?, ?, ?)",
                            (fio, login, password, role_id))

            conn.commit()
            conn.close()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))