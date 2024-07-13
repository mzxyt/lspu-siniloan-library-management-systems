DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS rentals;
DROP TABLE IF EXISTS rental_details;
DROP TABLE IF EXISTS authors;

CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  middlename TEXT NOT NULL,
  lastname TEXT NOT NULL,
  gender TEXT NOT NULL,
  year_level TEXT NOT NULL,
  student_id TEXT UNIQUE NOT NULL,
  photo
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    photo TEXT NOT NULL
);

CREATE TABLE categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
CREATE TABLE authors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn Text NOT NULL,
    title TEXT NOT NULL,
    sypnosis TEXT(5000) NOT NULL,
    date_published date not null,
    date_posted date null DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    isAvailable INTEGER DEFAULT 1,
    copies INTEGER DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
CREATE TABLE rentals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_no TEXT NOT NULL UNIQUE,
    student_id INTEGER NOT NULL,
    date_rented DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    --status : 0-pending, 1-approved, 2-declined, 3-Returned
    status INTEGER NOT NULL DEFAULT 0, 
    FOREIGN KEY (student_id) REFERENCES students(id)
    
);
CREATE TABLE rental_details(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rentals(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);