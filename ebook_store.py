import sqlite3
from tabulate import tabulate

#  Establishing a connection to the SQLite database file named 'ebookstore.db' and returns the connection object.
def connect_to_database():
    return sqlite3.connect('ebookstore.db')

# Creating a table named 'ebookstore' with columns for id, title, author, and qty. It also inserts initial data into the table.
def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ebookstore (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            qty INTEGER
        )
    """)

    cursor.execute('DELETE FROM ebookstore;')

    data = [
        (3001, "A Tale of Two Cities", "Charles Dickens", 30),
        (3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
        (3003, "The Lion, the Witch and the Wardrobe", "C. S. Lewis", 25),
        (3004, "The Lord of the Rings", "J.R.R Tolkien", 37),
        (3005, "Alice in Wonderland", "Lewis Carroll", 12)
    ]
    cursor.executemany('INSERT INTO ebookstore (id, title, author, qty) VALUES (?, ?, ?, ?)', data)

# Retrieving the maximum id value from the 'ebookstore' table. 
# It is used to assign a unique id to new records.
def get_max_id(cursor):
    cursor.execute('SELECT MAX(id) FROM ebookstore')
    max_id = cursor.fetchone()[0] or 0

    initial_data_max_id = max(row[0] for row in [
        (3001, "A Tale of Two Cities", "Charles Dickens", 30),
        (3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
        (3003, "The Lion, the Witch and the Wardrobe", "C. S. Lewis", 25),
        (3004, "The Lord of the Rings", "J.R.R Tolkien", 37),
        (3005, "Alice in Wonderland", "Lewis Carroll", 12)
    ])
    
    return max(max_id, initial_data_max_id)

# Allows the user to input information for a new book (title, author, quantity) and enters it into the database:
def enter_book(cursor):
    while True:
        # Display the current state of the 'ebookstore' table
        display_table(cursor)

        # Prompt the user to input the title of the new book
        title = input("Please enter the title name of the book: ")
        # Prompt the user to input the author's name of the new book
        author = input("Please enter the author's name: ")

        # Check if the entered title or author is empty or contains only whitespace characters
        if not title.strip() or not author.strip():
            print("You cannot leave the title and author empty. Please try again.")
            continue

        while True:
            try:
                # Attempt to convert user input into an integer (quantity)
                qty = int(input("Please enter the quantity: "))
                # Check if the entered quantity is negative
                if qty < 0:
                    raise ValueError("Please enter whole numbers only. (1, 15, 200)")
                break
            except ValueError as e:
                # Catch a ValueError if the user input cannot be converted to an integer
                print(f"Error: {e}")
                print("Please enter only whole numbers for quantity. (1, 15, 200)")

        # Get the maximum id value currently in the 'ebookstore' table
        max_id = get_max_id(cursor)
        # Calculate a new id for the upcoming book, ensuring uniqueness
        new_id = max_id + 1

        # Insert the new book's information into the 'ebookstore' table
        cursor.execute('INSERT INTO ebookstore (id, title, author, qty) VALUES (?, ?, ?, ?)', (new_id, title, author, qty))

        # Commit the changes to the database
        cursor.connection.commit()

        # Display the updated state of the 'ebookstore' table, including the newly added book
        display_table(cursor)

        # Exit the outer loop, ending the function execution
        break

#  Checks whether a given book id exists in the 'ebookstore' table:
def is_valid_book_id(book_id, cursor):
    try:
        book_id = int(book_id)
        cursor.execute('SELECT id FROM ebookstore WHERE id = ?', (book_id,))
        return cursor.fetchone() is not None
    except ValueError:
        return False

# Allows the user to update the quantity of a book by providing the book id and the new quantity
def update_book(cursor):
    while True:
        # Display the current state of the 'ebookstore' table
        display_table(cursor)
        book_id = input("Enter the book ID to update: ")

        # Check if the entered book ID is valid
        if not is_valid_book_id(book_id, cursor):
            print("Error: Invalid book ID. Please enter a valid book ID.")
            continue

        # Prompt the user to input the new quantity
        new_qty = input("Please enter the new quantity: ")

        while True:
            try:
                # Attempt to convert the user input into an integer (new quantity)
                new_qty = int(new_qty)
                # Check if the new quantity is non-negative
                if new_qty < 0:
                    raise ValueError("Quantity should be whole numbers only. (1, 15, 200)")
                break
            except ValueError as e:
                print(f"Error: {e}")
                print("Please enter a whole number for quantity.")

        # Update the 'ebookstore' table with the new quantity for the specified book ID
        cursor.execute('UPDATE ebookstore SET qty = ? WHERE id = ?', (new_qty, book_id))
     
        cursor.connection.commit()
        
        print("Book updated successfully.")
        # Display the updated state of the 'ebookstore' table
        display_table(cursor)
        break

# Allows the user to delete a book by providing the book ID
def delete_book(cursor):
    while True:
        try:
            print("Please enter the book ID number you would like to delete.")
            book_id = int(input("Enter here:"))

            # Check if the entered book ID is valid
            if not is_valid_book_id(book_id, cursor):
                print("Error: Invalid book ID. Please enter a valid book ID.")
                continue

            # Delete the book from the 'ebookstore' table
            cursor.execute('DELETE FROM ebookstore WHERE id = ?', (book_id,))
            
            cursor.connection.commit()
            
            print(f"Book with ID {book_id} deleted successfully.")
            # Display the updated state of the 'ebookstore' table
            display_table(cursor)
            break
        except ValueError:
            print("Error: Please enter a valid integer for book ID.")
        except Exception as e:
            print(f"Error: {e}")

# Allows the user to search for books by title or author
def search_book(cursor):
    display_table(cursor)
    keyword = input("Enter a title or author to search for: ")

    # Search for books with titles or authors that match the provided keyword
    cursor.execute('SELECT * FROM ebookstore WHERE title LIKE ? OR author LIKE ?', ('%' + keyword + '%', '%' + keyword + '%'))
    books = cursor.fetchall()

    if not books:
        print("No matching books found.")
    else:
        # Display the search results in a tabular format
        display_table(cursor)

# Retrieves all records from the 'ebookstore' table and displays them in a tabular format using the tabulate library
def display_table(cursor):
    cursor.execute('SELECT * FROM ebookstore')
    books = cursor.fetchall()

    if not books:
        print("No books in the database.")
    else:
        headers = ["ID", "Title", "Author", "Quantity"]
        table = tabulate(books, headers=headers, tablefmt="grid")
        print(table)


# An interactive menu for the user to choose operations listed below:
def menu():
    with connect_to_database() as connection:
        cursor = connection.cursor()
        create_table(cursor)

        while True:
            print("\nWelcome, please select the following below:\n")
            print("Menu")
            print("1. Enter book")
            print("2. Update book")
            print("3. Delete book")
            print("4. Search books")
            print("5. Display books")
            print("0. Exit  ")

            choice = input("Please enter your choice: ")

            if choice == "1":
                enter_book(cursor)

            elif choice == "2":
                update_book(cursor)

            elif choice == "3":
                delete_book(cursor)

            elif choice == "4":
                search_book(cursor)
            
            elif choice == "5":
                display_table(cursor)

            elif choice == "0":
                print("Exiting program. Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

# __main__ block: Calls the menu() function when the script is run.
if __name__ == "__main__":
    menu()