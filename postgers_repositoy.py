from psycopg2.extras import DictCursor
from psycopg2.extensions import cursor
import hazm
from pprint import pprint
from connection import get_connection
from datetime import datetime, timedelta


class PostgresRepository:

    def get_current_urls_for_fetch_news(self):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute("select * from current_urls")
        return [item["url"] for item in cur.fetchall()]

    def set_current_urls_for_fetch_news(self, urls: list):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute("delete from current_urls")
        for url in urls:
            cur.execute(f"insert into current_urls(url) values ('{url}')")
        return self.get_current_urls_for_fetch_news()

    @staticmethod
    def normalize_news(news: dict):
        for key, value in news.items():
            if key in ["title", "description"]:
                news[key] = hazm.Normalizer().normalize(value)
        return news

    def insert_news(self, news):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        news = self.normalize_news(news)
        try:
            cur.execute(
                f"insert into news(id,description,title,updated_at,media_url,news_agency,link) "
                f"values('{news['id']}','{news['description']}','{news['title']}','{news['time']}','{news['media_url']}',"
                f"'{news['news_agency']}','{news['link']}') ")
        except Exception as e:
            pass

    def get_not_indexed_news(self):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        try:
            cur.execute("select * from news where indexed = false ")
            rows = cur.fetchall()
            return [{k: v for k, v in record.items()} for record in rows]
        except Exception as e:
            pass

    def get_indexed_news(self, _from, _limit, from_time, to_time):
        now = datetime.now()
        ft = now + timedelta(-1 * int(from_time))
        to = now + timedelta(-1 * int(to_time))
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute(
            f"select * from news where indexed = true and updated_at < '{ft}' and updated_at > '{to}' "
            f"ORDER BY updated_at DESC LIMIT {_limit} OFFSET {_from}")
        rows = cur.fetchall()
        return [{k: v for k, v in record.items()} for record in rows]

    def index_news(self, terms, news_id):
        try:
            cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
            for term in terms:
                cur.execute(f"insert into inverted_index(news_id,term) values ('{news_id}','{str(term).strip()}')")
            cur.execute(f"update news set indexed =true where id='{news_id}'")
        except Exception as e:
            print(str(e))

    def get_news(self, news_id, indexed=False):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        try:
            cur.execute(f"select * from news where id ='{news_id}' ")
            news = {key: value for key, value in cur.fetchone().items()}
            if indexed and not news["indexed"]:
                return None
            return news
        except Exception as e:
            print(str(e))

    def get_not_ranked_news_with_query_terms(self, query_terms: set):
        try:
            cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
            a = str(query_terms)[1:-1]
            query = "select distinct(news_id) from inverted_index where term in" + "(" + a + ")"
            cur.execute(query)
            result = []
            for item in cur.fetchall():
                if item["news_id"] is not None:
                    result.append(item["news_id"])
            return result
        except Exception as e:
            print(e)

    def visit_news(self, news_id):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute(f"update news set visit=visit+1 where id = '{news_id}' RETURNING visit")
        return {"visit": cur.fetchone()["visit"]}

    def get_most_visited_news(self):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute(f"select * from news where updated_at > now() -interval '1 day' "
                    f"order by visit DESC")
        all_news = []
        for news in cur.fetchall():
            all_news.append({key: value for key, value in news.items()})
        return all_news

    def clear_news(self):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute("delete from news")

    def clear_urls(self):
        cur: cursor = get_connection().cursor(cursor_factory=DictCursor)
        cur.execute("delete from current_urls")


if __name__ == '__main__':
    PR = PostgresRepository()
    pprint(PR.get_not_indexed_news())
