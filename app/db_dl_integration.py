
import mysql.connector
from datetime import datetime
import json

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mypassword1!",
        database="skillbridge"
    )

# --- User Creation ---
def create_user(username, email, password, language):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute(
        "INSERT INTO users (username, email, password, language) VALUES (%s, %s, %s, %s)",
        (username, email, password, language)
    )
    conn.commit()
    conn.close()
    return True

# --- User Retrieval ---
def get_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user

# --- Original Assessment Save ---
def save_assessment(username, role, skill_ratings, quiz_results, readiness_score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO assessments (username, role, skill_ratings, quiz_results, readiness_score, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, role, skill_ratings, quiz_results, readiness_score, datetime.now())
    )
    conn.commit()
    conn.close()

# --- DL-enhanced Assessment Save ---
def save_assessment_with_dl(username, role, skill_ratings, quiz_results, readiness_score, dl_readiness_score, dl_skill_gaps, learning_paths):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO assessments (
            username, role, skill_ratings, quiz_results, readiness_score,
            dl_readiness_score, dl_skill_gaps, recommended_learning_paths, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            username,
            role,
            json.dumps(skill_ratings),
            json.dumps(quiz_results),
            readiness_score,
            dl_readiness_score,
            json.dumps(dl_skill_gaps),
            json.dumps(learning_paths),
            datetime.now()
        )
    )
    conn.commit()
    conn.close()

# --- Fetch Past Assessments ---
def get_assessments_by_user(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assessments WHERE username = %s ORDER BY created_at DESC", (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows
