from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db_manager import get_db_connection
from select_reader_window import SelectReaderWindow  # импортируем окно выбора читателя

class IssueBookWindow(QDialog):
    def __init__(self, book_id, borrowing_id=None):
        super().__init__()
        self.setWindowTitle("Выдача книги")
        self.resize(350,220)
        self.book_id = book_id
        self.borrowing_id = borrowing_id  # если редактируем существующую запись

        layout = QVBoxLayout(self)

        # Читатель
        self.reader_display = QLineEdit()
        # self.reader_display.setReadOnly(True)
        layout.addWidget(QLabel("Читатель:"))

        btn_select_reader = QPushButton("Выбрать читателя")
        btn_select_reader.clicked.connect(self.select_reader)
        reader_layout = QHBoxLayout()
        reader_layout.addWidget(self.reader_display)
        reader_layout.addWidget(btn_select_reader)
        layout.addLayout(reader_layout)

        # Дата выдачи
        self.borrow_date_edit = QDateEdit()
        self.borrow_date_edit.setCalendarPopup(True)
        self.borrow_date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Дата выдачи:"))
        layout.addWidget(self.borrow_date_edit)

        # Дата возврата
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(14))
        layout.addWidget(QLabel("Дата возврата:"))
        layout.addWidget(self.due_date_edit)

        # Кнопка подтверждения
        btn_ok = QPushButton("Сохранить")
        btn_ok.clicked.connect(self.save)
        layout.addWidget(btn_ok)

        # Если редактируем существующую запись
        if borrowing_id:
            self.load_existing()

    def select_reader(self):
        dlg = SelectReaderWindow()
        if dlg.exec_():
            login = dlg.get_selected_login()
            if login:
                self.reader_display.setText(login)

    def load_existing(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT UserID, BorrowDate, DueDate FROM Borrowings WHERE BorrowingID=?", (self.borrowing_id,))
        row = cur.fetchone()
        if row:
            user_id, borrow_date, due_date = row
            self.borrow_date_edit.setDate(QDate.fromString(borrow_date, "yyyy-MM-dd"))
            self.due_date_edit.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))

            cur.execute("SELECT Login FROM Users WHERE UserID=?", (user_id,))
            login = cur.fetchone()[0]
            self.reader_display.setText(login)
        conn.close()
        # При редактировании нельзя менять читателя
        self.reader_display.setDisabled(True)

    def save(self):
        login = self.reader_display.text().strip()
        borrow_date = self.borrow_date_edit.date().toString("yyyy-MM-dd")
        due_date = self.due_date_edit.date().toString("yyyy-MM-dd")

        if not login:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if self.borrowing_id:
                # редактируем только даты
                cur.execute(
                    "UPDATE Borrowings SET BorrowDate=?, DueDate=? WHERE BorrowingID=?",
                    (borrow_date, due_date, self.borrowing_id)
                )
            else:
                # новая выдача
                cur.execute("SELECT UserID FROM Users WHERE Login=?", (login,))
                row = cur.fetchone()
                if not row:
                    QMessageBox.warning(self, "Ошибка", "Читатель не найден")
                    return
                user_id = row[0]

                cur.execute(
                    "INSERT INTO Borrowings (UserID, BorrowDate, DueDate, StatusID) VALUES (?, ?, ?, ?)",
                    (user_id, borrow_date, due_date, 2)
                )
                borrowing_id = cur.lastrowid
                cur.execute(
                    "INSERT INTO BorrowingItems (BorrowingID, BookID, Quantity) VALUES (?, ?, ?)",
                    (borrowing_id, self.book_id, 1)
                )

            conn.commit()
            conn.close()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))