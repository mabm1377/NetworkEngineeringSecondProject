from functools import lru_cache
from psycopg2.extras import DictCursor
from psycopg2.extensions import cursor
from pprint import pprint
import datetime
import psycopg2


@lru_cache()
def create_postgres_connection():
    connection = psycopg2.connect(dbname="learning", host="0.0.0.0", user="learning", password="learning")
    connection.autocommit = True
    return connection


text = "سلام من دارم میام خونه تو هم بیا خونه من"


def insert_news(news):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    news["time"] = datetime.datetime.fromtimestamp(news["time"])
    news["time"] = datetime.datetime.strftime(news['time'], '%Y-%m-%d %H:%M:%S')
    try:
        cur.execute(
            f"insert into news(id,body,title,updated_at,image_url,news_agency,link) "
            f"values('{news['id']}','{news['body']}','{news['title']}','{news['time']}','{news['img']}',"
            f"'{news['news_agency']}','{news['link']}') ")
    except Exception as e:
        print(str(e))


def update_news(news):
    pass


def save_news(news):
    return insert_news(news)


def check_exist_news(news_id):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    cur.execute(f"select exists(select 1 from news where id='{news_id}') as news_existed")
    return cur.fetchone()['news_existed']


def save_tf_idf_of_news(tf_idf_dict, news_id):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    for key, value in tf_idf_dict.items():
        cur.execute(f"insert into docs_tf_idf(word, tf_idf, doc_id) values ('{str(key)}',{value},'{news_id}' )")


def calculate_tf_idf(news: str, news_id):
    terms = news.split(" ")
    terms_dict = dict()
    global_terms_number = 0
    tf_idf_results = dict()
    for term in terms:
        if len(term) < 3:
            continue
        if term not in terms_dict:
            terms_dict[term] = 0
        terms_dict[term] += 1
        global_terms_number += 1
    for key, value in terms_dict.items():
        tf_idf_results[key] = value / global_terms_number
    save_tf_idf_of_news(tf_idf_results, news_id)


def read_news(_from: int, _limit: int):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    cur.execute(f"select * from news ORDER BY updated_at LIMIT {_limit} OFFSET {_from} ")
    all_news = []
    for news in cur.fetchall():
        all_news.append({key: value for key, value in news.items()})
    return all_news


def read_news_of_on_news_agency(news_agency_name, _from: int, _limit: int):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    cur.execute(
        f"select * from news where news_agency = '{news_agency_name}' ORDER BY updated_at LIMIT {_limit} OFFSET {_from} ")
    all_news = []
    for news in cur.fetchall():
        all_news.append({key: value for key, value in news.items()})
    return all_news


if __name__ == '__main__':
    pprint(read_news(0, 10))
