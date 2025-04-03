from crawl4ai.content_filter_strategy import BM25ContentFilter, PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

prune_filter = PruningContentFilter(
    threshold=0.5,  # Score boundary. Blocks below this score get removed.
    threshold_type="fixed",  # or "dynamic": The filter adjusts threshold in a data-driven manner, "fixed": Straight comparison
    min_word_threshold=10,  # Discard blocks under N words as likely too short or unhelpful.
)

bm25_filter = BM25ContentFilter(
    user_query="machine learning",  # The term you want to focus on
    bm25_threshold=1.2,  # Raise it to keep fewer blocks; lower it to keep more.
)


def setup_markdown_generator() -> DefaultMarkdownGenerator:
    md_generator = DefaultMarkdownGenerator(
        content_filter=prune_filter,
        options={
            "ignore_links": True,
            "ignore_images": True,
            "escape_html": False,
            "body_width": 80,
            "skip_internal_links": True,
            "include_sup_sub": True,
        },
    )

    return md_generator
