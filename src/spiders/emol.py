import logging
import math
from datetime import datetime

from classes.paper import Paper
from services.web_fetcher import WebFetcher
from utils.date_utils import DateUtils


class Emol:
    def __init__(self):
        self.SITE_NAME = "EMOL"
        self.BASE_URL = "https://newsapi.ecn.cl/NewsApi/emol/buscador/emol?"
        self.MAX_PAPERS = 250
        self.fetcher = WebFetcher(delay=10, max_concurrent=1)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run(self, start_date: datetime, end_date: datetime) -> list[Paper]:
        self.logger.info(f"Obteniendo noticias desde {self.SITE_NAME}...")

        total_papers = self.get_total_papers()
        start_paper = self.get_start_paper(start_date, 0, total_papers - 1)
        end_paper = self.get_end_paper(end_date, 0, start_paper)

        urls = self.generate_urls(start_paper, end_paper)
        all_papers = []
        for url in urls:
            papers = self.get_list_papers(url)
            all_papers.extend(filter(lambda p: (p is not None) and (p.date >= start_date and p.date <= end_date), papers))

        return all_papers

    def get_total_papers(self) -> int:
        data = self.fetcher.fetch_json(f"{self.BASE_URL}size=1&from=0")
        if data is None:
            return 0

        return data["hits"]["total"]

    def get_start_paper(self, start_date: datetime, start_paper: int, end_paper: int) -> int:
        if start_paper >= end_paper - 1:
            return end_paper

        mid_paper = math.floor((start_paper + end_paper) / 2)

        data = self.fetcher.fetch_json(f"{self.BASE_URL}size=1&from={mid_paper}")
        if data is None:
            return self.get_start_paper(start_date, start_paper + 1, end_paper)

        paper_date_str = data["hits"]["hits"][0]["_source"]["fechaPublicacion"].split("T")[0]
        paper_date = datetime.strptime(paper_date_str, "%Y-%m-%d")

        diff = DateUtils.diff_days(start_date, paper_date)
        if diff == 1:
            return mid_paper
        elif diff > 1:
            return self.get_start_paper(start_date, start_paper, mid_paper)
        else:
            return self.get_start_paper(start_date, mid_paper, end_paper)

    def get_end_paper(self, end_date: datetime, start_paper: int, end_paper: int) -> int:
        if start_paper >= end_paper - 1:
            return start_paper

        mid_paper = math.floor((start_paper + end_paper) / 2)

        data = self.fetcher.fetch_json(f"{self.BASE_URL}size=1&from={mid_paper}")
        if data is None:
            return self.get_end_paper(end_date, start_paper, end_paper - 1)

        paper_date_str = data["hits"]["hits"][0]["_source"]["fechaPublicacion"].split("T")[0]
        paper_date = datetime.strptime(paper_date_str, "%Y-%m-%d")

        diff = DateUtils.diff_days(end_date, paper_date)
        if diff == -1:
            return mid_paper
        elif diff < -1:
            return self.get_end_paper(end_date, mid_paper, end_paper)
        else:
            return self.get_end_paper(end_date, start_paper, mid_paper)

    def generate_urls(self, start_paper: int, end_paper: int) -> list[str]:
        urls = []
        for i in range(end_paper, start_paper, self.MAX_PAPERS):
            url = f"{self.BASE_URL}size={self.MAX_PAPERS}&from={i}"
            urls.append(url)

        return urls

    def get_list_papers(self, url: str) -> list[Paper]:
        data = self.fetcher.fetch_json(url, is_success=True)
        if data is None:
            return []

        papers = []
        hits = data["hits"]["hits"]
        for hit in hits:
            paper = Paper(self.SITE_NAME, hit["_source"]["permalink"])
            paper.set_emol_data(hit["_source"])
            papers.append(paper)

        return papers
