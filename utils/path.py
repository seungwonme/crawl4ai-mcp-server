"""Path conversion utilities."""

from pathlib import Path
from urllib.parse import urlparse


def url_to_filepath(url: str, base_dir: Path) -> Path:
    """URL을 파일 경로로 변환

    https://docs.crawl4ai.com/core/deep-crawling/ -> base_dir/core/deep-crawling.md
    https://docs.crawl4ai.com/ -> base_dir/index.md

    Args:
        url: 변환할 URL
        base_dir: 기본 디렉토리

    Returns:
        파일 경로 (Path 객체)
    """
    url_path = urlparse(url).path.strip("/")

    if not url_path:
        url_path = "index"

    file_path = base_dir / f"{url_path}.md"
    return file_path
