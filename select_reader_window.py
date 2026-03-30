from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QPushButton
from db_manager import get_db_connection

class SelectReaderWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выберите читателя")
        self.resize(300,400)

        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по логину или ФИО")
        self.search_input.textChanged.connect(self.load_users)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_ok = QPushButton("Выбрать")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

        self.load_users()

    def load_users(self):
        text = self.search_input.text().lower()
        self.list_widget.clear()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT Login, FIO FROM Users WHERE RoleID=1")
        for login, fio in cur.fetchall():
            display = f"{fio} ({login})"
            if text in login.lower() or text in fio.lower():
                self.list_widget.addItem(display)
        conn.close()

    def get_selected_login(self):
        item = self.list_widget.currentItem()
        if item:
            # Извлекаем логин из "(логин)" в конце строки
            return item.text().split("(")[-1].replace(")","")
        return None