"""
shelf_track_v1.py
==============

A small-bookstore inventory manager.

Features:
---------
• Opens/creates "ebookstore.db" SQLite database.
• Ensures a book table exists and predefined starter data if empty.
• Offers a menu for:
  1. Adding books
  2. Updating existing books
  3. Deleting books
  4. Searching books by ID or title keyword
  0. Exiting the program

Extras:
-------
• Allows retrying if a book ID isn't found.
• Allows typing 'b' to return to the main menu during ID prompts.
• Includes input validation, parameterized SQL (safe from injection), and error handling.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Tuple

# Path to SQLite database file
DB_FILE = Path("ebookstore.db")

# Initial set of books to populate the database
STARTER_BOOKS: Tuple[Tuple[int, str, int, int], ...] = (
    (3001, "A Tale of Two Cities", 1290, 30),
    (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
    (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
    (3004, "The Lord of the Rings", 6380, 37),
    (3005, "Alice's Adventures in Wonderland", 5620, 12),
)

# Database setup
def get_connection() -> sqlite3.Connection:
    """Connect to the SQLite database (or create if it doesn't exist)."""
    return sqlite3.connect(DB_FILE)


def initialise_schema(cur: sqlite3.Cursor) -> None:
    """
    Create the book table if it does not exist and insert starter data
    if the table is empty.
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id       INTEGER PRIMARY KEY,
            title    TEXT    NOT NULL,
            authorID INTEGER NOT NULL,
            qty      INTEGER NOT NULL CHECK (qty >= 0)
        )
    """)
    # intiate  with starter books if the table is empty
    cur.execute("SELECT COUNT(*) FROM book")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            STARTER_BOOKS,
        )


# Input helpers

def prompt_int(
    prompt: str,
    *,
    positive: bool = False,
    allow_back: bool = False,
) -> Optional[int]:
    """
    Prompt the user for a number until valid.
    If allow_back=True, typing 'b' will return None to go back to the menu.
    """
    while True:
        value = input(prompt).strip().lower()
        if allow_back and value == "b":
            return None
        if not value:
            print("Input cannot be blank. Try again.")
            continue
        if not value.isdigit():
            print("Please enter a valid number.")
            continue
        num = int(value)
        if positive and num <= 0:
            print("Number must be greater than zero.")
            continue
        return num


def book_exists(cur: sqlite3.Cursor, book_id: int) -> bool:
    """Check if a book with the given ID exists in the database."""
    cur.execute("SELECT 1 FROM book WHERE id = ?", (book_id,))
    return cur.fetchone() is not None

# CRUD Operations

def add_book(cur: sqlite3.Cursor) -> None:
    """Add a new book to the database."""
    print("\n Add New Book")
    
    # Prompt for new ID and ensure uniqueness
    while True:
        new_id = prompt_int("Enter new book ID: ", positive=True)
        if book_exists(cur, new_id):
            print("That ID already exists. Please choose another.")
        else:
            break

    # Prompt for other book details
    title = input("Enter book title: ").strip()
    if not title:
        print("Title cannot be empty. Operation cancelled.")
        return

    author_id = prompt_int("Enter author ID: ", positive=True)
    qty = prompt_int("Enter quantity: ", positive=True)

    # Insert book into database
    try:
        cur.execute(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            (new_id, title, author_id, qty),
        )
        print(" Book added successfully.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def update_book(cur: sqlite3.Cursor) -> None:
    """Update quantity, title, or authorID of an existing book."""
    print("\n Update Book   (type 'b' to go back)")
    
    # Prompt for valid book ID
    while True:
        book_id = prompt_int("Enter the ID of the book to update: ", allow_back=True)
        if book_id is None:
            print(" Returning to menu.")
            return
        if not book_exists(cur, book_id):
            print("Book ID not found. Please try again.")
        else:
            break

    # Prompt for update field
    print("Choose field to update (default is quantity):\n"
          "  1. Quantity\n  2. Title\n  3. AuthorID")
    choice = input("Selection [1/2/3]: ").strip() or "1"

    # Determine update action
    if choice == "1":
        qty = prompt_int("Enter new quantity: ", positive=True)
        sql, params = ("UPDATE book SET qty = ? WHERE id = ?", (qty, book_id))
    elif choice == "2":
        new_title = input("Enter new title: ").strip()
        if not new_title:
            print("Title cannot be empty. Update cancelled.")
            return
        sql, params = ("UPDATE book SET title = ? WHERE id = ?", (new_title, book_id))
    elif choice == "3":
        new_author = prompt_int("Enter new author ID: ", positive=True)
        sql, params = ("UPDATE book SET authorID = ? WHERE id = ?", (new_author, book_id))
    else:
        print("Invalid selection. No changes made.")
        return

    # Execute update
    try:
        cur.execute(sql, params)
        if cur.rowcount:
            print("Book updated successfully.")
        else:
            print("No rows were updated.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def delete_book(cur: sqlite3.Cursor) -> None:
    """Delete a book from the database."""
    print("\n Delete Book  (type 'b' to go back)")

    # Prompt for book ID to delete
    while True:
        book_id = prompt_int("Enter the ID of the book to delete: ", allow_back=True)
        if book_id is None:
            print("Returning to menu.")
            return
        if not book_exists(cur, book_id):
            print("Book ID not found. Please try again.")
        else:
            break

    # Confirm deletion
    confirm = input("Are you sure you want to delete this book? [y/N]: ").lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    # Execute delete
    try:
        cur.execute("DELETE FROM book WHERE id = ?", (book_id,))
        print("Book deleted successfully.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def search_books(cur: sqlite3.Cursor) -> None:
    """Search for books by ID or by title keyword."""
    print("\n  Search Books")
    print("Search by: 1. ID  2. Title keyword")
    option = input("Choice [1/2]: ").strip() or "1"

    if option == "1":
        print(" Search by ID (type 'b' to go back)")
        while True:
            book_id = prompt_int("Enter ID to search: ", allow_back=True)
            if book_id is None:
                print("  Returning to menu.")
                return
            cur.execute("SELECT * FROM book WHERE id = ?", (book_id,))
            row = cur.fetchone()
            if row:
                print("\n Search Result:")
                print(row)
                break
            else:
                print("No book found with that ID. Please try again.")

    elif option == "2":
        keyword = input("Enter title keyword: ").strip()
        if not keyword:
            print("Keyword cannot be empty.")
            return
        cur.execute("SELECT * FROM book WHERE title LIKE ?", (f"%{keyword}%",))
        rows = cur.fetchall()
        if rows:
            print("\n Search Results:")
            for row in rows:
                print(row)
        else:
            print("No matching books found.")
    else:
        print("Invalid option.")


# Main menu loop

def menu() -> None:
    """Display main menu and handle user selections."""
    with get_connection() as conn:
        cur = conn.cursor()
        initialise_schema(cur)
        conn.commit()

        while True:
            print(
                "\n Bookstore Inventory Menu\n"
                "  1. Enter book\n"
                "  2. Update book\n"
                "  3. Delete book\n"
                "  4. Search books\n"
                "  0. Exit"
            )
            selection = input("Select an option: ").strip()

            if selection == "1":
                add_book(cur)
            elif selection == "2":
                update_book(cur)
            elif selection == "3":
                delete_book(cur)
            elif selection == "4":
                search_books(cur)
            elif selection == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid selection, please try again.")

            conn.commit()


# Entry point

if __name__ == "__main__":
    menu()
