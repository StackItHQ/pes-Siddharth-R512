# db_connection.py

import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create a database connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",     # Replace with your DB username
            password="Siddhu123",  # Replace with your DB password
            database="google_sheet_sync"   # Replace with your DB name
        )
        if connection.is_connected():
            print("Successfully connected to the database")
    except Error as e:
        print(f"Error: '{e}' occurred while connecting to the database")
    return connection

def close_connection(connection):
    """Close the database connection."""
    if connection.is_connected():
        connection.close()
        print("Connection to database closed")
