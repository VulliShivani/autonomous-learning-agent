import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="learning_agent",
        user="postgres",
        password="postgres",   # use the password YOU set
        host="localhost",
        port="5432"
    )
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