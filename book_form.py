
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QSpinBox, QPushButton, QComboBox, QMessageBox, QHBoxLayout
from db_manager import get_db_connection

class BookForm(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        self.book_data = book_data
        self.old_data = book_data
        self.setWindowTitle("Добавление книги" if not book_data else "Редактирование книги")
        self.resize(400, 500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.genre_combo = QComboBox()
        self.publisher_combo = QComboBox()
        self.year_input = QSpinBox()
        self.year_input.setMaximum(2100)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(1000)
        self.description_input = QTextEdit()
        self.cover_input = QLineEdit()

        form.addRow("Название", self.title_input)
        form.addRow("Автор", self.author_input)
        form.addRow("Жанр", self.genre_combo)
        form.addRow("Издательство", self.publisher_combo)
        form.addRow("Год", self.year_input)
        form.addRow("Количество", self.quantity_input)
        form.addRow("Описание", self.description_input)
        form.addRow("Фото (имя файла)", self.cover_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_save.clicked.connect(self.save_book)
        self.btn_cancel.clicked.connect(self.close)

        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00FA9A;
                color: black;
                font-family: 'Times New Roman';
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00e68a;
            }
        """)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                color: white;
                font-family: 'Times New Roman';
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)

        self.load_genres()
        self.load_publishers()

        if book_data:
            self.load_data()

    def load_genres(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT GenreID, GenreName FROM Genres")
        for row in cur.fetchall():
            self.genre_combo.addItem(row[1], row[0])
        conn.close()

    def load_publishers(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT PublisherID, PublisherName FROM Publishers")
        for row in cur.fetchall():
            self.publisher_combo.addItem(row[1], row[0])
        conn.close()

    def load_data(self):
        b = self.book_data
        self.title_input.setText(b[1])
        self.author_input.setText(b[2])
        self.set_combo_value(self.genre_combo, b[3])

        index = self.publisher_combo.findText(str(b[4]))
        if index >= 0:
            self.publisher_combo.setCurrentIndex(index)

        self.year_input.setValue(b[5])
        self.quantity_input.setValue(b[6])
        self.description_input.setText(b[7] or "")
        self.cover_input.setText(b[8] or "")

    def set_combo_value(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def save_book(self):
        data = (
            self.title_input.text(),
            self.author_input.text(),
            self.genre_combo.currentData(),  # ID жанра
            self.publisher_combo.currentData(),  # ID издательства
            self.year_input.value(),
            self.quantity_input.value(),
            self.description_input.toPlainText(),
            self.cover_input.text()
        )
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            if self.old_data:
                # ЗАМЕНЕНО: Publisher -> PublisherID
                cur.execute("""
                    UPDATE Books SET 
                    Title=?, Author=?, GenreID=?, PublisherID=?, Year=?, 
                    Quantity=?, Description=?, CoverImage=?
                    WHERE BookID=?
                """, data + (self.old_data[0],))
            else:
                # ЗАМЕНЕНО: Publisher -> PublisherID
                cur.execute("""
                    INSERT INTO Books (Title, Author, GenreID, PublisherID, Year, Quantity, Description, CoverImage)
                    VALUES (?,?,?,?,?,?,?,?)
                """, data)
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Книга сохранена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))