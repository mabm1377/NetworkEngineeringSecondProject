import hashlib
import requests
import time

from multiprocessing import Process
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from postgers_repositoy import PostgresRepository


class RSSCrawler(Process):
    postgres_repository = PostgresRepository()

    @staticmethod
    def prepare_url(url):
        # TODO
        return urljoin(url, "rss")

    def fetch_news(self, url):
        prepared_url = RSSCrawler.prepare_url(url)
        try:
            resp = requests.get(prepared_url)
            soup = BeautifulSoup(resp.content, features="xml")
            for item in soup.findAll('item'):
                media_url = None
                try:
                    media_url = item.enclosure.attrs["url"]
                except Exception as e:
                    print(e)
                news_item = {"title": item.title.text, "description": item.description.text, 'link': item.link.text,
                             'time': item.pubDate.text, "media_url": media_url}
                m = hashlib.sha256()
                m.update(news_item["link"].encode())
                a = m.hexdigest()
                hs_int = int(a, 16)
                news_item["id"] = str(hs_int)
                news_item["news_agency"] = urlparse(url).netloc
                self.postgres_repository.insert_news(news_item)
        except Exception as e:
            print(str(e))

    def run(self):
        while True:
            try:
                urls = self.postgres_repository.get_current_urls_for_fetch_news()
                for url in urls:
                    self.fetch_news(url)
                time.sleep(10)
            except Exception as e:
                print(str(e))


if __name__ == "__main__":
    rss_crawler = RSSCrawler()
    rss_crawler.start()
    rss_crawler.join()
    # PR = PostgresRepository()
    # url = "https://farsnews.ir/rss"
    # url = "https://www.isna.ir/rss"
    # url = "https://www.irna.ir/rss"
    # url = "https://www.mehrnews.com/rss"
    # url = "https://www.khabaronline.ir/rss"
    # url = "https://farsi.khamenei.ir/rss"
    # url = "http://dolat.ir/rss"
    # print(PR.get_current_urls_for_fetch_news())
    # urls = PR.set_current_urls_for_fetch_news(["https://www.mehrnews.com", "https://www.khabaronline.ir"])
    # rss_crawler = RSSCrawler()
    # for url in urls:
    #     rss_crawler.fetch_news(url)
