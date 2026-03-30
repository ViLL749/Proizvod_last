from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QLineEdit, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from db_manager import get_db_connection
from book_card import BookCard
from book_form import BookForm

class BookWindow(QWidget):
    def __init__(self, role, user_name="Гость", user_login=None):
        super().__init__()
        self.role = role
        self.user_name = user_name
        self.user_login = user_login  # логин

        self.setWindowTitle("Каталог книг")
        self.resize(1000,700)
        self.setWindowIcon(QIcon("resources/icon.png"))

        self.found_cards = []
        self.current_match_index = -1

        main_layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        logo = QLabel()
        logo_pix = QPixmap("photo/logo.png")
        logo.setPixmap(logo_pix.scaled(120,120,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        header_layout.addWidget(logo)

        # Жанры
        self.genre_filter = QComboBox()
        self.load_genres()
        self.genre_filter.currentIndexChanged.connect(self.load_books)
        self.genre_filter.currentTextChanged.connect(self.load_books)
        header_layout.addWidget(self.genre_filter)

        # Поиск и навигация
        if role in ["Librarian", "Admin"]:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по названию/автору")
            self.search_input.textChanged.connect(self.highlight_search)
            self.search_input.setMinimumWidth(250)
            header_layout.addWidget(self.search_input, stretch=2)

            # Навигация по найденным книгам
            nav_layout = QHBoxLayout()
            nav_layout.setSpacing(2)
            self.btn_prev = QPushButton("<")
            self.btn_next = QPushButton(">")
            self.btn_prev.setFixedSize(30,25)
            self.btn_next.setFixedSize(30,25)
            self.btn_prev.clicked.connect(lambda: self.navigate_search(-1))
            self.btn_next.clicked.connect(lambda: self.navigate_search(1))
            nav_layout.addWidget(self.btn_prev)
            nav_layout.addWidget(self.btn_next)
            header_layout.addLayout(nav_layout)

        header_layout.addStretch(1)

        # Информация о пользователе
        user_info = QLabel(f"<div align='right'>Пользователь: <b>{user_name}</b><br>Роль: <i>{role}</i></div>")
        user_info.setStyleSheet("font-size: 12px; color: #333;")
        header_layout.addWidget(user_info)

        # Кнопка добавления книги (только для Admin)
        if role=="Admin":
            btn_add = QPushButton("Добавить книгу")
            btn_add.setStyleSheet("""
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
            btn_add.clicked.connect(self.add_book)
            header_layout.addWidget(btn_add)

        # Кнопка "Мои книги" для авторизованных пользователей (не для гостей)
        if role == "Reader":
            btn_my_books = QPushButton("Мои книги")
            btn_my_books.setStyleSheet("""
                QPushButton {
                    background-color: #87CEFA;
                    color: black;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #00BFFF;
                }
            """)
            btn_my_books.clicked.connect(self.open_issued_books)
            header_layout.addWidget(btn_my_books)

        # Кнопка выхода
        btn_exit = QPushButton("Выйти")
        btn_exit.setFixedWidth(80)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                font-family: 'Times New Roman';
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f2f2f2;
            }
        """)
        btn_exit.clicked.connect(self.logout)
        header_layout.addWidget(btn_exit)

        main_layout.addLayout(header_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(15)
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        self.load_books()

    def load_genres(self):
        self.genre_filter.clear()
        self.genre_filter.addItem("Все жанры", None)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT GenreID, GenreName FROM Genres")
        for row in cur.fetchall():
            self.genre_filter.addItem(row[1], row[0])
        conn.close()

    def load_books(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            query = "SELECT BookID, Title, Author, GenreID, Publisher, Year, Quantity, Description, CoverImage FROM Books"
            params = []
            genre_id = self.genre_filter.currentData()
            if genre_id:
                query += " WHERE GenreID=?"
                params.append(genre_id)
            cur.execute(query, params)
            books = cur.fetchall()
            conn.close()
            for b in books:
                self.content_layout.addWidget(BookCard(b, self.role))
            if hasattr(self, "search_input"):
                self.highlight_search()
        except Exception as e:
            print("Ошибка загрузки:", e)

    def add_book(self):
        form = BookForm()
        if form.exec_():
            self.load_books()

    def open_issued_books(self):
        # В BookWindow
        self.issued_win = IssuedBooksWindow(self.user_login)
        self.issued_win.show()

    def highlight_search(self):
        text = self.search_input.text().lower().strip()
        self.found_cards = []
        self.current_match_index = -1  # сброс текущего индекса

        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if not item or not item.widget():
                continue
            card = item.widget()
            # Сбрасываем стиль к обычному
            card.setStyleSheet("BookCard { background:white; border:1px solid #dcdcdc; } * { outline:none; }")
            title = card.book_data[1]
            author = card.book_data[2]

            if not text:
                # Если поиск пустой, оставляем обычное отображение
                card.name_label.setText(f"<b>{title}</b>")
                continue

            # Если есть совпадение с названием или автором
            if text in title.lower() or text in author.lower():
                # Подсветка карточки
                card.setStyleSheet("BookCard { background:#ffffcc; border:2px solid orange; } * { outline:none; }")

                # Подсветка текста в названии
                start = title.lower().find(text) if text in title.lower() else -1
                if start != -1:
                    end = start + len(text)
                    highlighted_title = f"{title[:start]}<span style='background-color:#ff9d00;color:black;'>{title[start:end]}</span>{title[end:]}"
                    card.name_label.setText(f"<b>{highlighted_title}</b>")
                else:
                    card.name_label.setText(f"<b>{title}</b>")

                self.found_cards.append(card)
            else:
                card.name_label.setText(f"<b>{title}</b>")

    def navigate_search(self, step):
        if not self.found_cards: return

        # Сброс предыдущей подсветки
        if self.current_match_index != -1:
            prev_card = self.found_cards[self.current_match_index]
            prev_card.setStyleSheet("BookCard { background:#ffffcc; border:2px solid orange; } * { outline:none; }")

        # Вычисляем следующий индекс
        self.current_match_index += step
        if self.current_match_index >= len(self.found_cards): self.current_match_index = 0
        if self.current_match_index < 0: self.current_match_index = len(self.found_cards)-1

        # Выделяем текущую карточку красной рамкой
        target_card = self.found_cards[self.current_match_index]
        target_card.setStyleSheet("BookCard { background:#ffeb3b; border:3px solid red; } * { outline:none; }")
        self.scroll_area.ensureWidgetVisible(target_card)

    def logout(self):
        from auth_window import AuthWindow
        self.auth_win = AuthWindow()
        self.auth_win.show()
        self.close()




class IssuedBooksWindow(QWidget):
    def __init__(self, user_login):
        super().__init__()
        self.user_login = user_login
        self.setWindowTitle(f"Выданные книги пользователя {user_login}")
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        self.load_issued_books()

    def load_issued_books(self):
        # Очищаем предыдущие карточки
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Получаем UserID по логину
            cur.execute("SELECT UserID FROM Users WHERE Login = ?", (self.user_login,))
            row = cur.fetchone()
            if not row:
                conn.close()
                label = QLabel("Пользователь не найден.")
                label.setStyleSheet("font-size: 14pt; color: red;")
                self.content_layout.addWidget(label)
                return
            user_id = row[0]

            # Получаем все выданные книги пользователя
            # Берем только те записи, которые реально выданы (StatusID = 2 — 'Выдана')
            query = """
                SELECT b.BookID, b.Title, b.Author, g.GenreName, b.Publisher, b.Year, b.Quantity, b.Description, b.CoverImage
                FROM Borrowings br
                JOIN BorrowingItems bi ON br.BorrowingID = bi.BorrowingID
                JOIN Books b ON bi.BookID = b.BookID
                LEFT JOIN Genres g ON b.GenreID = g.GenreID
                WHERE br.UserID = ? AND br.StatusID = 2
            """
            cur.execute(query, (user_id,))
            books = cur.fetchall()
            conn.close()

            if not books:
                label = QLabel("У вас пока нет выданных книг.")
                label.setStyleSheet("font-size: 14pt; color: #555;")
                self.content_layout.addWidget(label)
                return

            for book in books:
                self.content_layout.addWidget(BookCard(book, role="User"))

        except Exception as e:
            print("Ошибка загрузки выданных книг:", e)