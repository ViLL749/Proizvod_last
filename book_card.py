from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db_manager import get_db_connection
from book_form import BookForm

class BookCard(QFrame):
    def __init__(self, book_data, role):
        super().__init__()
        self.book_data = book_data
        self.role = role
        self.book_id = book_data[0]

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            BookCard { background-color: #FFFFFF; border: 1px solid #dcdcdc; border-radius:5px; font-family: 'Times New Roman'; font-size:12pt;}
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10,10,10,10)

        # Фото
        photo_label = QLabel()
        photo_label.setFixedSize(120,160)
        pixmap = QPixmap(f"photo/{book_data[8]}")
        if pixmap.isNull():
            photo_label.setText("Фото отсутствует")
            photo_label.setAlignment(Qt.AlignCenter)
        else:
            photo_label.setPixmap(pixmap.scaled(120,160,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        main_layout.addWidget(photo_label)

        # Информация
        center_layout = QVBoxLayout()
        self.name_label = QLabel(f"<b>{book_data[1]}</b>")
        center_layout.addWidget(self.name_label)
        center_layout.addWidget(QLabel(f"Автор: {book_data[2]}"))
        center_layout.addWidget(QLabel(f"Жанр: {book_data[3]}"))
        center_layout.addWidget(QLabel(f"Издательство: {book_data[4]}"))
        center_layout.addWidget(QLabel(f"Год: {book_data[5]}"))
        center_layout.addWidget(QLabel(f"Количество: {book_data[6]}"))
        center_layout.addWidget(QLabel(f"{book_data[7]}"))
        main_layout.addLayout(center_layout, stretch=1)

        # Действия
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        if role == "Librarian":
            btn_issue = QPushButton("Выдать")
            btn_issue.setStyleSheet("""
                QPushButton {
                    background-color: #32CD32;
                    color: white;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #28a428;
                }
            """)
            btn_issue.setFixedWidth(100)
            btn_issue.clicked.connect(self.issue_book)
            right_layout.addWidget(btn_issue, alignment=Qt.AlignTop)

        if role == "Admin":
            right_layout.addSpacing(10)

            # Кнопка редактировать
            self.btn_edit = QPushButton("Редактировать")
            self.btn_edit.setStyleSheet("""
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
            self.btn_edit.clicked.connect(self.edit_book)

            # Кнопка удалить
            self.btn_delete = QPushButton("Удалить")
            self.btn_delete.setStyleSheet("""
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
            self.btn_delete.clicked.connect(self.delete_book)

            right_layout.addWidget(self.btn_edit)
            right_layout.addWidget(self.btn_delete)

        main_layout.addLayout(right_layout)

    def issue_book(self):
        from issue_book_window import IssueBookWindow
        dlg = IssueBookWindow(self.book_data[0])
        if dlg.exec_():
            parent_window = self.window()
            if hasattr(parent_window, "load_books"):
                parent_window.load_books()

    def delete_book(self):
        reply = QMessageBox.question(
            self, "Удаление", f"Удалить книгу {self.book_data[1]}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # 1. Получаем все BorrowingItems с этой книгой
            cur.execute("SELECT BorrowingID, Quantity FROM BorrowingItems WHERE BookID=?", (self.book_id,))
            items = cur.fetchall()

            for borrowing_id, qty in items:
                # 2. Возвращаем книги на склад (увеличиваем Quantity)
                cur.execute("UPDATE Books SET Quantity = Quantity + ? WHERE BookID=?", (qty, self.book_id))

                # 3. Удаляем запись из BorrowingItems
                cur.execute("DELETE FROM BorrowingItems WHERE BorrowingID=? AND BookID=?", (borrowing_id, self.book_id))

                # 4. Проверяем, остались ли книги в BorrowingItems для этого BorrowingID
                cur.execute("SELECT COUNT(*) FROM BorrowingItems WHERE BorrowingID=?", (borrowing_id,))
                count = cur.fetchone()[0]
                if count == 0:
                    # если нет, удаляем сам Borrowings
                    cur.execute("DELETE FROM Borrowings WHERE BorrowingID=?", (borrowing_id,))

            # 5. Удаляем книгу из Books
            cur.execute("DELETE FROM Books WHERE BookID=?", (self.book_id,))

            conn.commit()
            conn.close()

            # Скрываем карточку
            self.hide()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def edit_book(self):
        form = BookForm(self.book_data)
        if form.exec_():
            parent_window = self.window()
            if hasattr(parent_window, "load_books"):
                parent_window.load_books()