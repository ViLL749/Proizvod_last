from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db_manager import get_db_connection

class BorrowingForm(QDialog):
    def __init__(self, borrowing_id):
        super().__init__()
        self.setWindowTitle("Редактирование выдачи")
        self.resize(300,150)
        self.borrowing_id = borrowing_id

        layout = QVBoxLayout(self)

        # Дата возврата
        layout.addWidget(QLabel("Дата возврата:"))
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        layout.addWidget(self.due_date_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.load_existing()

    def load_existing(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DueDate FROM Borrowings WHERE BorrowingID=?", (self.borrowing_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            due_date = row[0]
            self.due_date_edit.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))

    def save(self):
        due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE Borrowings SET DueDate=? WHERE BorrowingID=?", (due_date, self.borrowing_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Дата возврата обновлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))