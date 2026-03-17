"""Centralized platform ID constants for MIS scanners.

These IDs correspond to the rows inserted by migration _006_v2_platforms.py.
Import from here instead of defining local constants in each scanner.

These IDs MUST match migration _006_v2_platforms.py — mismatch causes
silent FK violations when inserting products.

Usage:
    from mis.platform_ids import HOTMART_PLATFORM_ID, EDUZZ_PLATFORM_ID
"""

HOTMART_PLATFORM_ID = 1
CLICKBANK_PLATFORM_ID = 2
KIWIFY_PLATFORM_ID = 3
EDUZZ_PLATFORM_ID = 4
MONETIZZE_PLATFORM_ID = 5
PERFECTPAY_PLATFORM_ID = 6
BRAIP_PLATFORM_ID = 7
PRODUCT_HUNT_PLATFORM_ID = 8
UDEMY_PLATFORM_ID = 9
JVZOO_PLATFORM_ID = 10
GUMROAD_PLATFORM_ID = 11
APPSUMO_PLATFORM_ID = 12
