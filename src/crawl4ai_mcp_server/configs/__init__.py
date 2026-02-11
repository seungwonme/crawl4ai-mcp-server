"""Configuration presets for Crawl4AI."""

from .browser import FAST_CONFIG, DEBUG_CONFIG, STEALTH_CONFIG
from .crawler import DOCS_CRAWL_CONFIG, TEXT_ONLY_CONFIG, COMPREHENSIVE_CONFIG
from .deep_crawl import create_bfs_strategy, create_dfs_strategy, create_best_first_strategy

__all__ = [
    # Browser configs
    "FAST_CONFIG",
    "DEBUG_CONFIG",
    "STEALTH_CONFIG",
    # Crawler configs
    "DOCS_CRAWL_CONFIG",
    "TEXT_ONLY_CONFIG",
    "COMPREHENSIVE_CONFIG",
    # Deep crawl strategies
    "create_bfs_strategy",
    "create_dfs_strategy",
    "create_best_first_strategy",
]
