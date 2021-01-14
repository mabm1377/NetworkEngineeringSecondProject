from abc import ABC, abstractmethod


class NewsAgencyBaseCrawler(ABC):
    def __init__(self, url):
        self.url = url
        self.current_links = []

    @abstractmethod
    def fetch_urls(self):
        pass

    @abstractmethod
    def fetch_pages(self):
        pass

    @abstractmethod
    def crawl(self):
        pass


