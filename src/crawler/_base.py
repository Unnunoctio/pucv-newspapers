from abc import ABC, abstractmethod
from typing import Any, Dict, List

from core.models import Article, DateRange, NewspaperType
from utils.logger import Logger


class BaseCrawler(ABC):
    """Base crawler"""

    def __init__(self, config: Dict[str, Any], date_range: DateRange):
        try:
            self.NAME = NewspaperType(config.get("name"))
            self.BASE_URLS = config.get("base_urls")
        except ValueError:
            raise ValueError("Invalid crawler main configuration")

        self.date_range = date_range

    async def crawl(self) -> List[Article]:
        """Crawl the newspaper"""
        Logger.info(prefix="SPIDER", message=f" Obteniendo noticias de {self.NAME.value}")

        all_pages = []

        for base_url in self.BASE_URLS:
            pages = self.generate_pages(base_url)
            all_pages.extend(pages)
        
        print(len(all_pages))
        articles = await self.get_articles(pages)

        return articles

    @abstractmethod
    def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""
        pass

    @abstractmethod
    async def get_articles(self, pages: List[str]) -> List[Article]:
        """Get the list of articles from the pages"""
        pass
