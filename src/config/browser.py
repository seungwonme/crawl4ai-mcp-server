from crawl4ai import BrowserConfig


def setup_browser_config() -> BrowserConfig:
    browser_conf = BrowserConfig(
        browser_type="firefox",
        headless=False,
        # proxy_config=None,
        viewport_width=1080,
        viewport_height=600,
        verbose=True,
        use_persistent_context=False,  # 변경: 새로운 브라우저 세션 사용
        # cookies=None,
        # headers=None,
        # user_agent=None,
        text_mode=False,
        light_mode=False,
    )

    return browser_conf
