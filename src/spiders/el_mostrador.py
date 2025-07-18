import asyncio
import logging
import math
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from classes.paper import Paper
from services.web_fetcher import WebFetcher
from utils.date_utils import DateUtils


class ElMostrador:
    def __init__(self):
        self.SITE_NAME = "EL_MOSTRADOR"
        self.BASE_URL = "https://www.elmostrador.cl/categoria/dia/"
        self.fetcher = WebFetcher(delay=5, max_concurrent=10)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")

        total_pages = self.get_total_pages()
        start_page = self.get_start_page(start_date, 1, total_pages)
        end_page = self.get_end_page(end_date, 1, start_page)

        pages = self.generate_pages(start_page, end_page)
        pages.reverse()

        all_papers = []
        async with aiohttp.ClientSession() as session:
            block_urls = await self.async_get_papers_urls(session, pages)
            urls = [item for sublist in block_urls for item in sublist]

            papers = await self.async_get_papers(session, urls)
            all_papers.extend(filter(lambda p: (p is not None) and (p.date >= start_date and p.date <= end_date), papers))

        return all_papers

    def get_total_pages(self) -> int:
        body = self.fetcher.fetch_page(f"{self.BASE_URL}")
        if body is None:
            return 0

        soup = BeautifulSoup(body, "html.parser")

        page_items = soup.select(".the-pagination .the-pagination__item")
        last_page_url = page_items[-1].get("href")
        return int(last_page_url.split("/")[6])

    def get_start_page(self, start_date: datetime, start_page: int, end_page: int) -> int:
        if start_page >= end_page - 1:
            return end_page

        mid_page = math.floor((start_page + end_page) / 2)

        body = self.fetcher.fetch_page(f"{self.BASE_URL}page/{mid_page}/")
        if body is None:
            return self.get_start_page(start_date, start_page + 1, end_page)

        soup = BeautifulSoup(body, "html.parser")
        page_items = soup.select(".d-section__body .d-tag-card .d-tag-card__date")
        # DATE (dd-mm-yyyy)
        last_paper_time = page_items[-1].get("datetime")
        last_paper_date = datetime.strptime(last_paper_time, "%d-%m-%Y")

        diff = DateUtils.diff_days(start_date, last_paper_date)
        if diff == 1:
            return mid_page
        elif diff > 1:
            return self.get_start_page(start_date, start_page, mid_page)
        else:
            return self.get_start_page(start_date, mid_page, end_page)

    def get_end_page(self, end_date: datetime, start_page: int, end_page: int) -> int:
        if start_page >= end_page - 1:
            return start_page

        mid_page = math.floor((start_page + end_page) / 2)

        body = self.fetcher.fetch_page(f"{self.BASE_URL}page/{mid_page}/")
        if body is None:
            return self.get_end_page(end_date, start_page, end_page - 1)

        soup = BeautifulSoup(body, "html.parser")
        page_items = soup.select(".d-section__body .d-tag-card .d-tag-card__date")
        # DATE (dd-mm-yyyy)
        last_paper_time = page_items[-1].get("datetime")
        last_paper_date = datetime.strptime(last_paper_time, "%d-%m-%Y")

        diff = DateUtils.diff_days(end_date, last_paper_date)
        if diff == -1:
            return mid_page
        elif diff < -1:
            return self.get_end_page(end_date, mid_page, end_page)
        else:
            return self.get_end_page(end_date, start_page, mid_page)

    def generate_pages(self, start_page: int, end_page: int) -> list[str]:
        return [f"{self.BASE_URL}page/{page}/" for page in range(end_page, start_page + 1)]

    async def async_get_papers_urls(self, session: aiohttp.ClientSession, pages: list[str]) -> list[list[str]]:
        tasks = [self.async_get_paper_urls(session, page) for page in pages]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper_urls(self, session: aiohttp.ClientSession, page: str) -> list[str]:
        body = await self.fetcher.async_fetch_page(session, page)
        if body is None:
            return []

        soup = BeautifulSoup(body, "html.parser")

        links = soup.select(".d-section__body .d-tag-card__title .d-tag-card__permalink")
        urls = set()
        for elem in links:
            paper_url = elem.get("href")
            if paper_url is not None:
                urls.add(paper_url)

        return list(urls)

    async def async_get_papers(self, session: aiohttp.ClientSession, urls: list[str]) -> list[Paper]:
        tasks = [self.async_get_paper(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def async_get_paper(self, session: aiohttp.ClientSession, url: str) -> Paper | None:
        body = await self.fetcher.async_fetch_page(session, url, is_success=True)
        if body is None:
            return None

        paper = Paper(self.SITE_NAME, url)
        paper.set_el_mostrador_data(body)
        return paper
