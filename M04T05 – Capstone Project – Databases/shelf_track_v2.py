"""
shelf_track_v2.py
==============

A small bookstore inventory manager.

Part2 additions
----------------
• New table "author" (id, name, country) with starter data.
• Menu item 5 - View details of all books (title ,author and country).
• Update flow now shows current author name and country and lets you edit them.
• When adding a book, if the author ID is unknown, you can create that author
  on the spot.

UX niceties
-----------
• Type **b** at any ID prompt to return to the main menu.
• All ID prompts re-ask until a valid one is entered.
• Parameterised SQL throughout (safe from injection) and graceful errors.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Tuple

# Starter data

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


# Database helpers

def get_connection() -> sqlite3.Connection:
    """Connect to (or create) the SQLite DB."""
    return sqlite3.connect(DB_FILE)


def initialise_schema(cur: sqlite3.Cursor) -> None:
    """Create tables and initiate starter rows if empty."""
    # book table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS book (
            id       INTEGER PRIMARY KEY,
            title    TEXT    NOT NULL,
            authorID INTEGER NOT NULL,
            qty      INTEGER NOT NULL CHECK (qty >= 0),
            FOREIGN KEY (authorID) REFERENCES author(id)
        )
        """
    )

    # author table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS author (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            country TEXT NOT NULL
        )
        """
    )

    # predifined authors
    cur.execute("SELECT COUNT(*) FROM author")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
            STARTER_AUTHORS,
        )

    # predfined books
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
    Prompt repeatedly for an integer.
    • 'positive=True' = number must be > 0
    • 'allow_back=True' = typing 'b' returns None (go back)
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


def record_exists(cur: sqlite3.Cursor, table: str, pk: int) -> bool:
    """Generic existence check for a primary-key value in `table`."""
    cur.execute(f"SELECT 1 FROM {table} WHERE id = ?", (pk,))
    return cur.fetchone() is not None



# CRUD operations

def add_book(cur: sqlite3.Cursor) -> None:
    """Add a new book (and author row if needed)."""
    print("\n  Add New Book")

    # Book ID (unique)
    while True:
        new_id = prompt_int("Enter new book ID: ", positive=True)
        if record_exists(cur, "book", new_id):
            print("That ID already exists. Please choose another.")
        else:
            break

    # Title
    title = input("Enter book title: ").strip()
    if not title:
        print("Title cannot be empty. Operation cancelled.")
        return

    # Author ID (must exist or create)
    author_id = prompt_int("Enter author ID: ", positive=True)
    if not record_exists(cur, "author", author_id):
        # Create new author row
        print("Author ID not found — let's add that author.")
        name = input("  Author name : ").strip()
        country = input("  Author country : ").strip()
        if not name or not country:
            print("Author data incomplete. Operation cancelled.")
            return
        try:
            cur.execute(
                "INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
                (author_id, name, country),
            )
        except sqlite3.Error as exc:
            print(f"Database error: {exc}")
            return

    # Quantity
    qty = prompt_int("Enter quantity: ", positive=True)

    # Insert book
    try:
        cur.execute(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            (new_id, title, author_id, qty),
        )
        print("Book added successfully.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def update_book(cur: sqlite3.Cursor) -> None:
    """
    Update a book's quantity/title OR its author's name/country.
    Shows current details, then lets user change whichever fields they want.
    """
    print("\n Update Book   (type 'b' to go back)")

    # Valid book ID
    while True:
        book_id = prompt_int("Enter book ID to update: ", allow_back=True)
        if book_id is None:
            print("Returning to menu.")
            return
        if not record_exists(cur, "book", book_id):
            print("Book ID not found. Please try again.")
        else:
            break

    # Fetch current joined details
    cur.execute(
        """
        SELECT b.title, b.qty, a.id, a.name, a.country
        FROM book b
        JOIN author a ON b.authorID = a.id
        WHERE b.id = ?
        """,
        (book_id,),
    )
    title, qty, author_id, author_name, author_country = cur.fetchone()

    print("\nCurrent details")
    print("---------------")
    print(f"Title          : {title}")
    print(f"Quantity       : {qty}")
    print(f"Author name    : {author_name}")
    print(f"Author country : {author_country}\n")

    print(
        "What would you like to change?\n"
        "  1. Quantity\n"
        "  2. Title\n"
        "  3. Author name and/or country\n"
        "  0. Cancel"
    )
    choice = input("Selection: ").strip() or "0"

    try:
        # Quantity
        if choice == "1":  
            new_qty = prompt_int("Enter new quantity: ", positive=True)
            cur.execute("UPDATE book SET qty = ? WHERE id = ?", (new_qty, book_id))
            print("Quantity updated.")
        # Title
        elif choice == "2":  
            new_title = input("Enter new title: ").strip()
            if not new_title:
                print("Title cannot be empty. No change made.")
                return
            cur.execute("UPDATE book SET title = ? WHERE id = ?", (new_title, book_id))
            print("Title updated.")

        # Author details
        elif choice == "3":  
            new_name = input(f"New author name    (blank = keep '{author_name}') : ").strip()
            new_country = input(f"New author country (blank = keep '{author_country}') : ").strip()
            if new_name or new_country:
                cur.execute(
                    """
                    UPDATE author
                    SET name = COALESCE(NULLIF(?,''), name),
                        country = COALESCE(NULLIF(?,''), country)
                    WHERE id = ?
                    """,
                    (new_name, new_country, author_id),
                )
                print("Author details updated.")
            else:
                print("Nothing entered. No change made.")
        else:
            print("Update cancelled.")

    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def delete_book(cur: sqlite3.Cursor) -> None:
    """Delete a book row (keeps author row intact)."""
    print("\n Delete Book  (type 'b' to go back)")
    while True:
        book_id = prompt_int("Enter the ID of the book to delete: ", allow_back=True)
        if book_id is None:
            print("Returning to menu.")
            return
        if not record_exists(cur, "book", book_id):
            print("Book ID not found. Please try again.")
        else:
            break

    confirm = input("Are you sure you want to delete this book? [y/N]: ").lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    try:
        cur.execute("DELETE FROM book WHERE id = ?", (book_id,))
        print("Book deleted successfully.")
    except sqlite3.Error as exc:
        print(f"Database error: {exc}")


def search_books(cur: sqlite3.Cursor) -> None:
    """Search by ID or title keyword."""
    print("\n Search Books")
    print("Search by: 1. ID  2. Title keyword")
    option = input("Choice [1/2]: ").strip() or "1"

    if option == "1":
        print("Search by ID (type 'b' to go back)")
        while True:
            book_id = prompt_int("Enter ID to search: ", allow_back=True)
            if book_id is None:
                print("Returning to menu.")
                return
            cur.execute(
                """
                SELECT b.title, a.name, a.country, b.qty
                FROM book b
                JOIN author a ON b.authorID = a.id
                WHERE b.id = ?
                """,
                (book_id,),
            )
            row = cur.fetchone()
            if row:
                title, name, country, qty = row
                print("\nResult")
                print("----------")
                print(f"Title          : {title}")
                print(f"Author         : {name} ({country})")
                print(f"Quantity in DB : {qty}")
                break
            else:
                print("No book found with that ID. Please try again.")

    elif option == "2":
        keyword = input("Enter title keyword: ").strip()
        if not keyword:
            print("Keyword cannot be empty.")
            return
        cur.execute(
            """
            SELECT b.title, a.name, a.country
            FROM book b
            JOIN author a ON b.authorID = a.id
            WHERE b.title LIKE ?
            """,
            (f"%{keyword}%",),
        )
        rows = cur.fetchall()
        if rows:
            print("\n Results")
            print("-----------")
            for title, name, country in rows:
                print(f"{title}  —  {name} ({country})")
        else:
            print("No matching books found.")
    else:
        print("Invalid option.")


def view_all_details(cur: sqlite3.Cursor) -> None:
    """Display every book with its author name and country."""
    print("\n Full Book Details\n")
    cur.execute(
        """
        SELECT b.title, a.name, a.country
        FROM book b
        JOIN author a ON b.authorID = a.id
        ORDER BY b.title
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("No books in database.")
        return

    for title, name, country in rows:
        print("--------------------------------------------------")
        print(f"Title           : {title}")
        print(f"Author's Name   : {name}")
        print(f"Author's Country: {country}")
    print("--------------------------------------------------")


# Main menu loop

def menu() -> None:
    """Main control loop."""
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
                "  5. View details of all books\n"
                "  0. Exit"
            )
            choice = input("Select an option: ").strip()

            if choice == "1":
                add_book(cur)
            elif choice == "2":
                update_book(cur)
            elif choice == "3":
                delete_book(cur)
            elif choice == "4":
                search_books(cur)
            elif choice == "5":
                view_all_details(cur)
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid selection, please try again.")

            conn.commit()


# Entry point
if __name__ == "__main__":
    menu()
