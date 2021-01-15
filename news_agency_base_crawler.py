from abc import ABC, abstractmethod
from multiprocessing import Process
import hazm
from utils import save_news, invert_index
import time


class NewsAgencyBaseCrawler(ABC, Process):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.current_links = []
        self.current_pages = []
        self.normalizer = hazm.Normalizer()

    @abstractmethod
    def fetch_urls(self):
        pass

    @abstractmethod
    def fetch_pages(self):
        pass

    def run(self):
        while True:
            self.fetch_urls()
            self.fetch_pages()
            for news in self.current_pages:
                try:
                    save_news(news)
                    invert_index(news)
                except Exception as e:
                    print(e)
            time.sleep(3600)

