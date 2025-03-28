import argparse

from crawl4ai import CacheMode


def setup_argparse():
    parser = argparse.ArgumentParser(description="Web crawling utility")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser to use (default: chromium)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default: False)",
    )
    parser.add_argument(
        "--cache-mode",
        choices=[cm.value for cm in CacheMode],
        default=CacheMode.ENABLED,
        help="Cache mode for crawler (default: ENABLED)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        default=False,
        action="store_true",
        help="Enable verbose logging (default: False)",
    )
    # parser.add_argument("--output", "-o", help="Output file prefix (default: auto-generated)")
    # parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    # parser.add_argument(
    #     "--wait", type=float, default=0, help="Wait time after page load in seconds (default: 0)"
    # )
    return parser
