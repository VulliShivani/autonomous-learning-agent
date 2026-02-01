import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="learning_agent",
        user="postgres",
        password="postgres",   # use the password YOU set
        host="localhost",
        port="5432"
    )
