"""Custom exceptions for the MIS scraping system."""


class ScraperError(Exception):
    """Raised when a scraper fails after exhausting all retry attempts.

    Attributes:
        url: The URL that was being fetched.
        attempts: Number of attempts made before giving up.
        cause: The underlying exception that caused the failure.
    """

    def __init__(self, url: str, attempts: int, cause: Exception) -> None:
        self.url = url
        self.attempts = attempts
        self.cause = cause
        super().__init__(
            f"ScraperError after {attempts} attempt(s) on {url}: {cause}"
        )
