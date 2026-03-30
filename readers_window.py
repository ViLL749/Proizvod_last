from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton,
    QHBoxLayout, QMessageBox
)
from db_manager import get_db_connection
from PyQt5.QtCore import Qt
from reader_form import ReaderForm  # создадим ниже

class ReadersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление читателями")
        self.resize(700, 600)

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)

        self.scroll_area.setWidget(self.content)
        main_layout.addWidget(self.scroll_area)

        # Кнопка добавления читателя
        btn_add = QPushButton("Добавить читателя")
        btn_add.setStyleSheet("background:#28a745; color:white; padding:6px; font-weight:bold;")
        btn_add.clicked.connect(self.create_reader)
        main_layout.addWidget(btn_add)

        self.load_readers()

    def load_readers(self):
        # Очистка старых карточек
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        conn = get_db_connection()
        cur = conn.cursor()
        # Только роль "Читатель"
        cur.execute("""
            SELECT UserID, FIO, Login FROM Users
            WHERE RoleID=(SELECT RoleID FROM Roles WHERE RoleName='Reader')
            ORDER BY FIO
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            card = self.create_card(row)
            self.content_layout.addWidget(card)

    def create_card(self, row):
        user_id, fio, login = row

        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("background:#fafafa; padding:10px;")
        layout = QVBoxLayout(frame)

        label = QLabel(f"<b>ФИО:</b> {fio}<br><b>Логин:</b> {login}")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Кнопки действий
        btns = QHBoxLayout()

        btn_edit = QPushButton("Редактировать")
        btn_edit.setStyleSheet("background:#00bfff; color:white; padding:6px;")
        btn_edit.clicked.connect(lambda: self.edit_reader(user_id))

        btn_delete = QPushButton("Удалить")
        btn_delete.setStyleSheet("background:#d9534f; color:white; padding:6px;")
        btn_delete.clicked.connect(lambda: self.delete_reader(user_id))

        btns.addWidget(btn_edit)
        btns.addWidget(btn_delete)
        layout.addLayout(btns)

        return frame

    def create_reader(self):
        form = ReaderForm()
        if form.exec_():
            self.load_readers()

    def edit_reader(self, user_id):
        form = ReaderForm(user_id)
        if form.exec_():
            self.load_readers()

    def delete_reader(self, user_id):
        reply = QMessageBox.question(self, "Удаление", "Удалить этого читателя?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM Users WHERE UserID=?", (user_id,))
                conn.commit()
                conn.close()
                self.load_readers()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))