import asyncio
import logging
import time
from typing import Optional

import aiohttp
import requests


class WebFetcher:
    def __init__(self, max_retries: int = 3, delay: int = 5, max_concurrent: int = 10):
        self.MAX_RETRIES = max_retries
        self.DELAY = delay
        self.MAX_CONCURRENT = max_concurrent

        # Configure concurrent requests
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        # Configure default headers to avoid being blocked
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def sleep(self, seconds: int) -> None:
        time.sleep(seconds)

    # === Metodos Sincronos ===
    def fetch_page(self, url: str, delay: int = None, retries: int = 0, is_success: bool = False) -> Optional[str]:
        if delay is None:
            delay = self.DELAY

        try:
            res = requests.get(url, headers=self.headers, timeout=30)
            res.raise_for_status()
            res.encoding = "utf-8"

            if is_success:
                self.logger.info(f"OK for URL: {url}")
            return res.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.info(f"404 not found for URL: {url}")
                return None
            else:
                return self._handle_retry_page(url, delay, retries, e)
        except Exception as e:
            return self._handle_retry_page(url, delay, retries, e)

    def fetch_json(self, url: str, delay: int = None, retries: int = 0, is_success: bool = False) -> Optional[dict]:
        if delay is None:
            delay = self.DELAY

        try:
            res = requests.get(url, headers=self.headers, timeout=30)
            res.raise_for_status()
            
            if is_success:
                self.logger.info(f"OK for URL: {url}")
            return res.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.info(f"404 not found for URL: {url}")
                return None
            else:
                return self._handle_retry_json(url, delay, retries, e)
        except Exception as e:
            return self._handle_retry_json(url, delay, retries, e)

    def _handle_retry_page(self, url: str, delay: int, retries: int, error: Exception) -> Optional[str]:
        if retries < self.MAX_RETRIES:
            self.logger.warning(f"RETRY {retries + 1} for URL: {url}")
            self.sleep(delay)
            return self.fetch_page(url, delay, retries + 1)
        else:
            self.logger.error(f"FAILED fetch after {self.MAX_RETRIES} for URL: {url}")
            return None

    def _handle_retry_json(self, url: str, delay: int, retries: int, error: Exception) -> Optional[dict]:
        if retries < self.MAX_RETRIES:
            self.logger.warning(f"RETRY {retries + 1} for URL: {url}")
            self.sleep(delay)
            return self.fetch_json(url, delay, retries + 1, is_success=True)
        else:
            self.logger.error(f"FAILED fetch after {self.MAX_RETRIES} for URL: {url}")
            return None

    # === Metodos Asincronos ===
    async def async_fetch_page(self, session: aiohttp.ClientSession, url: str, delay: int = None, retries: int = 0, is_success: bool = False) -> Optional[str]:
        if delay is None:
            delay = self.DELAY

        async with self.semaphore:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as res:
                    if res.status == 404:
                        self.logger.info(f"404 not found for URL: {url}")
                        return None

                    res.raise_for_status()
                    content = await res.text(encoding="utf-8")

                    if is_success:
                        self.logger.info(f"OK for URL: {url}")
                    return content
            except aiohttp.ClientError as e:
                return await self._async_handle_retry_page(session, url, delay, retries, e)
            except Exception as e:
                return await self._async_handle_retry_page(session, url, delay, retries, e)

    async def async_fetch_json(self, session: aiohttp.ClientSession, url: str, delay: int = None, retries: int = 0, is_success: bool = False) -> Optional[dict]:
        if delay is None:
            delay = self.DELAY

        async with self.semaphore:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 404:
                        self.logger.info(f"404 not found for URL: {url}")
                        return None

                    response.raise_for_status()

                    if is_success:
                        self.logger.info(f"OK for URL: {url}")
                    return await response.json()
            except aiohttp.ClientError as e:
                return await self._async_handle_retry_json(session, url, delay, retries, e)
            except Exception as e:
                return await self._async_handle_retry_json(session, url, delay, retries, e)

    async def _async_handle_retry_page(self, session: aiohttp.ClientSession, url: str, delay: int, retries: int, error: Exception) -> Optional[str]:
        if retries < self.MAX_RETRIES:
            self.logger.warning(f"RETRY {retries + 1} for URL: {url}")
            await asyncio.sleep(delay)
            return await self.async_fetch_page(session, url, delay, retries + 1)
        else:
            self.logger.error(f"FAILED fetch after {self.MAX_RETRIES} for URL: {url}")
            return None

    async def _async_handle_retry_json(self, session: aiohttp.ClientSession, url: str, delay: int, retries: int, error: Exception) -> Optional[dict]:
        if retries < self.MAX_RETRIES:
            self.logger.warning(f"RETRY {retries + 1} for URL: {url}")
            await asyncio.sleep(delay)
            return await self.async_fetch_json(session, url, delay, retries + 1)
        else:
            self.logger.error(f"FAILED fetch after {self.MAX_RETRIES} for URL: {url}")
            return None
