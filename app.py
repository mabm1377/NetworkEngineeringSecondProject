import uvicorn

from starlette.middleware.cors import CORSMiddleware
from postgers_repositoy import PostgresRepository
from search_engine import SearchEngine
from rss_crawler import RSSCrawler
from fastapi import FastAPI, Query
from typing import List, Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

postgres_repository = PostgresRepository()


@app.get("/set_urls")
def set_urls_for_fetch_pages(urls: Optional[List[str]] = Query(None)):
    if len(urls) > 0:
        postgres_repository.set_current_urls_for_fetch_news(urls)
    return {"msg": "آدرس ها با موفقیت ثبت شدند."}


@app.get("/get_news")
def get_indexed_news(_from: Optional[int] = Query(None, alias="from"),
                     _limit: Optional[str] = Query(None, alias="limit")):
    return postgres_repository.get_indexed_news(_from or 0, _limit or 10)


@app.get("/search")
def search(query: str):
    return SearchEngine.search(query)


@app.get("/visit")
def visit(news_id: str):
    return postgres_repository.visit_news(news_id)


@app.get("/most_visited")
def most_visited_list():
    return postgres_repository.get_most_visited_news()


if __name__ == '__main__':
    search_engine = SearchEngine()
    rss_crawler = RSSCrawler()
    search_engine.start()
    rss_crawler.start()
    uvicorn.run(app, host='0.0.0.0', port=5000)
    search_engine.join()
    rss_crawler.join()
