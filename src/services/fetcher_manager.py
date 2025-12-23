import asyncio
import json
from typing import Any, Optional, Tuple

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from utils.logger import Logger
from utils.user_agent import UserAgent


class FetcherManager:
    """Manager for fetchers"""

    def __init__(self, max_retries: int = 3, retry_delay: int = 5, timeout: int = 30, max_concurrent: int = 15):
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY = retry_delay
        self.TIMEOUT = timeout
        self.MAX_CONCURRENT = max_concurrent

        # config concurrent requests
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # config a session
        self._session: ClientSession | None = None

    async def _get_session(self) -> ClientSession:
        """Obtain or create a session of aiohttp"""
        if self._session is None or self._session.closed:
            connector = TCPConnector(limit=100, limit_per_host=self.MAX_CONCURRENT)
            timeout = ClientTimeout(total=self.TIMEOUT)
            headers = {"User-Agent": UserAgent.get_random_user_agent()}
            self._session = ClientSession(connector=connector, timeout=timeout, headers=headers)

        return self._session

    async def fetch_html(self, url: str, **kwargs) -> Tuple[Optional[str], Optional[int]]:
        """Fetch the url and return the response, status code and exception"""
        for attempt in range(self.MAX_RETRIES):
            async with self.semaphore:
                try:
                    session = await self._get_session()
                    async with session.get(url, **kwargs) as response:
                        if response.status == 200:
                            html = await response.text(encoding="utf-8", errors="replace")

                            Logger.info(prefix="SUCCESS", message=f"[{response.status}] fetch for URL: {url}")
                            return html, response.status
                        elif response.status == 404:
                            Logger.error("ERROR", f"[404] not found for URL: {url}")
                            return None, 404
                        else:
                            Logger.warning("WARNING", f"[{response.status}] error to fetch URL: {url}")
                            Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {self.RETRY_DELAY} seconds...")
                            await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    Logger.error("ERROR", f"Error to fetch URL: {url} [Error: {e}]")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {self.RETRY_DELAY} seconds...")
                    await asyncio.sleep(self.RETRY_DELAY)

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None

    async def fetch_json(self, url: str, **kwargs) -> Tuple[Optional[Any], Optional[int]]:
        """Fetch the url and return the response, status code and exception"""
        for attempt in range(self.MAX_RETRIES):
            async with self.semaphore:
                try:
                    session = await self._get_session()
                    async with session.get(url, **kwargs) as response:
                        if response.status == 200:
                            try:
                                json_data = await response.json()

                                Logger.info(prefix="SUCCESS", message=f"[{response.status}] fetch for URL: {url}")
                                return json_data, response.status
                            except json.JSONDecodeError as e:
                                Logger.error("SYSTEM", f"Error to decode JSON for URL: {url} [Error: {e}]")
                                return None, response.status
                            except Exception as e:
                                Logger.error("ERROR", f"Error to fetch JSON for URL: {url} [Error: {e}]")
                                return None, response.status
                        elif response.status == 404:
                            Logger.error("ERROR", f"[404] not found for URL: {url}")
                            return None, 404
                        else:
                            Logger.warning("WARNING", f"[{response.status}] error to fetch JSON for URL: {url}")
                            Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {self.RETRY_DELAY} seconds...")
                            await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    Logger.error("ERROR", f"Error to fetch JSON for URL: {url} [Error: {e}]")
                    Logger.info(prefix="NETWORK", message=f"Retry {attempt + 1} for URL: {url}, in {self.RETRY_DELAY} seconds...")
                    await asyncio.sleep(self.RETRY_DELAY)

        Logger.error("TIMER", f"Number of attempts exceeded for URL: {url}")
        return None, None

    async def close(self):
        """Close sessions"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """Context manager async entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager async exit"""
        await self.close()
