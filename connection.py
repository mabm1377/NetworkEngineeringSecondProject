import psycopg2
from functools import lru_cache


@lru_cache()
def get_connection():
    connection = psycopg2.connect(dbname="learning", host="0.0.0.0", user="learning", password="learning")
    connection.autocommit = True
    return connection
