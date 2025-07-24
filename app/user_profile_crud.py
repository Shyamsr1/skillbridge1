import json
import mysql.connector
from mysql.connector import Error

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mypassword1!",
        database="skillbridge"
    )

def create_user(user_id, name, email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name, email) VALUES (%s, %s, %s)",
            (user_id, name, email)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "User created successfully"
    except Error as e:
        return f"Error: {e}"

def read_user(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        return f"Error: {e}"

def update_user(user_id, name, email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = %s, email = %s WHERE user_id = %s",
            (name, email, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "User updated successfully"
    except Error as e:
        return f"Error: {e}"

def delete_user(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return "User deleted successfully"
    except Error as e:
        return f"Error: {e}"
