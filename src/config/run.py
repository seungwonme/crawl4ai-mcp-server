from crawl4ai import CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


def setup_run_config(md_generator: DefaultMarkdownGenerator) -> CrawlerRunConfig:
    run_conf = CrawlerRunConfig(
        word_count_threshold=10,  # Minimum words per content block
        # extraction_strategy=None,
        markdown_generator=md_generator,
        # js_code=None,
        wait_for="js:() => window.loaded === true",
        screenshot=True,
        pdf=True,
        verbose=False,  # Same as browser_conf.verbose
        excluded_tags=["nav", "aside", "footer", "form", "header"],
        exclude_external_links=True,  # Remove external links
        remove_overlay_elements=True,  # Remove popups/modals
        process_iframes=True,  # Process iframe content
        stream=False,
    )
    return run_conf
