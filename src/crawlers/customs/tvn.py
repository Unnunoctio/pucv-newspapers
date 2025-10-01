import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from crawlers.generics.static_website import StaticWebsiteCrawler


class TVNCrawler(StaticWebsiteCrawler):
    """Crawler custom to TVN"""

    def __init__(self, config, date_range):
        super().__init__(config, date_range)

    # TODO: GENERATE PAGES
    async def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""
        total_pages = await self._get_total_pages(base_url)

        pages = []
        for i in range(1, total_pages + 1):
            page_url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
            page_url = re.sub(r"\(\\d\+\)", str(i), page_url)
            pages.append(page_url)

        return pages[::-1]

    # TODO: ENCAPSULATION OF GET DATA FROM HTML
    def _get_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        date_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("date").get("selectors"))
        if date_elem is not None:
            date_str = date_elem.get_text(strip=True)
            date_split = date_str.split(" ")

            months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            day = int(date_split[1])
            month = months.index(date_split[3].lower()) + 1
            year = int(date_split[5])

            return datetime(year, month, day)

        return None
