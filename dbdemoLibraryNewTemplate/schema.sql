-- ============================================================
--  schema.sql — ระบบห้องสมุด (category, book, member, borrow, fine)
--  รันไฟล์นี้ทั้งไฟล์บน MySQL เพื่อสร้างตาราง + ข้อมูลตัวอย่าง
-- ============================================================

/*
DROP TABLE IF EXISTS fine;
DROP TABLE IF EXISTS borrow;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS category;
*/

-- =====================================================
-- 1. CATEGORY
-- =====================================================

CREATE TABLE category (
    category_id  INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(255)
);


-- =====================================================
-- 2. BOOK
-- =====================================================

CREATE TABLE book (
    book_id       INT AUTO_INCREMENT PRIMARY KEY,
    isbn          VARCHAR(20)  UNIQUE,
    title         VARCHAR(255) NOT NULL,
    author        VARCHAR(150) NOT NULL,
    category_id   INT NOT NULL,
    publish_year  YEAR,
    quantity      INT NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);


-- =====================================================
-- 3. MEMBER
-- =====================================================

CREATE TABLE member (
    member_id   INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    gender      ENUM('female', 'male', 'non_binary', 'not_specified')
                NOT NULL DEFAULT 'not_specified',
    email       VARCHAR(100) UNIQUE,
    phone       VARCHAR(20),
    status      ENUM('active', 'inactive') NOT NULL DEFAULT 'active'
);


-- =====================================================
-- 4. BORROW
-- =====================================================

CREATE TABLE borrow (
    borrow_id    INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT NOT NULL,
    member_id    INT NOT NULL,
    borrow_date  DATE NOT NULL,
    due_date     DATE NOT NULL,
    return_date  DATE,                       -- NULL = ยังไม่คืน
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);


-- =====================================================
-- 5. FINE
-- =====================================================

CREATE TABLE fine (
    fine_id    INT AUTO_INCREMENT PRIMARY KEY,
    borrow_id  INT NOT NULL UNIQUE,
    amount     DECIMAL(8,2) NOT NULL DEFAULT 0,
    paid       BOOLEAN NOT NULL DEFAULT FALSE,
    paid_date  DATE,
    FOREIGN KEY (borrow_id) REFERENCES borrow(borrow_id)
);



-- =====================================================
-- 1. CATEGORY
-- =====================================================

INSERT INTO category(category_id, name,         description)
VALUES
    (1,           'Computer',  'คอมพิวเตอร์ การเขียนโปรแกรม'),
    (2,           'Science',   'วิทยาศาสตร์ และเทคโนโลยี'),
    (3,           'Novel',     'นวนิยาย เรื่องสั้น เรื่องอ่านเล่น'),
    (4,           'Business',  'ธุรกิจ เศรษฐศาสตร์'),
    (5,           'Manga',     'กาตูนย์ มังงะ');


-- =====================================================
-- 2. BOOK
-- =====================================================

INSERT INTO book(book_id, isbn, title,                         author,             category_id, publish_year, quantity)
VALUES
    (1,       '9780131103627', 'The C Programming Language',  'Brian Kernighan',   1,          1988,         3),
    (2,       '9780132350884', 'Clean Code',                  'Robert Martin',     1,          2008,         5),
    (3,       '9780262033848', 'Introduction to Algorithms',  'Thomas Cormen',     1,          2009,         2),
    (4,       '9781492078005', 'Python Crash Course',         'Eric Matthes',      1,          2023,         4),
    (5,       '9780134685991', 'Effective Java',              'Joshua Bloch',      1,          2018,         3),
    (6,       '9780593135204', 'Harry Potter',                'JK Rowling',        3,          2000,         4),
    (7,       '9786162871234', 'Hunter x Hunter',             'Yoshihiro Togashi', 5,          2001,         5),
    (8,       '9786162871235', 'Naruto',                	  'Masashi Kishimoto', 5,          2000,         3),
    (9,       '9786162871236', 'One Piece',                   'Eiichiro Oda',      5,          1997,         4),
    (10,      '9780134494166', 'Fundamentals of Physics',     'David Halliday',    2,          2013,         2),
    (11,      '9781292407337', 'Principles of Marketing',     'Philip Kotler',     4,          2020,         1),
    (12,      '9780135166307', 'Database System Concepts',    'Abraham Silberschatz', 1,       2019,         3);


-- =====================================================
-- 3. MEMBER
-- =====================================================

INSERT INTO member(member_id, name,             gender,          email,               phone,        status)
VALUES
    (1,        'J Hope',         'male',          'jhope@email.com',   '0812345678', 'active'),
    (2,        'Prymania',       'female',        'prymania@email.com','0823456789', 'active'),
    (3,        'Anan Wong',      'male',          'anan@email.com',    '0834567890', 'active'),
    (4,        'Malee Sai',      'female',        'malee@email.com',   '0845678901', 'active'),
    (5,        'Narin Suk',      'male',          'narin@email.com',   '0856789012', 'inactive'),
    (6,        'Ploy Kanya',     'female',        'ploy@email.com',    '0867890123', 'active'),
    (7,        'Krit Sorn',      'non_binary',    'krit@email.com',    '0878901234', 'active'),
    (8,        'Mali Chai',      'not_specified', 'mali@email.com',    '0889012345', 'active');


-- =====================================================
-- 4. BORROW
-- =====================================================

INSERT INTO borrow(borrow_id, book_id, member_id, borrow_date,  due_date,    return_date)
VALUES
    (1,         2,       1,         '2026-09-01', '2026-09-15', '2026-09-10'),
    (2,         7,       2,         '2026-09-02', '2026-09-16', NULL),
    (3,         4,       3,         '2026-09-03', '2026-09-17', '2026-09-15'),
    (4,         6,       4,         '2026-09-04', '2026-09-18', NULL),
    (5,         3,       1,         '2026-09-05', '2026-09-19', '2026-09-18'),
    (6,         9,       5,         '2026-09-06', '2026-09-20', NULL),
    (7,         11,      6,         '2026-09-07', '2026-09-21', NULL),
    (8,         12,      7,         '2026-09-08', '2026-09-22', '2026-09-20'),
    (9,         2,       8,         '2026-09-10', '2026-09-24', NULL),
    (10,        7,       3,         '2026-09-11', '2026-09-25', NULL);


-- =====================================================
-- 5. FINE
-- =====================================================

INSERT INTO fine
    (fine_id, borrow_id, amount, paid, paid_date)
VALUES
    (1,       4,         30.00,  FALSE, NULL),
    (2,       6,         50.00,  TRUE,  '2026-09-22');

