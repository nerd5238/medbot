import sqlite3

def list_appointments():
    # Connect to the SQLite database
    conn = sqlite3.connect('clinic.db')

    # Create a cursor object
    c = conn.cursor()

    # SQL query to select all rows from the appointments table
    query = "SELECT * FROM users"

    try:
        # Execute the query
        c.execute(query)

        # Fetch all rows
        rows = c.fetchall()

        print("Appointments:")
        # Print each row
        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if (conn):
            conn.close()

# Call the function to list appointments
list_appointments()