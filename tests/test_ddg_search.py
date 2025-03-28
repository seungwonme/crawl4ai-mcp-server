import json

import pytest
from duckduckgo_search import DDGS

from src.utils.file import save_text_to_unique_file


@pytest.fixture
def ddgs():
    return DDGS()


def save_search_results(results, search_type):
    results_list = list(results)
    results_json = json.dumps(results_list, indent=2, ensure_ascii=False)
    save_text_to_unique_file(
        results_json, f"ddg_{search_type}_search_results", "json", "test_results"
    )
    return results_list


def test_text_search(ddgs):
    results = save_search_results(ddgs.text("Python programming", max_results=5), "text")
    assert len(results) > 0, "No results returned for text search"
    for result in results:
        assert "title" in result
        assert "href" in result


def test_image_search(ddgs):
    results = save_search_results(ddgs.images("Python logo", max_results=5), "image")
    assert len(results) > 0, "No results returned for image search"
    for result in results:
        assert "image" in result
        assert "thumbnail" in result


def test_news_search(ddgs):
    results = save_search_results(ddgs.news("Technology", max_results=5), "news")
    assert len(results) > 0, "No results returned for news search"
    for result in results:
        assert "title" in result
        assert "body" in result
