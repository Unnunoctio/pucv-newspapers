import re
from datetime import timedelta
from typing import List

from crawler.static_website import StaticWebsiteCrawler


class CooperativaCrawler(StaticWebsiteCrawler):
    """Crawler custom to TVN"""

    def __init__(self, config, date_range):
        super().__init__(config, date_range)

    def generate_pages(self, base_url: str) -> List[str]:
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
    
