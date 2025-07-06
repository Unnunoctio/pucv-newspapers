import logging
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from classes.paper import Paper
from services.web_fetcher import WebFetcher


class Cooperativa:
    def __init__(self):
        self.SITE_NAME = "COOPERATIVA"
        self.BASE_URL = "https://www.cooperativa.cl"
        self.PAGE_BASE_URL = "https://www.cooperativa.cl/noticias/site/cache/nroedic/todas/"
        self.SLEEP = 5000
        self.fetcher = WebFetcher(delay=self.SLEEP)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    def run(self, start_date: datetime, end_date: datetime) -> None:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")
        start_time = time.time()

        pages = self.generate_pages(start_date, end_date)
        all_papers = []
        for page in pages:
            date_string = page.split("/")[-1].split(".")[0]
            date = datetime.strptime(date_string, "%Y%m%d")

            urls = self.get_paper_urls(page)
            urls.reverse()

            papers = [self.get_paper(url, date) for url in urls]
            all_papers.extend(filter(lambda p: p is not None, papers))

        end_time = time.time()
        self.logger.info(f"{self.SITE_NAME}: {end_time - start_time} segundos")
        return all_papers

    def generate_pages(self, start_date: datetime, end_date: datetime) -> list[str]:
        pages = []
        i_date = start_date
        while i_date <= end_date:
            date_formatted = i_date.strftime("%Y%m%d")
            pages.append(f"{self.PAGE_BASE_URL}{date_formatted}.html")
            i_date += timedelta(days=1)

        return pages

    def get_paper_urls(self, page: str) -> list[str]:
        body = self.fetcher.fetch_page(page)
        if body is None:
            return []

        soup = BeautifulSoup(body, "html.parser")

        links = soup.select(".art-todas a")
        urls = set()
        for elem in links:
            page_url = elem.get("href")
            if page_url is not None:
                url = f"{self.BASE_URL}{page_url}"
                urls.add(url)

        return list(urls)

    def get_paper(self, url: str, date: datetime) -> Paper | None:
        body = self.fetcher.fetch_page(url, is_success=True)
        if body is None:
            return None
        
        paper = Paper(self.SITE_NAME, url)
        paper.set_cooperativa_data(body, date)
        return paper
