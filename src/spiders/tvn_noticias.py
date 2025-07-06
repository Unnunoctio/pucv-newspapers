import asyncio
import logging
import time
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from classes.paper import Paper
from services.web_fetcher import WebFetcher


class TvnNoticias:
    def __init__(self):
        self.SITE_NAME = "TVN_NOTICIAS"
        self.BASE_URL = "https://www.tvn.cl/noticias"
        self.PAPER_BASE_URL = "https://www.tvn.cl"
        self.fetcher = WebFetcher(delay=5, max_concurrent=10)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")
        start_time = time.time()

        total_pages = self.get_total_pages()
        pages = self.generate_pages(1, total_pages)
        pages.reverse()

        all_papers = []
        async with aiohttp.ClientSession() as session:
            block_urls = await self.async_get_papers_urls(session, pages)
            urls = [item for sublist in block_urls for item in sublist]

            papers = await self.async_get_papers(session, urls)
            all_papers.extend(filter(lambda p: p is not None, papers))

        end_time = time.time()
        self.logger.info(f"{self.SITE_NAME}: {end_time - start_time} segundos")
        return all_papers

    def get_total_pages(self) -> int:
        body = self.fetcher.fetch_page(f"{self.BASE_URL}/p/1")
        if body is None:
            return 0

        soup = BeautifulSoup(body, "html.parser")
        page_items = soup.select(".auxi .wp-pagenavi a")

        last_page_url = page_items[-1].get("href")
        return int(last_page_url.split("/")[3])

    def generate_pages(self, start_page: int, end_page: int) -> list[str]:
        return [f"{self.BASE_URL}/p/{page}/" for page in range(start_page, end_page + 1)]

    async def async_get_papers_urls(self, session: aiohttp.ClientSession, pages: list[str]) -> list[list[str]]:
        tasks = [self.async_get_paper_urls(session, page) for page in pages]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper_urls(self, session: aiohttp.ClientSession, page: str) -> list[str]:
        body = await self.fetcher.async_fetch_page(session, page)
        if body is None:
            return []

        soup = BeautifulSoup(body, "html.parser")

        links = soup.select(".auxi .row article a")
        urls = set()
        for elem in links:
            paper_url = elem.get("href")
            if paper_url is not None:
                url = f"{self.PAPER_BASE_URL}{paper_url}"
                urls.add(url)

        return list(urls)

    async def async_get_papers(self, session: aiohttp.ClientSession, urls: list[str]) -> list[Paper]:
        tasks = [self.async_get_paper(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper(self, session: aiohttp.ClientSession, url: str) -> Paper | None:
        body = await self.fetcher.async_fetch_page(session, url, is_success=True)
        if body is None:
            return None

        paper = Paper(self.SITE_NAME, url)
        paper.set_tvn_data(body)
        return paper
