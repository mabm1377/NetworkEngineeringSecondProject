from news_agency_base_crawler import NewsAgencyBaseCrawler
from bs4 import BeautifulSoup
from urllib import request
from bs4.element import Doctype, NavigableString, Tag
import re
import hazm

class FarsNewsCrawler(NewsAgencyBaseCrawler):
    def __init__(self, url="https://www.farsnews.ir/"):
        super().__init__(url)

    def fetch_urls(self):
        page = request.urlopen(self.url)
        soup = BeautifulSoup(page)
        news_links = []
        url_pattern = r'https?:\/\/?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        for link in soup.findAll('link'):
            if link.get("type") == "application/rss+xml":
                rss_page = request.urlopen(link.get("href"))
                rss_soup = BeautifulSoup(rss_page)
                for news_link in re.findall(url_pattern, rss_soup.text):
                    if str(news_link).startswith("/news"):
                        news_links.append(str(news_link))
        self.current_links = news_links

    def fetch_pages(self):
        for link in self.current_links:
            f_link = self.url+link
            print(f_link)
            page = request.urlopen(self.url+link)
            soup = BeautifulSoup(page)
            normalizer = hazm.Normalizer()
            l = normalizer.normalize(soup.text)
            print("---------------------------------------------------------------------")

    def crawl(self):
        pass


if __name__ == "__main__":
    crawler = FarsNewsCrawler()
    crawler.fetch_urls()
    crawler.fetch_pages()
    # for link in links:
    #     print(link)
    # crawler.fetch_pages(links)
