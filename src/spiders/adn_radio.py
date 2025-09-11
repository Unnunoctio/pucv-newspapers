import logging
import math
from datetime import datetime, timedelta

from playwright.async_api import async_playwright

from classes.paper import Paper
from utils.date_utils import DateUtils


class ADNRadio:
    def __init__(self):
        self.SITE_NAME = "ADN_RADIO"
        self.BASE_URL = "https://www.adnradio.cl/noticias/"
        self.TOTAL_PAGES = 398

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            start_page = await self.get_start_page(page, start_date, 0, self.TOTAL_PAGES)
            end_page = await self.get_end_page(page, end_date, 0, start_page)

            url_pages = self.generate_pages(start_page, end_page)
            url_pages.reverse()

            all_papers_urls = []
            for url_page in url_pages:
                all_papers_urls.extend(await self.get_paper_urls(page, url_page))

            all_papers = []
            for paper_url in all_papers_urls:
                paper = await self.get_paper(page, paper_url)
                if paper is not None:
                    if paper.date is not None:
                        if paper.date >= start_date and paper.date <= end_date:
                            all_papers.append(paper)
                    else:
                        print(f"No se pudo obtener la fecha del paper: {paper_url}")

            await browser.close()

        return all_papers

    async def get_start_page(self, page, start_date: datetime, start_page: int, end_page: int) -> int:
        if start_page >= end_page - 1:
            return end_page

        mid_page = math.floor((start_page + end_page) / 2)

        await page.goto(f"{self.BASE_URL}{mid_page}/")
        await page.wait_for_load_state("load")

        page_items = await page.query_selector_all("section.c-cad.cho-3 article")
        if len(page_items) == 0 or page_items is None:
            return await self.get_start_page(page, start_date, start_page + 1, end_page)

        # DATE (dd-mm-yyyy) (Hoy) (Ayer) (Otro)
        last_paper_date_elem = await page_items[-1].query_selector("div.c-bln p:nth-child(2)")
        last_paper_date_str = await last_paper_date_elem.inner_text()
        if last_paper_date_str == "Hoy":
            last_paper_date = datetime.now()
        elif last_paper_date_str == "Ayer":
            last_paper_date = datetime.now() - timedelta(days=1)
        else:
            try:
                last_paper_date = datetime.strptime(last_paper_date_str, "%d/%m/%Y")
            except Exception:
                last_paper_date = datetime.now() - timedelta(days=2)

        diff = DateUtils.diff_days(start_date, last_paper_date)
        if diff == 1:
            return mid_page
        elif diff > 1:
            return await self.get_start_page(page, start_date, start_page, mid_page)
        else:
            return await self.get_start_page(page, start_date, mid_page, end_page)

    async def get_end_page(self, page, end_date: datetime, start_page: int, end_page: int) -> int:
        if start_page >= end_page - 1:
            return start_page

        mid_page = math.floor((start_page + end_page) / 2)

        await page.goto(f"{self.BASE_URL}{mid_page}/")
        await page.wait_for_load_state("load")

        page_items = await page.query_selector_all("section.c-cad.cho-3 article")
        if len(page_items) == 0 or page_items is None:
            return await self.get_end_page(page, end_date, start_page, end_page - 1)

        # DATE (dd-mm-yyyy) (Hoy) (Ayer) (Otro)
        last_paper_date_elem = await page_items[-1].query_selector("div.c-bln p:nth-child(2)")
        last_paper_date_str = await last_paper_date_elem.inner_text()
        if last_paper_date_str == "Hoy":
            last_paper_date = datetime.now()
        elif last_paper_date_str == "Ayer":
            last_paper_date = datetime.now() - timedelta(days=1)
        else:
            try:
                last_paper_date = datetime.strptime(last_paper_date_str, "%d/%m/%Y")
            except Exception:
                last_paper_date = datetime.now() - timedelta(days=2)

        diff = DateUtils.diff_days(end_date, last_paper_date)
        if diff == -1:
            return mid_page
        elif diff < -1:
            return await self.get_end_page(page, end_date, mid_page, end_page)
        else:
            return await self.get_end_page(page, end_date, start_page, mid_page)

    def generate_pages(self, start_page: int, end_page: int) -> list[str]:
        return [f"{self.BASE_URL}{page}/" for page in range(end_page, start_page + 1)]

    async def get_paper_urls(self, page, url_page: str) -> list[str]:
        await page.goto(url_page)
        await page.wait_for_load_state("load")

        items = await page.query_selector_all("section.c-cad.cho-3 article")
        if len(items) == 0 or items is None:
            return []

        urls = set()
        for item in items:
            item_url_elem = await item.query_selector("a")
            if item_url_elem is not None:
                item_url = await item_url_elem.get_attribute("href")
                if item_url is not None:
                    urls.add(f"https://www.adnradio.cl{item_url}")

        return list(urls)

    async def get_paper(self, page, url_paper: str) -> Paper | None:
        try:
            await page.goto(url_paper)
            await page.wait_for_load_state("load")
        except Exception as e:
            self.logger.error("Error al procesar el paper: " + url_paper + "\n" + str(e))
            return None

        try:
            paper = Paper(self.SITE_NAME, url_paper)
            await paper.set_adn_radio_data(page)
            return paper
        except Exception as e:
            self.logger.error("Error al procesar el paper: " + url_paper + "\n" + str(e))
            return None
