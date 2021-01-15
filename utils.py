from functools import lru_cache
from psycopg2.extras import DictCursor
from psycopg2.extensions import cursor
import datetime
import psycopg2
from flask import jsonify


@lru_cache()
def create_postgres_connection():
    connection = psycopg2.connect(dbname="learning", host="0.0.0.0", user="learning", password="learning")
    connection.autocommit = True
    return connection


def get_news(news_id):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    try:
        cur.execute(f"select * from news where id ='{news_id}' ")
        return {key: value for key, value in cur.fetchone().items()}

    except Exception as e:
        print(str(e))


def invert_index(news):
    id = news['id']
    if not check_exist_news(id):
        return
    body = str(news['body'])
    words = set(body.split(" "))
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    for word in words:
        try:
            cur.execute(f"insert into inverted_index(news_id,term) values ('{id}','{word}')")
        except Exception as e:
            print(str(e))


def get_not_ranked_news_with_query_terms(query_terms: set):
    a = ""
    for term in query_terms:
        a += f"'{str(term)}',"
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)

    cur.execute(f"select distinct(news_id) from inverted_index where term in ({a[:-1]})")
    result = []
    for item in cur.fetchall():
        if item["news_id"] is not None:
            result.append(item["news_id"])
    return result


def calculate_tf_idf(query_terms, news_id):
    news = get_news(news_id)
    body_terms = str(news["body"]).split(" ")
    tf = 0
    for i, body_term in enumerate(body_terms):
        if query_terms[0] == body_term:
            k = 0
            for query_term in query_terms:
                if query_term != body_terms[i + k]:
                    break
                k += 1
            else:
                tf += 1
    tf_idf = tf / len(body_terms)
    if tf_idf > 0:
        return tf_idf, news
    else:
        return tf_idf, None


def search(query: str):
    query_terms = set(query.split(" "))
    news_ids = get_not_ranked_news_with_query_terms(query_terms)
    ranked_news = []
    for news_id in news_ids:
        tf_idf, news = calculate_tf_idf(query.split(" "), news_id)
        if news is not None:
            ranked_news.append({"news_id": news_id, "tf_idf": tf_idf, "news": news})
    ranked_news.sort(key=lambda x: x.get("tf_idf"), reverse=True)
    return ranked_news[0:10]


def insert_news(news):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    id = news['id']
    if check_exist_news(id):
        return
    news["time"] = datetime.datetime.fromtimestamp(news["time"])
    news["time"] = datetime.datetime.strftime(news['time'], '%Y-%m-%d %H:%M:%S')
    try:
        cur.execute(
            f"insert into news(id,body,title,updated_at,image_url,news_agency,link) "
            f"values('{news['id']}','{news['body']}','{news['title']}','{news['time']}','{news['img']}',"
            f"'{news['news_agency']}','{news['link']}') ")
    except Exception as e:
        print(str(e))


def save_news(news):
    return insert_news(news)


def check_exist_news(news_id):
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    cur.execute(f"select exists(select 1 from news where id='{news_id}') as news_existed")
    return cur.fetchone()['news_existed']


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


def visit_news(news_id):
    if not check_exist_news(news_id):
        return jsonify({"error": "چنین خبری وجود ندارد"}), 404
    cur: cursor = create_postgres_connection().cursor(cursor_factory=DictCursor)
    cur.execute(f"update news set visit=visit+1 where id = '{news_id}' RETURNING visit")
    return jsonify({"visit": cur.fetchone()["visit"]}), 200

# if __name__ == "__main__":
#     print(visit_news("71952248825273618625976079404344221381471001777672550813923485717447029901517"))
