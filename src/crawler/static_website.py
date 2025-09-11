import asyncio
import math
import re
from datetime import datetime
from typing import List

from scrapling.fetchers import AsyncFetcher, Fetcher

from core.models import Article, DateRange
from crawler._base import BaseCrawler
from utils.date_utils import DateUtils


class StaticWebsiteCrawler(BaseCrawler):
    """Crawler for static websites"""

    def __init__(self, config: dict, date_range: DateRange):
        super().__init__(config, date_range)
        self.PAGES_CONFIG = config.get("pages_config")
        self.ARTICLES_LIST_CONFIG = config.get("articles_list_config")

    def generate_pages(self, base_url: str) -> List[str]:
        """Generate the list of pages to crawl"""

        total_pages = self._get_total_pages(base_url)

        start_page = self._get_start_page(base_url, self.date_range.start_date, 1, total_pages)
        end_page = self._get_end_page(base_url, self.date_range.end_date, 1, start_page)

        pages = []
        for i in range(end_page, start_page + 1):
            page_url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
            page_url = re.sub(r"\(\\d\+\)", str(i), page_url)
            pages.append(page_url)

        return pages[::-1]

    def _get_total_pages(self, base_url: str) -> int:
        """Get the total number of pages"""

        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(1), url)

        page = Fetcher.get(url)
        if page is None:
            return 0

        pagination_config = self.PAGES_CONFIG.get("pagination")

        page_items = page.css(pagination_config.get("selector"))
        last_item_url = page_items[pagination_config.get("pos_pagination_item")].attrib["href"]
        if pagination_config.get("split_href") is not None:
            return int(last_item_url.split(pagination_config.get("split_href"))[pagination_config.get("pos_href")])

        return int(last_item_url.split("/")[pagination_config.get("pos_href")])

    def _get_start_page(self, base_url: str, start_date: datetime, start_page: int, end_page: int) -> int:
        """Get the start page to crawl"""
        if start_page >= end_page - 1:
            return end_page

        mid_page = math.floor((start_page + end_page) / 2)

        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(mid_page), url)

        page = Fetcher.get(url)
        if page is None:
            return self._get_start_page(base_url, start_page, start_page + 1, end_page)

        datetime_config = self.ARTICLES_LIST_CONFIG.get("datetime")

        articles_items = page.css(self.ARTICLES_LIST_CONFIG.get("selector"))
        last_article_date_item = articles_items[-1].css_first(datetime_config.get("selector"))

        if datetime_config.get("attribute") is not None:
            last_article_date_str = last_article_date_item.attrib[datetime_config.get("attribute")]
        else:
            last_article_date_str = last_article_date_item.text

        last_article_date = datetime.strptime(last_article_date_str, datetime_config.get("format"))

        diff = DateUtils.diff_days(start_date, last_article_date)
        if diff == 1:
            return mid_page
        elif diff > 1:
            return self._get_start_page(base_url, start_date, start_page, mid_page)
        else:
            return self._get_start_page(base_url, start_date, mid_page, end_page)

    def _get_end_page(self, base_url: str, end_date: datetime, start_page: int, end_page: int) -> int:
        """Get the end page to crawl"""
        if start_page >= end_page - 1:
            return start_page

        mid_page = math.floor((start_page + end_page) / 2)

        url = re.sub(r"\(\\s\+\)", base_url, self.PAGES_CONFIG.get("url_pattern"))
        url = re.sub(r"\(\\d\+\)", str(mid_page), url)

        page = Fetcher.get(url)
        if page is None:
            return self._get_end_page(base_url, start_page, start_page, end_page - 1)

        datetime_config = self.ARTICLES_LIST_CONFIG.get("datetime")

        articles_items = page.css(self.ARTICLES_LIST_CONFIG.get("selector"))
        last_article_date_item = articles_items[-1].css_first(datetime_config.get("selector"))
        if datetime_config.get("attribute") is not None:
            last_article_date_str = last_article_date_item.attrib[datetime_config.get("attribute")]
        else:
            last_article_date_str = last_article_date_item.text

        last_article_date = datetime.strptime(last_article_date_str, datetime_config.get("format"))

        diff = DateUtils.diff_days(end_date, last_article_date)
        if diff == -1:
            return mid_page
        elif diff < -1:
            return self._get_end_page(base_url, end_date, mid_page, end_page)
        else:
            return self._get_end_page(base_url, end_date, start_page, mid_page)

    async def get_articles(self, pages: List[str]) -> List[Article]:
        PETITION_SIZE = 50
        
        all_articles_urls = []
        for i in range(0, len(pages), PETITION_SIZE):
            await asyncio.sleep(3) # Sleep 3 seconds between petitions
            block_urls = await self._get_articles_urls(pages[i:i+PETITION_SIZE])
            article_urls = [item for sublist in block_urls for item in sublist]
            all_articles_urls.extend(article_urls)

        for url in all_articles_urls:
            print(url)
        print(len(all_articles_urls))
        return []

    async def _get_articles_urls(self, pages: List[str]) -> List[List[str]]:
        tasks = [self._get_article_urls(page) for page in pages]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def _get_article_urls(self, page: str) -> List[str]:
        page = await AsyncFetcher.get(page)
        if page is None:
            return []

        selector = f"{self.ARTICLES_LIST_CONFIG.get('selector')} {self.ARTICLES_LIST_CONFIG.get('url').get('selector')}"

        article_links = page.css(selector)
        article_urls = set()

        for article_link in article_links:
            article_url = article_link.attrib["href"]
            if article_url is not None:
                if self.ARTICLES_LIST_CONFIG.get("url").get("prefix") is not None:
                    article_urls.add(f"{self.ARTICLES_LIST_CONFIG.get('url').get('prefix')}{article_url}")
                else:
                    article_urls.add(article_url)

        return list(article_urls)
