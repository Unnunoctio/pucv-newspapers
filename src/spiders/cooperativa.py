import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup

from classes.paper import Paper
# from services.web_fetcher import WebFetcher
from services.WebFetcherV2 import WebFetcherV2


class Cooperativa:
    def __init__(self):
        self.SITE_NAME = "COOPERATIVA"
        self.BASE_URL = "https://www.cooperativa.cl"
        self.PAGE_BASE_URL = "https://www.cooperativa.cl/noticias/site/cache/nroedic/todas/"
        # self.fetcher = WebFetcher(delay=5, max_concurrent=10)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")

        pages = self.generate_pages(fetcher, start_date, end_date)
        all_papers = []
        async with aiohttp.ClientSession() as session:
            block_urls = await self.async_get_papers_urls(session, pages)
            urls = [item for sublist in block_urls for item in sublist]

            papers = await self.async_get_papers(session, urls)
            all_papers.extend(filter(lambda p: (p is not None) and (p.date >= start_date and p.date <= end_date), papers))

        return all_papers

    def generate_pages(self, fetcher:  start_date: datetime, end_date: datetime) -> list[str]:
        pages = []
        i_date = start_date
        while i_date <= end_date:
            date_formatted = i_date.strftime("%Y%m%d")
            pages.append(f"{self.PAGE_BASE_URL}{date_formatted}.html")
            i_date += timedelta(days=1)

        return pages

    async def async_get_papers_urls(self, session: aiohttp.ClientSession, pages: list[str]) -> list[list[str]]:
        tasks = [self.async_get_paper_urls(session, page) for page in pages]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper_urls(self, session: aiohttp.ClientSession, page: str) -> list[str]:
        body = await self.fetcher.async_fetch_page(session, page)
        if body is None:
            return []

        soup = BeautifulSoup(body, "html.parser")

        links = soup.select(".art-todas a")
        if len(links) == 0:
            links = soup.select(".tdd .bloque-tit-fh h2 a")
        urls = set()
        for elem in links:
            paper_url = elem.get("href")
            if paper_url is not None:
                url = f"{self.BASE_URL}{paper_url}"
                urls.add(url)

        return list(urls)

    async def async_get_papers(self, session: aiohttp.ClientSession, urls: list[str]) -> list[Paper]:
        tasks = [self.async_get_paper(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper(self, session: aiohttp.ClientSession, url: str) -> Paper | None:
        body = await self.fetcher.async_fetch_page(session, url, is_success=True)
        if body is None:
            return None

        try:
            paper = Paper(self.SITE_NAME, url)
            paper.set_cooperativa_data(body)
            return paper
        except Exception as e:
            self.logger.error("Error al procesar el paper: " + url + "\n" + str(e))
            return None
