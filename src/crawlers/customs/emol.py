import asyncio
import math
import re
import time
from datetime import datetime
from typing import List

from core.models import Article
from crawlers.generics.api import ApiCrawler
from utils.date_utils import DateUtils
from utils.logger import Logger


class EmolCrawler(ApiCrawler):
    """Crawler custom to EMOL"""

    def __init__(self, config, date_range):
        super().__init__(config, date_range)

    # TODO: GENERATE PAGES
    async def generate_pages(self, base_url) -> List[str]:
        """Generate the list of pages to crawl"""
        total_papers = await self._get_total_articles(base_url)
        start_paper = await self._get_start_paper(base_url, self.date_range.start_date, 0, total_papers - 1)
        end_paper = await self._get_end_paper(base_url, self.date_range.end_date, 0, start_paper)
        if end_paper > start_paper:
            start_paper, end_paper = end_paper, start_paper

        Logger.info(prefix="INFO", message=f"Getting papers between: {end_paper} and {start_paper}")
        Logger.info(prefix="SPIDER", message=f"Obteniendo: {start_paper - end_paper} artículos")

        urls = []
        for i in range(end_paper, start_paper, self.REQUESTS_CONFIG.get("articles_per_request")):
            url = re.sub(r"\(\\size\+\)", str(self.REQUESTS_CONFIG.get("articles_per_request")), base_url)  # set size
            url = re.sub(r"\(\\from\+\)", str(i), url)  # set from
            urls.append(url)

        return urls

    async def _get_total_articles(self, base_url: str) -> int:
        url = re.sub(r"\(\\size\+\)", str(1), base_url)  # set size
        url = re.sub(r"\(\\from\+\)", str(0), url)  # set from

        data_json, status = await self.FETCHER.fetch_json(url=url)
        if status is None or status == 404:
            return 0

        total_articles = self._get_nested_safe(data_json, self.PAGINATION.get("total_articles").get("path"))
        if total_articles is None:
            return 0

        return total_articles

    async def _get_start_paper(self, base_url: str, start_date: datetime, start_article: int, end_article: int) -> int:
        """Get the start paper to crawl"""
        if start_article >= end_article - 1:
            return end_article

        mid_article = math.floor((start_article + end_article) / 2)

        url = re.sub(r"\(\\size\+\)", str(1), base_url)  # set size
        url = re.sub(r"\(\\from\+\)", str(mid_article), url)  # set from

        data_json, status = await self.FETCHER.fetch_json(url=url)
        if status is None or status == 404:
            return await self._get_start_paper(base_url, start_date, start_article + 1, end_article)

        # Get articles
        article_list = self._get_nested_safe(data_json, self.ARTICLES_LIST_CONFIG.get("path"))
        if article_list is None or len(article_list) == 0:
            Logger.error("NETWORK", f"Don't found any articles for URL: {url}")
            await asyncio.sleep(self.FETCHER.RETRY_DELAY)
            return await self._get_start_paper(base_url, start_date, start_article + 1, end_article)

        # Get date from article
        article = article_list[0]
        date_str = self._get_attribute_safe(article, self.ARTICLE_CONFIG.get("date").get("paths"))

        if self.ARTICLE_CONFIG.get("date").get("formats") is not None:
            for date_format in self.ARTICLE_CONFIG.get("date").get("formats"):
                try:
                    if "T" in date_format:
                        new_date_format = date_format.split("T")[0]
                        new_date_str = date_str.split("T")[0]
                        article_date = datetime.strptime(new_date_str, new_date_format)
                    else:
                        article_date = datetime.strptime(date_str, date_format)
                    break
                except Exception:
                    pass
        else:
            article_date = datetime.strptime(date_str)

        # Binary search logic
        diff = DateUtils.diff_days(start_date, article_date)
        if diff == 1:
            return mid_article
        elif diff > 1:
            return await self._get_start_paper(base_url, start_date, start_article, mid_article)
        else:
            return await self._get_start_paper(base_url, start_date, mid_article, end_article)

    async def _get_end_paper(self, base_url: str, end_date: datetime, start_article: int, end_article: int) -> int:
        """Get the end paper to crawl"""
        if start_article >= end_article - 1:
            return start_article

        mid_article = math.floor((start_article + end_article) / 2)

        url = re.sub(r"\(\\size\+\)", str(1), base_url)  # set size
        url = re.sub(r"\(\\from\+\)", str(mid_article), url)  # set from

        data_json, status = await self.FETCHER.fetch_json(url=url)
        if status is None or status == 404:
            return await self._get_end_paper(base_url, end_date, start_article, end_article - 1)

        # Get articles
        article_list = self._get_nested_safe(data_json, self.ARTICLES_LIST_CONFIG.get("path"))
        if article_list is None or len(article_list) == 0:
            Logger.error("NETWORK", f"Don't found any articles for URL: {url}")
            await asyncio.sleep(self.FETCHER.RETRY_DELAY)
            return await self._get_end_paper(base_url, end_date, start_article, end_article - 1)

        # Get date from article
        article = article_list[0]
        date_str = self._get_attribute_safe(article, self.ARTICLE_CONFIG.get("date").get("paths"))

        if self.ARTICLE_CONFIG.get("date").get("formats") is not None:
            for date_format in self.ARTICLE_CONFIG.get("date").get("formats"):
                try:
                    if "T" in date_format:
                        new_date_format = date_format.split("T")[0]
                        new_date_str = date_str.split("T")[0]
                        article_date = datetime.strptime(new_date_str, new_date_format)
                    else:
                        article_date = datetime.strptime(date_str, date_format)
                    break
                except Exception:
                    pass
        else:
            article_date = datetime.strptime(date_str)

        # Binary search logic
        diff = DateUtils.diff_days(end_date, article_date)
        if diff == -1:
            return mid_article
        elif diff < -1:
            return await self._get_end_paper(base_url, end_date, mid_article, end_article)
        else:
            return await self._get_end_paper(base_url, end_date, start_article, mid_article)

    # TODO: GET ARTICLES
    async def get_articles(self, pages: List[str]) -> List[Article]:
        """Get the list of articles from the url"""
        BLOCK_SIZE = int(self.REQUESTS_CONFIG.get("requests_per_minute") / 60)

        all_articles = []
        for i in range(0, len(pages), BLOCK_SIZE):
            start_time = time.time()
            articles = await self._get_block_articles(pages[i : i + BLOCK_SIZE])
            if self.REQUESTS_CONFIG.get("filter_inside_date_range") is not None and self.REQUESTS_CONFIG.get("filter_inside_date_range") is False:
                all_articles.extend(filter(lambda a: (a is not None), articles))
            else:
                all_articles.extend(filter(lambda a: (a is not None) and (a.date >= self.date_range.start_date and a.date <= self.date_range.end_date), articles))

            await self._sleep_between_requests(start_time)

        # close fetcher
        await self.FETCHER.close()

        return all_articles

    async def _get_block_articles(self, urls: List[str]) -> List[Article]:
        tasks = [self._get_articles(url) for url in urls]
        block_articles = await asyncio.gather(*tasks, return_exceptions=False)
        return [item for sublist in block_articles for item in sublist]

    async def _get_articles(self, url: str) -> List[Article]:
        data_json, status = await self.FETCHER.fetch_json(url)
        if status is None or status == 404:
            return []

        # Get articles
        article_list = self._get_nested_safe(data_json, self.ARTICLES_LIST_CONFIG.get("path"))
        if article_list is None or len(article_list) == 0:
            return []

        # Parse articles
        articles_parsed = []
        for article in article_list:
            article_parsed = self._parse_article(article)
            articles_parsed.append(article_parsed)

        return articles_parsed
