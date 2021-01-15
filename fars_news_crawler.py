import json
import datetime
import re
import time
from news_agency_base_crawler import NewsAgencyBaseCrawler
from bs4 import BeautifulSoup
from urllib import request
from bs4.element import Tag
from utils import save_news, calculate_tf_idf


class FarsNewsCrawler(NewsAgencyBaseCrawler):
    def __init__(self, url="https://www.farsnews.ir/"):
        super().__init__(url)

    def fetch_urls(self):
        page = request.urlopen(self.url)
        soup = BeautifulSoup(page)
        url_pattern = r'https?:\/\/?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        for link in soup.findAll('link'):
            if link.get("type") == "application/rss+xml":
                rss_page = request.urlopen(link.get("href"))
                rss_soup = BeautifulSoup(rss_page)
                for news_link in re.findall(url_pattern, rss_soup.text):
                    if str(news_link).startswith("/news"):
                        self.current_links.append(str(news_link))

    def fetch_pages(self):
        for link in self.current_links:
            try:
                page = request.urlopen(self.url + link)
                soup = BeautifulSoup(page)
                body = max(self.normalizer.normalize(soup.findAll("main")[0].text).split("\n\n"), key=len)
                head = self.normalizer.normalize(soup.findAll("head")[0].text)
                new_news = {"body": body, "title": head, "news_agency": "fars_news"}
                for content in soup.contents:
                    if isinstance(content, Tag):
                        for content2 in content.contents:
                            if isinstance(content2, Tag):
                                for content3 in content2.contents:
                                    if isinstance(content3, Tag):
                                        if content3.attrs.get("name") == "dc.Date":
                                            str_time = content3.attrs.get("content")
                                            am_or_pm = str(str_time).split(" ")[-1]
                                            new_news.update({"time": time.mktime(datetime.datetime.strptime(
                                                content3.attrs.get("content"),
                                                '%m/%d/%Y %H:%M:%S ' + am_or_pm).timetuple())})
                                        if content3.attrs.get("name") == 'thumbnail':
                                            new_news.update({"img": content3.attrs.get("content")})
                new_news.update({"link": str(self.url + link)})
                new_news.update({"id": str(hash(new_news['link']))})
                self.current_pages.append(new_news)
            except Exception as e:
                print(str(e))
        self.current_links = []

    def run(self):
        while True:
            self.fetch_urls()
            self.fetch_pages()
            for news in self.current_pages:
                save_news(news)


if __name__ == "__main__":
    crawler = FarsNewsCrawler()
    crawler.fetch_urls()
    crawler.fetch_pages()
    for page in crawler.current_pages:
        save_news(page)
    # for
    # calculate_tf_idf(news_id=page['id'], news=page['body'])

    # for link in links:
    #     print(link)
    # crawler.fetch_pages(links)
