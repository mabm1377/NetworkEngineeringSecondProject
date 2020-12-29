from bs4 import BeautifulSoup
from urllib import request
import re
import xml.etree.ElementTree as ET

url = "https://www.farsnews.ir/"
page = request.urlopen(url)
soup = BeautifulSoup(page)
for link in soup.findAll('link'):
    if link.get("type") == "application/rss+xml":
        rss_page = request.urlopen(link.get("href"))
        rss_soup = BeautifulSoup(rss_page)
        root = ET.fromstring(rss_soup.prettify())
        for child in root:
            print(child.attrib)
        # print(type(rss_soup.prettify()))

# print(soup.prettify())
