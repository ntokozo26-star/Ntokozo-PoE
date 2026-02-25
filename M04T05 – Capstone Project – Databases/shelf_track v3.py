"""
Shelf-Track_v3.py
================
A small-bookstore inventory manager rewritten for clarity, safety and maintainability.

Features:
---------
* Creates/opens an SQLite database called "ebookstore.db".
* Creates author and book tables and seeds them with starter data.
* Presents an interactive menu so a clerk can:
  1. Add a new book
  2. Update an existing book or its author's details
  3. Delete a book
  4. Search for books by ID or title keyword
  5. View all book details
  0. Exit the program

Best Practices:
---------------
* Code modularity: functions handle isolated responsibilities
* Error handling: handles ValueError, sqlite3.Error, and general exceptions
* Data validation: validates ID patterns, positive numbers, non-blank strings
* Context managers: with statements for all DB operations
* Style and documentation: PEP8-compliant, docstrings, consistent prompts

Pseudocode Overview:
--------------------
1. Initialize the SQLite database:
   - Create author and book tables if they don't exist
   - Seed starter data only if the tables are empty

2. Display main menu:
   - Allow the user to select options (1-5 or 0 to exit)
   - Based on selection, call the corresponding function

3. Each function includes:
   - Input validation (IDs, text, quantities)
   - Context-managed DB connection and execution
   - Proper error handling

"""


from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional, Tuple


# Constants & starter data

DB_FILE = Path("ebookstore.db")

STARTER_BOOKS: Tuple[Tuple[int, str, int, int], ...] = (
    (3001, "A Tale of Two Cities", 1290, 30),
    (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
    (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
    (3004, "The Lord of the Rings", 6380, 37),
    (3005, "Alice's Adventures in Wonderland", 5620, 12),
)

STARTER_AUTHORS: Tuple[Tuple[int, str, str], ...] = (
    (1290, "Charles Dickens", "England"),
    (8937, "J.K. Rowling", "England"),
    (2356, "C.S. Lewis", "Ireland"),
    (6380, "J.R.R. Tolkien", "South Africa"),
    (5620, "Lewis Carroll", "England"),
)

ID_PATTERN = re.compile(r"^[0-9]{4}$")

# Database helpers


def connect_db() -> sqlite3.Connection:
    return sqlite3.connect(DB_FILE, timeout=10, isolation_level="DEFERRED")

def initialise_schema() -> None:
    with connect_db() as conn, conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS author (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id       INTEGER PRIMARY KEY,
                title    TEXT NOT NULL,
                authorID INTEGER NOT NULL,
                qty      INTEGER NOT NULL CHECK (qty >= 0),
                FOREIGN KEY (authorID) REFERENCES author(id)
            )
        """)
        if not cur.execute("SELECT 1 FROM author LIMIT 1").fetchone():
            cur.executemany("INSERT INTO author (id, name, country) VALUES (?, ?, ?)", STARTER_AUTHORS)
        if not cur.execute("SELECT 1 FROM book LIMIT 1").fetchone():
            cur.executemany("INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)", STARTER_BOOKS)


# Input validation helpers

def validate_four_digit(value: str) -> int:
    if not ID_PATTERN.fullmatch(value):
        raise ValueError("ID must be exactly four numeric digits (e.g. 1234).")
    return int(value)

def prompt_id(label: str, *, allow_back: bool = False) -> Optional[int]:
    while True:
        raw = input(f"{label} (4 digits{' or b to back' if allow_back else ''}): ").strip()
        if allow_back and raw.lower() == "b":
            return None
        try:
            return validate_four_digit(raw)
        except ValueError as err:
            print(err)

def prompt_positive_int(label: str) -> int:
    while True:
        raw = input(f"{label}: ").strip()
        if raw.lower() == "b":
            print("'b' not allowed here - enter a number.")
            continue
        if not raw.isdigit() or int(raw) <= 0:
            print("Enter a positive integer.")
            continue
        return int(raw)

def prompt_non_blank(label: str) -> str:
    while True:
        text = input(f"{label}: ").strip()
        if text:
            return text
        print("Value cannot be blank.")

# Reusable DB helpers

def record_exists(table: str, pk: int) -> bool:
    with connect_db() as conn, closing(conn.cursor()) as cur:
        cur.execute(f"SELECT 1 FROM {table} WHERE id = ?", (pk,))
        return cur.fetchone() is not None

def execute(sql: str, params: tuple = ()) -> None:
    with connect_db() as conn, conn:
        conn.execute(sql, params)


# Feature: Add book

def add_book() -> None:
    print("\n Add New Book")
    while True:
        book_id = prompt_id("Book ID")
        if not record_exists("book", book_id):
            break
        print("That book ID already exists - choose a different one.")
    title = prompt_non_blank("Title")
    qty = prompt_positive_int("Quantity in stock")
    author_id = prompt_id("Author ID")
    if not record_exists("author", author_id):
        print("Author ID not found - let's create that author.")
        author_name = prompt_non_blank("Author name")
        author_country = prompt_non_blank("  Author country")
        execute("INSERT INTO author (id, name, country) VALUES (?, ?, ?)", (author_id, author_name, author_country))
    try:
        execute("INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)", (book_id, title, author_id, qty))
        print("Book added.")
    except sqlite3.IntegrityError as exc:
        print(f"DB error: {exc}")


# Feature: Update book

def fetch_book_details(book_id: int):
    with connect_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            SELECT b.title, b.qty, a.id, a.name, a.country
            FROM book b JOIN author a ON b.authorID = a.id
            WHERE b.id = ?
        """, (book_id,))
        return cur.fetchone()

def update_book() -> None:
    print("\nUpdate Book (b to menu)")
    while True:
        book_id = prompt_id("Book ID", allow_back=True)
        if book_id is None:
            return
        if record_exists("book", book_id):
            break
        print("No book matches that ID - try again.")
    title, qty, auth_id, auth_name, auth_country = fetch_book_details(book_id)
    print("\nCurrent details")
    print("---------------")
    print(f"Title          : {title}")
    print(f"Quantity       : {qty}")
    print(f"Author         : {auth_name} ({auth_country})\n")
    print("What change?")
    print("  1. Quantity  2. Title  3. Author name/country  0. Cancel")
    choice = input("Selection: ").strip()
    if choice == "1":
        new_qty = prompt_positive_int("New quantity")
        execute("UPDATE book SET qty = ? WHERE id = ?", (new_qty, book_id))
        print(" Quantity updated.")
    elif choice == "2":
        new_title = prompt_non_blank("New title")
        execute("UPDATE book SET title = ? WHERE id = ?", (new_title, book_id))
        print("Title updated.")
    elif choice == "3":
        new_name = input(f"New author name    (enter to keep '{auth_name}'): ").strip()
        new_country = input(f"New author country (enter to keep '{auth_country}'): ").strip()
        if new_name or new_country:
            execute("""
                UPDATE author
                SET name = COALESCE(NULLIF(?, ''), name),
                    country = COALESCE(NULLIF(?, ''), country)
                WHERE id = ?
            """, (new_name, new_country, auth_id))
            print("Author updated.")
        else:
            print("Nothing changed.")
    else:
        print("Cancelled.")

# Feature: Delete book

def delete_book() -> None:
    print("\n Delete Book (b to menu)")
    while True:
        book_id = prompt_id("Book ID", allow_back=True)
        if book_id is None:
            return
        if record_exists("book", book_id):
            break
        print("That ID does not exist - try again.")
    if input("Are you sure? [y/N]: ").lower() != "y":
        print("Deletion cancelled.")
        return
    execute("DELETE FROM book WHERE id = ?", (book_id,))
    print("Book deleted.")


# Feature: Search & view

def list_all_details() -> None:
    print("\n Every Book\n")
    with connect_db() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            SELECT b.title, a.name, a.country, b.qty
            FROM book b JOIN author a ON b.authorID = a.id
            ORDER BY b.title
        """)
        rows = cur.fetchall()
    if not rows:
        print("No books yet.")
        return
    for title, name, country, qty in rows:
        print("-" * 50)
        print(f"Title           : {title}")
        print(f"Author          : {name}")
        print(f"Country         : {country}")
        print(f"In stock        : {qty}")
    print("-" * 50)

def search_books() -> None:
    print("\n Search Books")
    mode = input("1. By ID  2. By title keyword  (default 1): ").strip() or "1"
    if mode == "1":
        while True:
            bid = prompt_id("Book ID", allow_back=True)
            if bid is None:
                return
            with connect_db() as conn, closing(conn.cursor()) as cur:
                cur.execute("""
                    SELECT b.title, a.name, a.country, b.qty
                    FROM book b JOIN author a ON b.authorID = a.id
                    WHERE b.id = ?
                """, (bid,))
                row = cur.fetchone()
            if row:
                title, name, country, qty = row
                print("\nResult")
                print("------")
                print(f"Title   : {title}")
                print(f"Author  : {name} ({country})")
                print(f"In stock: {qty}")
                return
            print("No match try again.")
    elif mode == "2":
        kw = prompt_non_blank("Keyword in title")
        with connect_db() as conn, closing(conn.cursor()) as cur:
            cur.execute("""
                SELECT b.title, a.name, a.country
                FROM book b JOIN author a ON b.authorID = a.id
                WHERE b.title LIKE ?
            """, (f"%{kw}%",))
            rows = cur.fetchall()
        if rows:
            for title, name, country in rows:
                print(f"* {title}  —  {name} ({country})")
        else:
            print("No matches.")
    else:
        print("Invalid selection.")


# Main Menu

def main_menu() -> None:
    initialise_schema()
    actions = {
        "1": add_book,
        "2": update_book,
        "3": delete_book,
        "4": search_books,
        "5": list_all_details,
    }
    while True:
        print("""
    Inventory Menu
  1. Enter book
  2. Update book
  3. Delete book
  4. Search books
  5. View details of all books
  0. Exit
""")
        choice = input("Select option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except sqlite3.Error as db_err:
                print(f"Database error: {db_err}")
            except Exception as ex:
                print(f"Unexpected error: {ex}")
        else:
            print("Invalid selection - try again.")

if __name__ == "__main__":
    main_menu()
