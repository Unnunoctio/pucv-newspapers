import re
from datetime import timedelta
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from crawlers.generics.static_website import StaticWebsiteCrawler


class CooperativaCrawler(StaticWebsiteCrawler):
    """Crawler custom to TVN"""

    def __init__(self, config, date_range):
        super().__init__(config, date_range)

    # TODO: GENERATE PAGES
    async def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""
        pages = []

        i_date = self.date_range.start_date
        while i_date <= self.date_range.end_date:
            date_formatted = i_date.strftime("%Y%m%d")

            page_url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
            page_url = re.sub(r"\(\\d\+\)", date_formatted, page_url)
            pages.append(page_url)

            i_date += timedelta(days=1)

        return pages

    # TODO: ENCAPSULATION OF GET DATA FROM HTML
    def _get_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        date_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("date").get("selectors"))
        if date_elem is not None:
            date_str = date_elem.get_text(strip=True)
            date_split = date_str.split(" ")

            months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            day = int(date_split[1])
            month = months.index(date_split[3].lower()) + 1
            year = int(date_split[6])

            return datetime(year, month, day)

        return None
    
    def _get_tag(self, soup: BeautifulSoup) -> Optional[str]:
        tag_elem = self._get_html_elem(soup, self.ARTICLE_CONFIG.get("tag").get("selectors"))
        if tag_elem is not None:
            return tag_elem.get_text(strip=True)
        
        canonical_link = soup.select_one("link[rel=canonical]")
        if canonical_link is not None:
            url_split = canonical_link.get("href").split("/")
            if len(url_split) > 4:
                return url_split[4]

        return None