import psycopg2
import os 

def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL)

def save_progress(user_id, mode, topic, score, attempt):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO progress (user_id, mode, topic, score, attempt)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, mode, topic, score, attempt)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_progress():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT mode, topic, score, attempt, created_at FROM progress"
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows