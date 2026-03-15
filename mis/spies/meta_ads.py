"""MetaAdsScraper — Meta Ad Library API oficial (SPY-02).

Coleta anúncios ativos de um produto via Meta Ad Library API.
Requer META_ACCESS_TOKEN no .env. Retorna [] graciosamente se token ausente.

Usage:
    scraper = MetaAdsScraper()
    ads = await scraper.fetch_ads("Nome do Produto")
    # [{"page_name": ..., "ad_snapshot_url": ..., "ad_creative_bodies": [...], ...}, ...]
"""
import os

import httpx
import structlog

from ..exceptions import ScraperError

log = structlog.get_logger()

META_API_URL = "https://graph.facebook.com/v25.0/ads_archive"


class MetaAdsScraper:
    """Spy que coleta anúncios via Meta Ad Library API oficial.

    Não herda BaseScraper — usa httpx.AsyncClient diretamente (API REST, não scraping).
    ad_reached_countries=BR é OBRIGATÓRIO pela API Meta (sem isso retorna 400).
    """

    async def fetch_ads(self, product_title: str) -> list[dict]:
        """Busca anúncios ativos para o produto na Meta Ad Library.

        Args:
            product_title: Nome do produto para buscar (truncado a 100 chars).

        Returns:
            Lista de dicts com campos page_name, ad_snapshot_url,
            ad_creative_bodies, ad_delivery_start_time.
            Retorna [] se META_ACCESS_TOKEN ausente ou API retornar {"data": []}.

        Raises:
            ScraperError: Quando a API retorna 4xx/5xx.
        """
        token = os.getenv("META_ACCESS_TOKEN", "").strip()
        if not token:
            log.warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")
            return []

        params = {
            "access_token": token,
            "search_terms": product_title[:100],
            "ad_reached_countries": "BR",  # OBRIGATÓRIO — sem isso a API retorna 400
            "ad_active_status": "ACTIVE",
            "ad_type": "ALL",
            "fields": "page_name,ad_snapshot_url,ad_creative_bodies,ad_delivery_start_time",
            "limit": 25,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(META_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json().get("data", [])
                log.info(
                    "meta_ads.fetched",
                    product_title=product_title,
                    ads_count=len(data),
                )
                return data
            except httpx.HTTPStatusError as e:
                raise ScraperError(
                    url=META_API_URL,
                    attempts=1,
                    cause=e,
                ) from e
