-- ===========================
-- 1. Таблица ролей
-- ===========================
CREATE TABLE Roles (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleName TEXT NOT NULL UNIQUE
);

-- ===========================
-- 2. Пользователи (читатели, библиотекари, администраторы)
-- ===========================
CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    FIO TEXT NOT NULL,
    Login TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    RoleID INTEGER NOT NULL,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
);

-- ===========================
-- 3. Жанры книг
-- ===========================
CREATE TABLE Genres (
    GenreID INTEGER PRIMARY KEY AUTOINCREMENT,
    GenreName TEXT NOT NULL UNIQUE
);

-- ===========================
-- 4. Книги
-- ===========================
CREATE TABLE Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    GenreID INTEGER,
    Publisher TEXT,
    Year INTEGER,
    Quantity INTEGER NOT NULL,
    Description TEXT,
    CoverImage TEXT,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID)
);

-- ===========================
-- 5. Статусы выдачи
-- ===========================
CREATE TABLE Statuses (
    StatusID INTEGER PRIMARY KEY AUTOINCREMENT,
    StatusName TEXT NOT NULL UNIQUE
);

-- ===========================
-- 6. Выдачи книг
-- ===========================

CREATE TABLE Borrowings (
    BorrowingID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    BorrowDate TEXT NOT NULL,      -- когда взял
    DueDate TEXT NOT NULL,         -- до какого должен вернуть
    ReturnDate TEXT,               -- когда вернул (NULL = ещё не вернул)
    StatusID INTEGER NOT NULL,     -- 1-обработке, 2-выдана, 3-просрочена, 4-возвращена
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (StatusID) REFERENCES Statuses(StatusID)
);

-- ===========================
-- 7. Состав выдачи (какие книги были выданы)
-- ===========================
CREATE TABLE BorrowingItems (
    BorrowingItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    BorrowingID INTEGER NOT NULL,
    BookID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    FOREIGN KEY (BorrowingID) REFERENCES Borrowings(BorrowingID),
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);

-- ======================================
-- 1. Роли
-- ======================================
INSERT INTO Roles (RoleName) VALUES
('Reader'),       -- Читатель
('Librarian'),    -- Библиотекарь
('Admin');        -- Администратор


-- ======================================
-- 2. Пользователи
-- Пароли — просто строки для теста
-- ======================================
INSERT INTO Users (FIO, Login, Password, RoleID) VALUES
('Иванов Иван Иванович', 'reader1', '12345', 1),
('Петрова Анна Сергеевна', 'reader2', '12345', 1),
('Сидоров Павел Викторович', 'librarian1', 'qwerty', 2),
('Админов Михаил Петрович', 'admin', 'admin', 3);


-- ======================================
-- 3. Жанры
-- ======================================
INSERT INTO Genres (GenreName) VALUES
('Фантастика'),
('Детектив'),
('Роман'),
('История'),
('Приключения'),
('Научная литература');


-- ======================================
-- 4. Книги
-- Quantity — условное количество экземпляров
-- ======================================
INSERT INTO Books (Title, Author, GenreID, Publisher, Year, Quantity, Description, CoverImage) VALUES
('Дюна', 'Фрэнк Герберт', 1, 'АСТ', 2020, 5, 'Эпическая научно-фантастическая сага.', 'dune.jpg'),
('1984', 'Джордж Оруэлл', 1, 'Эксмо', 2019, 4, 'Антиутопический роман о тоталитаризме.', '1984.jpg'),
('Шерлок Холмс: Собака Баскервилей', 'Артур Конан Дойл', 2, 'АСТ', 2018, 3, 'Классический детектив.', 'baskerville.jpg'),
('Анна Каренина', 'Лев Толстой', 3, 'Азбука', 2021, 6, 'Знаменитый роман русской литературы.', 'karennina.jpg'),
('Сапиенс. Краткая история человечества', 'Юваль Ной Харари', 6, 'МИФ', 2022, 5, 'Популярная научная литература.', 'sapiens.jpg'),
('Путешествие к центру Земли', 'Жюль Верн', 5, 'АСТ', 2017, 4, 'Приключенческая фантастика.', 'journey_center_earth.jpg'),
('Три мушкетёра', 'Александр Дюма', 5, 'Азбука', 2020, 7, 'Историко-приключенческий роман.', 'musketeers.jpg');


-- ======================================
-- 5. Статусы
-- ======================================
INSERT INTO Statuses (StatusName) VALUES
('Оформлена'),
('Выдана'),
('Возвращена'),
('Просрочена');


-- ======================================
-- 6. Выдачи книг (Borrowings)
-- ======================================
INSERT INTO Borrowings (UserID, BorrowDate, DueDate, ReturnDate, StatusID) VALUES
-- 1. Пользователь 1 вернул книгу вовремя
(1, '2024-03-01', '2024-03-15', '2024-03-14', 4),

-- 2. Пользователь 2 взял книгу, она сейчас "на руках" (выдана)
(2, '2024-03-20', '2024-04-03', NULL, 2),

-- 3. Пользователь 1 подал заявку, она еще "в обработке"
(1, '2026-03-28', '2026-04-11', NULL, 1),

-- 4. Просроченная выдача (дата возврата DueDate уже прошла, ReturnDate пуст)
(2, '2024-02-01', '2024-02-15', NULL, 3),

-- 5. Пользователь 2 вернул книгу, но с опозданием
(2, '2024-01-10', '2024-01-24', '2024-01-30', 4);


-- ======================================
-- 7. Состав выдачи (BorrowingItems)
-- BorrowingID = 1,2,3
-- BookID — по порядку вставки
-- ======================================
INSERT INTO BorrowingItems (BorrowingID, BookID, Quantity) VALUES
-- Выдача #1 (читатель #1)
(1, 1, 1),   -- Дюна
(1, 3, 1),   -- Собака Баскервилей

-- Выдача #2 (читатель #2)
(2, 2, 1),   -- 1984
(2, 5, 1),   -- Sapiens

-- Выдача #3 (читатель #1)
(3, 7, 1);   -- Три мушкетёра

-- Создаем таблицу издательств
CREATE TABLE Publishers (
    PublisherID INTEGER PRIMARY KEY AUTOINCREMENT,
    PublisherName TEXT NOT NULL UNIQUE
);
