from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from db_manager import get_db_connection

class PublisherForm(QDialog):
    def __init__(self, publisher_id=None):
        super().__init__()
        self.setWindowTitle("Издательство")
        self.resize(300, 150)
        self.publisher_id = publisher_id

        layout = QVBoxLayout(self)

        # Название издательства
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Название издательства:"))
        layout.addWidget(self.name_input)

        # Кнопка сохранить
        btn_ok = QPushButton("Сохранить")
        btn_ok.setStyleSheet("background:#28a745; color:white; padding:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.save)
        layout.addWidget(btn_ok)

        if publisher_id:
            self.load_existing()

    def load_existing(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT PublisherName FROM Publishers WHERE PublisherID=?", (self.publisher_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.name_input.setText(row[0])

    def save(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if self.publisher_id:
                # Редактирование
                cur.execute("UPDATE Publishers SET PublisherName=? WHERE PublisherID=?", (name, self.publisher_id))
            else:
                # Добавление нового
                cur.execute("INSERT INTO Publishers (PublisherName) VALUES (?)", (name,))

            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Возможно, такое издательство уже существует")