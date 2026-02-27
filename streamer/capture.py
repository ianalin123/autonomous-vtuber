import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page


class HeadlessCapture:
    def __init__(self, frontend_url: str) -> None:
        self._url = frontend_url
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def start(self) -> None:
        pw = await async_playwright().start()
        self._browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--display=:99",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-web-security",
            ],
        )
        self._page = await self._browser.new_page(
            viewport={"width": 1280, "height": 720}
        )
        await self._page.goto(self._url)
        await self._page.wait_for_load_state("networkidle")

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
