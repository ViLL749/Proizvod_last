from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from db_manager import get_db_connection
from publisher_form import PublisherForm


class PublishersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление издательствами")
        self.resize(600, 500)

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.content)
        main_layout.addWidget(self.scroll_area)

        # Кнопка добавления
        btn_add = QPushButton("Добавить издательство")
        btn_add.setStyleSheet("background:#00FA9A; color:black; padding:8px; font-weight:bold; border-radius:4px;")
        btn_add.clicked.connect(self.add_publisher)
        main_layout.addWidget(btn_add)

        self.load_publishers()

    def load_publishers(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT PublisherID, PublisherName FROM Publishers ORDER BY PublisherName")
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.content_layout.addWidget(self.create_card(row))

    def create_card(self, row):
        pub_id, name = row
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background:white; border: 1px solid #ddd; border-radius: 5px;")
        layout = QHBoxLayout(frame)

        label = QLabel(f"<b>{name}</b>")
        layout.addWidget(label)

        btns = QHBoxLayout()
        btn_edit = QPushButton("Правка")
        btn_edit.setStyleSheet("background:#00bfff; color:white; padding:4px;")
        btn_edit.clicked.connect(lambda: self.edit_publisher(pub_id))

        btn_delete = QPushButton("Удалить")
        btn_delete.setStyleSheet("background:#d9534f; color:white; padding:4px;")
        btn_delete.clicked.connect(lambda: self.delete_publisher(pub_id))

        btns.addWidget(btn_edit)
        btns.addWidget(btn_delete)
        layout.addLayout(btns)
        return frame

    def add_publisher(self):
        if PublisherForm().exec_():
            self.load_publishers()

    def edit_publisher(self, pub_id):
        if PublisherForm(pub_id).exec_():
            self.load_publishers()

    def delete_publisher(self, pub_id):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # ПРОВЕРКА: есть ли книги у этого издателя
            cur.execute("SELECT COUNT(*) FROM Books WHERE PublisherID=?", (pub_id,))
            count = cur.fetchone()[0]

            if count > 0:
                QMessageBox.warning(self, "Запрещено",
                                    f"Нельзя удалить издателя. В библиотеке числится книг этого издательства: {count} шт.")
                conn.close()
                return

            reply = QMessageBox.question(self, "Удаление", "Удалить это издательство?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                cur.execute("DELETE FROM Publishers WHERE PublisherID=?", (pub_id,))
                conn.commit()

            conn.close()
            self.load_publishers()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))