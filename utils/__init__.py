"""Utility functions for crawling."""

from .domain import extract_domain, extract_output_dir_name
from .path import url_to_filepath

__all__ = ["extract_domain", "extract_output_dir_name", "url_to_filepath"]
