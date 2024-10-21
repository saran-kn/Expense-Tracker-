import mysql.connector
from datetime import datetime
import time

DATABASE_NAME = "expense_db"
TABLE_NAME = "expense_table"

def create_database_and_table():
    try:
        # Connect to MySQL server to create the database if it doesn't exist
        connection = None
        cursor = None
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        connection.commit()
        print(f"Database checked/created.")
        
        # Close the connection and reconnect to the specific database
        cursor.close()
        connection.close()

        # Connect to the newly created database
        connection = get_connection()
        cursor = connection.cursor()

        # Create the table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id BIGINT PRIMARY KEY,
                amount DECIMAL(10, 2),
                date DATE,
                description VARCHAR(255)
            );
        """)
        connection.commit()
        print(f"Table '{TABLE_NAME}' checked/created.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_connection():
    """Establish a new connection to the database."""
    connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="saran",
            password="saran",
            database=DATABASE_NAME,
            auth_plugin='mysql_native_password'
        )
    return connection


def add_expense():
    """Add a new expense to the database."""
    connection = None
    cursor = None
    try:
        amount = float(input("Enter amount: "))
        date_str = input("Enter date (YYYY-MM-DD): ")
        description = input("Enter description: ")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        epoch_id = int(time.mktime(date_obj.timetuple()))  # Generate epoch ID

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} (id, amount, date, description)
            VALUES (%s, %s, %s, %s);
        """, (epoch_id, amount, date_obj.date(), description))
        connection.commit()
        print("Expense added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def remove_expense():
    """Remove an expense by its ID."""
    connection = None
    cursor = None
    try:
        expense_id = int(input("Enter the expense ID (epoch value) to remove: "))
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = %s;", (expense_id,))
        connection.commit()
        if cursor.rowcount > 0:
            print("Expense removed successfully.")
        else:
            print("No expense found with the given ID.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def view_expenses():
    """View expenses filtered by date, month, or year."""
    connection = None
    cursor = None
    try:
        filter_type = input("View by (date/month/year): ").strip().lower()
        connection = get_connection()
        cursor = connection.cursor()

        if filter_type == "date":
            date_str = input("Enter date (YYYY-MM-DD): ")
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE date = %s;", (date_str,))
        elif filter_type == "month":
            month = input("Enter month (YYYY-MM): ") + "-01"
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE MONTH(date) = MONTH(%s) AND YEAR(date) = YEAR(%s);", 
                           (month, month))
        elif filter_type == "year":
            year = input("Enter year (YYYY): ")
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE YEAR(date) = %s;", (year,))
        else:
            print("Invalid filter type.")
            return

        expenses = cursor.fetchall()
        total = sum(expense[1] for expense in expenses)

        if expenses:
            print(f"\nExpenses ({filter_type}):")
            for exp in expenses:
                print(f"ID: {exp[0]}, Amount: {exp[1]}, Date: {exp[2]}, Description: {exp[3]}")
            print(f"\nTotal: {total:.2f}")
        else:
            print("No expenses found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def main():
    create_database_and_table()  # Ensure the DB and table are ready

    while True:
        print("\nExpense Tracker")
        print("1. Add Expense")
        print("2. Remove Expense")
        print("3. View Expenses")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            remove_expense()
        elif choice == '3':
            view_expenses()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()