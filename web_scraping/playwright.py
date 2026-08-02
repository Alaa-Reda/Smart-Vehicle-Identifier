"""
Selenium Browser Handler

Handles JavaScript-rendered pages using Selenium WebDriver.
Named playwright.py to match the module architecture.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Chrome Options Builder
# ==========================================================

def _build_options(headless: bool = True) -> Options:
    """Build Chrome options for scraping."""

    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Hide automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return options


# ==========================================================
# Browser Session
# ==========================================================

class BrowserSession:
    """
    Selenium WebDriver session for rendering dynamic pages.

    Usage
    -----
    with BrowserSession() as browser:
        html = browser.get_page("https://example.com")
    """

    def __init__(
        self,
        headless: bool = True,
        wait_timeout: int = 10,
        page_load_timeout: int = 30,
    ) -> None:

        self.wait_timeout = wait_timeout
        self._driver: Optional[webdriver.Chrome] = None

        options = _build_options(headless=headless)

        try:
            self._driver = webdriver.Chrome(options=options)
            self._driver.set_page_load_timeout(page_load_timeout)
            logger.info("Browser session started.")

        except WebDriverException as error:
            logger.error("Failed to start browser: %s", error)
            raise

    def get_page(
        self,
        url: str,
        wait_for: Optional[str] = None,
        scroll: bool = False,
        delay: float = 2.0,
    ) -> Optional[str]:
        """
        Navigate to URL and return rendered HTML.

        Parameters
        ----------
        url : str
            Target URL.

        wait_for : str | None
            CSS selector to wait for before extracting HTML.

        scroll : bool
            Scroll to bottom to trigger lazy-loaded content.

        delay : float
            Extra wait time after page load (seconds).

        Returns
        -------
        str | None
            Rendered HTML content, or None on failure.
        """

        try:
            self._driver.get(url)

            if wait_for:
                WebDriverWait(self._driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )

            if scroll:
                self._scroll_to_bottom()

            time.sleep(delay)

            html = self._driver.page_source

            logger.info("Rendered page: %s (%d chars)", url, len(html))

            return html

        except TimeoutException:
            logger.warning("Timeout waiting for selector on: %s", url)
            return self._driver.page_source  # Return what we have

        except WebDriverException as error:
            logger.error("Browser error on %s: %s", url, error)
            return None

    def _scroll_to_bottom(self) -> None:
        """Scroll page to trigger lazy-loaded content."""

        last_height = self._driver.execute_script(
            "return document.body.scrollHeight"
        )

        while True:
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1.5)

            new_height = self._driver.execute_script(
                "return document.body.scrollHeight"
            )

            if new_height == last_height:
                break

            last_height = new_height

    def close(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None
            logger.info("Browser session closed.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()