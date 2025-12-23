from abc import ABC, abstractmethod
from typing import Any, Dict, List

from html2text import HTML2Text

from core.models import Article, DateRange, NewspaperType
from utils.logger import Logger


class BaseCrawler(ABC):
    """Base crawler"""

    def __init__(self, config: Dict[str, Any], date_range: DateRange):
        try:
            self.NAME = NewspaperType(config.get("name"))
            self.BASE_URLS = config.get("base_urls")
            self.REQUESTS_CONFIG = config.get("requests_config")
        except ValueError as e:
            raise ValueError("Invalid crawler main configuration: " + str(e))

        self.date_range = date_range

        # Configure HTML parser
        self.HTML_PARSER = HTML2Text()
        self.HTML_PARSER.ignore_links = True
        self.HTML_PARSER.ignore_images = True
        self.HTML_PARSER.body_width = 0
        self.HTML_PARSER.skip_internal_links = True
        self.HTML_PARSER.unicode_snob = True

        # Desactive a Markdown format
        self.HTML_PARSER.bold = False
        self.HTML_PARSER.italic = False
        self.HTML_PARSER.underline = False
        self.HTML_PARSER.mark_code = False
        self.HTML_PARSER.ignore_emphasis = True
        self.HTML_PARSER.single_line_break = True

    async def crawl(self) -> List[Article]:
        """Crawl the newspaper"""
        Logger.info(prefix="SPIDER", message=f"Obteniendo noticias de {self.NAME.value}")

        all_pages = []

        for base_url in self.BASE_URLS:
            pages = await self.generate_pages(base_url)
            all_pages.extend(pages)

        articles = await self.get_articles(all_pages)

        return articles

    @abstractmethod
    async def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""
        pass

    @abstractmethod
    async def get_articles(self, pages: List[str]) -> List[Article]:
        """Get the list of articles from the pages"""
        pass
