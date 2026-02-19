import psycopg2
import os


def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)


# 🔥 This function creates the table automatically
def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            mode VARCHAR(100),
            topic TEXT,
            score INTEGER,
            attempt INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def save_progress(user_id, mode, topic, score, attempt):
    if not user_id:
        return

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
