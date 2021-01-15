from abc import ABC, abstractmethod
from multiprocessing import Process
import hazm


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
