import asyncio
import logging
import math
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from classes.paper import Paper
from services.web_fetcher import WebFetcher
from utils.date_utils import DateUtils


class ADNRadio:
    def __init__(self):
        self.SITE_NAME = "ADN_RADIO"
        self.BASE_URL = "https://www.adnradio.cl/noticias/"
        self.TOTAL_PAGES = 400
        self.fetcher = WebFetcher(delay=5, max_concurrent=10)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")

        start_page = self.get_start_page(start_date, 0, self.TOTAL_PAGES)

        print(start_page)

        return []
    

    def get_start_page(self, start_date: datetime, start_page: int, end_page: int) -> int:
        if start_page >= end_page - 1:
            return end_page

        mid_page = math.floor((start_page + end_page) / 2)
        
        print(f"{start_page} - {end_page} -> {mid_page}")

        body = self.fetcher.fetch_page(f"{self.BASE_URL}?page={mid_page}")
        if body is None:
            return self.get_start_page(start_date, start_page + 1, end_page)

        soup = BeautifulSoup(body, "html.parser")
        print(soup.prettify())
        return 0

        page_items = soup.select("div.p-stk div.s-1-2 article.sc")

        if len(page_items) == 0:
            return self.get_start_page(start_date, start_page, end_page - 1)

        # DATE (dd-mm-yyyy) (Hoy) (Ayer) (Otro)
        last_paper_date_str = page_items[-1].select("div.c-bln p")[-1].get_text(strip=True)
        if last_paper_date_str == "Hoy":
            last_paper_date = datetime.now()
        elif last_paper_date_str == "Ayer":
            last_paper_date = datetime.now() - timedelta(days=1)
        else:
            try:
                last_paper_date = datetime.strptime(last_paper_date_str, "%d-%m-%Y")
            except Exception:
                last_paper_date = datetime.now() - timedelta(days=2)
        
        diff = DateUtils.diff_days(start_date, last_paper_date)
        if diff == 1:
            return mid_page
        elif diff > 1:
            return self.get_start_page(start_date, start_page, mid_page)
        else:
            return self.get_start_page(start_date, mid_page, end_page)