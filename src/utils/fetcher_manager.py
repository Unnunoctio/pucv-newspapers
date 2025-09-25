import asyncio
import time
from typing import Optional, Tuple

import aiohttp
import requests
from scrapling.fetchers import AsyncFetcher, Fetcher

from utils.logger import Logger
from utils.user_agent import UserAgent


class FetcherManager:
    """Manager for fetchers"""

    MAX_RETRIES = 3
    RETRY_DELAY = 5
    TIMEOUT = 30
    MAX_CONCURRENT = 16

    @staticmethod
    def fetch_html(url: str, retry_delay: int = RETRY_DELAY) -> Tuple[Optional[str], Optional[int]]:
        """Fetch the url and return the response, status code and exception"""
        for attempt in range(FetcherManager.MAX_RETRIES):
            try:
                response = requests.get(url=url, timeout=FetcherManager.TIMEOUT, headers={"User-Agent": UserAgent.get_random_user_agent()})
                response.raise_for_status()

                Logger.info(prefix="SUCCESS", message=f"[{response.status_code}] fetch for URL: {url}")
                return response.text, response.status_code
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    Logger.error("ERROR", f"[404] not found for URL: {url}")
                    return None, 404
                else:
                    Logger.warning("WARNING", f"[{e.response.status_code}] error to fetch URL: {url}")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            except Exception:
                Logger.error("ERROR", f"Error to fetch URL: {url}")
                Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                time.sleep(retry_delay)

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None

    @staticmethod
    def fetch_html_v2(url: str, retry_delay: int = RETRY_DELAY) -> Tuple[Optional[str], Optional[int]]:
        """Fetch the url and return the response, status code and exception"""
        for attempt in range(FetcherManager.MAX_RETRIES):
            try:
                response = Fetcher.get(
                    url,
                    retry_delay=retry_delay,
                    timeout=FetcherManager.TIMEOUT,
                    retries=FetcherManager.MAX_RETRIES,
                    headers={"User-Agent": UserAgent.get_random_user_agent()},
                )
                if response is None or response.status == 404:
                    Logger.error("ERROR", f"[404] not found for URL: {url}")
                    return None, 404
                elif response.status != 200:
                    Logger.warning("WARNING", f"[{response.status}] error to fetch URL: {url}")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    Logger.info(prefix="SUCCESS", message=f"[{response.status}] fetch for URL: {url}")
                    return response.html_content, response.status
            except Exception:
                Logger.error("ERROR", f"Error to fetch URL: {url}")

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None

    @staticmethod
    async def async_fetch_html(url: str, retry_delay: int, max_concurrent_requests: int = MAX_CONCURRENT) -> Tuple[Optional[str], Optional[int]]:
        """Async fetch the url and return the response, status code and exception"""
        for attempt in range(FetcherManager.MAX_RETRIES):
            async with asyncio.Semaphore(max_concurrent_requests):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url, timeout=FetcherManager.TIMEOUT, headers={"User-Agent": UserAgent.get_random_user_agent()}
                        ) as response:
                            if response.status == 200:
                                html = await response.text()
                                Logger.info(prefix="SUCCESS", message=f"[{response.status}] fetch for URL: {url}")
                                return html, response.status
                            elif response.status == 404:
                                Logger.error("ERROR", f"[404] not found for URL: {url}")
                                return None, 404
                            else:
                                Logger.warning("WARNING", f"[{response.status}] error to fetch URL: {url}")
                                Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                                asyncio.sleep(retry_delay)
                except Exception as e:
                    Logger.error("ERROR", f"Error to fetch URL: {url} [Error: {e}]")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None

    @staticmethod
    async def async_fetch_html_v2(url: str, retry_delay: int = RETRY_DELAY, max_concurrent_requests: int = MAX_CONCURRENT) -> Tuple[Optional[str], Optional[int]]:
        """Fetch the url and return the response, status code and exception"""
        for attempt in range(FetcherManager.MAX_RETRIES):
            try:
                response = await AsyncFetcher.get(
                    url,
                    retry_delay=retry_delay,
                    timeout=FetcherManager.TIMEOUT,
                    retries=FetcherManager.MAX_RETRIES,
                    headers={"User-Agent": UserAgent.get_random_user_agent()},
                )
                if response is None or response.status == 404:
                    Logger.error("ERROR", f"[404] not found for URL: {url}")
                    return None, 404
                elif response.status != 200:
                    Logger.warning("WARNING", f"[{response.status}] error to fetch URL: {url}")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    Logger.info(prefix="SUCCESS", message=f"[{response.status}] fetch for URL: {url}")
                    return response.html_content, response.status
            except Exception:
                Logger.error("ERROR", f"Error to fetch URL: {url}")

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None
