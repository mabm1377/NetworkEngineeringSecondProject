from bs4 import BeautifulSoup
from urllib import request
import re

url = "https://www.farsnews.ir/"
page = request.urlopen(url)
soup = BeautifulSoup(page)
for link in soup.findAll('link'):
    if link.get("type") == "application/rss+xml":
        print(link)

# print(soup.prettify())
