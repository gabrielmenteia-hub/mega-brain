"""Spy modules for product intelligence extraction.

Each spy is responsible for extracting one type of intelligence:
- SalesPageScraper: extracts copy and offer structure from any sales page URL
"""
from .sales_page import SalesPageScraper  # noqa: F401
