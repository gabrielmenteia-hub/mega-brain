"""ReviewsScraper — coleta de reviews de plataformas nativas + Google fallback (SPY-04).

Fontes por plataforma:
- hotmart, clickbank, kiwify: página do produto na plataforma (reviews nativos)
- Demais plataformas: Google Search "{nome produto} review"

Valência:
- positive: rating >= 4.0
- negative: rating < 4.0

Campo source: 'hotmart' | 'clickbank' | 'kiwify' | 'google' | 'sales_page'

Falha graciosa: ScraperError é capturado e retorna [] (reviews não é bloqueante no gate).

Usage:
    async with ReviewsScraper() as scraper:
        reviews = await scraper.collect("hotmart", "https://hotmart.com/product/...", "Produto X")
        # [{"text": ..., "valence": "positive", "rating": 5.0, "source": "hotmart"}, ...]
"""
import structlog
from bs4 import BeautifulSoup

from ..base_scraper import BaseScraper
from ..exceptions import ScraperError

log = structlog.get_logger()

# Plataformas com reviews nativos acessíveis via scraping
NATIVE_REVIEW_PLATFORMS = {"hotmart", "clickbank", "kiwify"}


class ReviewsScraper(BaseScraper):
    """Spy que coleta reviews de plataformas nativas ou via Google fallback.

    Herda fetch() e fetch_spa() de BaseScraper.
    Nunca propaga ScraperError — retorna [] para não bloquear o pipeline.
    """

    async def collect(
        self,
        platform: str,
        product_url: str,
        product_title: str = "",
    ) -> list[dict]:
        """Coleta reviews. Falha graciosa — nunca propaga ScraperError.

        Args:
            platform: Plataforma de origem ('hotmart', 'clickbank', 'kiwify', etc.)
            product_url: URL da página do produto na plataforma.
            product_title: Nome do produto (usado no fallback Google).

        Returns:
            Lista de dicts com campos: text, valence, rating, source.
            Retorna [] em caso de erro.
        """
        try:
            if platform in NATIVE_REVIEW_PLATFORMS:
                return await self._collect_native(platform, product_url)
            else:
                return await self._google_fallback(product_title)
        except ScraperError as e:
            log.warning(
                "reviews.collect_failed",
                platform=platform,
                product_url=product_url,
                error=str(e),
            )
            return []

    async def _collect_native(self, platform: str, url: str) -> list[dict]:
        """Coleta reviews nativos via HTML scraping.

        Seletores CSS adaptados à estrutura da fixture hotmart_reviews.html:
        - .review-item: container de cada review
        - .review-rating[data-rating]: rating numérico
        - .review-text: texto do comentário
        """
        html = await self.fetch(url)
        soup = BeautifulSoup(html, "lxml")
        reviews = []

        for item in soup.select(".review-item"):
            try:
                rating_el = item.select_one(".review-rating[data-rating]")
                if not rating_el:
                    continue
                rating = float(rating_el["data-rating"])
                text_el = item.select_one(".review-text")
                text = text_el.get_text(strip=True) if text_el else ""
                if not text:
                    continue
                reviews.append(
                    {
                        "text": text,
                        "valence": "positive" if rating >= 4.0 else "negative",
                        "rating": rating,
                        "source": platform,
                    }
                )
            except (ValueError, KeyError, AttributeError):
                continue

        log.info(
            "reviews.native_collected",
            platform=platform,
            url=url,
            reviews_count=len(reviews),
        )
        return reviews

    async def _google_fallback(self, product_title: str) -> list[dict]:
        """Coleta snippets de resultado do Google como reviews informais.

        Args:
            product_title: Nome do produto para buscar.

        Returns:
            Lista de dicts com source='google'. Retorna [] se sem título ou erro.
        """
        if not product_title:
            return []

        query = f'"{product_title}" review'
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        try:
            html = await self.fetch(url)
            soup = BeautifulSoup(html, "lxml")
            reviews = []

            # Seletores para snippets de resultados do Google
            for snippet in soup.select(".VwiC3b, .st, [data-sncf]")[:10]:
                text = snippet.get_text(strip=True)
                if len(text) > 20:
                    reviews.append(
                        {
                            "text": text,
                            "valence": "positive",  # sem rating → assumir neutro/positivo
                            "rating": None,
                            "source": "google",
                        }
                    )

            log.info(
                "reviews.google_fallback",
                product_title=product_title,
                reviews_count=len(reviews),
            )
            return reviews
        except ScraperError:
            return []
