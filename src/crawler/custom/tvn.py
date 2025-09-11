import re
from typing import List

from crawler.static_website import StaticWebsiteCrawler


class TVNCrawler(StaticWebsiteCrawler):
    """Crawler custom to TVN"""

    def __init__(self, config, date_range):
        super().__init__(config, date_range)

    def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""

        total_pages = self._get_total_pages(base_url)

        pages = []
        for i in range(1, total_pages + 1):
            page_url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
            page_url = re.sub(r"\(\\d\+\)", str(i), page_url)
            pages.append(page_url)

        return pages[::-1]
