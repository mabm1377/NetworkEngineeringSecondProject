import time
from multiprocessing import Process

from postgers_repositoy import PostgresRepository


class SearchEngine(Process):
    postgres_repository = PostgresRepository()

    @classmethod
    def calculate_tf_idf(cls, query_terms, news_id):
        news = cls.postgres_repository.get_news(news_id, True)
        title_terms = str(news["title"]).split(" ")
        tf = 0
        for i, body_term in enumerate(title_terms):
            if query_terms[0] == body_term:
                k = 0
                for query_term in query_terms:
                    if query_term != title_terms[i + k]:
                        break
                    k += 1
                else:
                    tf += 1
        tf_idf = tf / len(title_terms)
        if tf_idf > 0:
            return tf_idf, news
        else:
            return tf_idf, None

    @classmethod
    def search(cls, query: str):
        query_terms = set(query.split(" "))
        news_ids = cls.postgres_repository.get_not_ranked_news_with_query_terms(query_terms)
        ranked_news = []
        for news_id in news_ids:
            tf_idf, news = cls.calculate_tf_idf(query.split(" "), news_id)
            if news is not None:
                ranked_news.append({"news_id": news_id, "tf_idf": tf_idf, "news": news})
        ranked_news.sort(key=lambda x: x.get("tf_idf"), reverse=True)
        return [news["news"] for news in ranked_news[0:10]]

    def index(self):
        not_indexed_news = self.postgres_repository.get_not_indexed_news()
        for news in not_indexed_news:
            terms = str(news["title"]).split(" ")
            self.postgres_repository.index_news(terms=terms, news_id=news['id'])

    def run(self):
        while True:
            self.index()
            time.sleep(10)


if __name__ == '__main__':
    se = SearchEngine()
    se.start()
    se.join()
