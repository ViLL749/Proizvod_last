from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from db_manager import get_db_connection


class BorrowingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление выдачами книг")
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)


        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)

        self.scroll_area.setWidget(self.content)
        main_layout.addWidget(self.scroll_area)

        self.load_borrowings()

    def load_borrowings(self):
        # Очищаем
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT br.BorrowingID, u.FIO, b.Title, br.BorrowDate, br.DueDate, br.ReturnDate, br.StatusID
        FROM Borrowings br
        JOIN Users u ON br.UserID = u.UserID
        JOIN BorrowingItems bi ON br.BorrowingID = bi.BorrowingID
        JOIN Books b ON bi.BookID = b.BookID
        ORDER BY br.BorrowDate DESC;
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            card = self.create_card(row)
            self.content_layout.addWidget(card)

    def create_card(self, row):
        borrowing_id, fio, title, borrow_date, due_date, return_date, status_id = row

        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("background:#fafafa; padding:10px;")
        layout = QVBoxLayout(frame)

        # Информация о книге и читателе
        today = QDate.currentDate()
        due_q = QDate.fromString(due_date, "yyyy-MM-dd")

        if return_date:
            status_text = f"Возвращена {return_date}"
            color = "green"
        elif today > due_q:
            status_text = f"Просрочена! Должна быть возвращена {due_date}"
            color = "red"
        else:
            status_text = f"Вернуть до {due_date}"
            color = "orange"

        label = QLabel(f"""
        <b>Читатель:</b> {fio}<br>
        <b>Книга:</b> {title}<br><br>
        <b>Дата выдачи:</b> {borrow_date}<br>
        <span style="color:{color}"><b>{status_text}</b></span>
        """)
        label.setWordWrap(True)
        layout.addWidget(label)

        # --------------------
        # Кнопки
        # --------------------
        btns = QHBoxLayout()

        btn_edit = QPushButton("Изменить")
        btn_edit.clicked.connect(lambda: self.edit_borrowing(borrowing_id))
        btn_edit.setStyleSheet("background:#00bfff; color:white; padding:6px;")

        btn_return = QPushButton("Отметить возврат")
        btn_return.clicked.connect(lambda: self.return_book(borrowing_id))
        btn_return.setStyleSheet("background:#5bc0de; color:white; padding:6px;")

        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(lambda: self.delete_borrowing(borrowing_id))
        btn_delete.setStyleSheet("background:#d9534f; color:white; padding:6px;")

        # Теперь проверяем статус и блокируем кнопку возврата если книга уже возвращена
        if return_date or status_id == 4:
            btn_return.setEnabled(False)
            btn_edit.setEnabled(False)
        else:
            btn_return.setEnabled(True)
            btn_edit.setEnabled(True)

        btns.addWidget(btn_edit)
        btns.addWidget(btn_return)
        btns.addWidget(btn_delete)

        layout.addLayout(btns)
        return frame

    def create_borrowing(self):
        from borrowing_form import BorrowingForm  # создадим ниже
        form = BorrowingForm()
        if form.exec_():
            self.load_borrowings()

    def edit_borrowing(self, borrowing_id):
        from borrowing_form import BorrowingForm
        form = BorrowingForm(borrowing_id)
        if form.exec_():
            # После редактирования перезагружаем весь список
            self.load_borrowings()

    def return_book(self, borrowing_id):
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Borrowings
            SET ReturnDate = DATE('now'), StatusID = 4
            WHERE BorrowingID = ?
        """, (borrowing_id,))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Успех", "Книга отмечена как возвращённая.")
        self.load_borrowings()

    def delete_borrowing(self, borrowing_id):
        reply = QMessageBox.question(self, "Удаление", "Удалить запись выдачи?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM BorrowingItems WHERE BorrowingID = ?", (borrowing_id,))
            cur.execute("DELETE FROM Borrowings WHERE BorrowingID = ?", (borrowing_id,))

            conn.commit()
            conn.close()

            self.load_borrowings()