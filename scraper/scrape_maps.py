#!/usr/bin/env python3
"""Google Maps scraper for French businesses without websites."""

import asyncio
import io
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

# Load .env manually (works on Windows + GitHub Actions without python-dotenv)
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding='utf-8').splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

SCRIPT_DIR = Path(__file__).parent
LEADS_FILE = SCRIPT_DIR / "today_leads.json"
PROCESSED_FILE = SCRIPT_DIR / "processed_urls.json"

SEARCH_QUERIES = [
    "restaurant Paris France",
    "café Lyon France",
    "boulangerie Marseille France",
    "pizzeria Toulouse France",
    "brasserie Bordeaux France",
    "kebab Nantes France",
    "crêperie Rennes France",
    "salon de thé Nice France",
    "traiteur Strasbourg France",
    "restaurant Lille France",
    "café Montpellier France",
    "boulangerie Grenoble France",
]


def clean_category(raw: str) -> str:
    """Extract clean category name from Google Maps raw text."""
    if not raw:
        return "Restaurant"
    # Try to find known category keywords
    categories = [
        "Boulangerie", "Pâtisserie", "Restaurant", "Café", "Pizzeria",
        "Brasserie", "Kebab", "Crêperie", "Salon de thé", "Traiteur",
        "Épicerie", "Bar", "Bistrot", "Sandwicherie", "Rôtisserie",
        "Glacier", "Chocolaterie", "Fromagerie",
    ]
    raw_lower = raw.lower()
    for cat in categories:
        if cat.lower() in raw_lower:
            return cat
    # Strip numbers and special chars, take last word sequence
    cleaned = re.sub(r"[\d,.()\·€–\-]", " ", raw)
    words = [w for w in cleaned.split() if len(w) > 2]
    return words[-1].capitalize() if words else "Restaurant"


def slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[éèêë]", "e", name)
    name = re.sub(r"[àâä]", "a", name)
    name = re.sub(r"[ùûü]", "u", name)
    name = re.sub(r"[îï]", "i", name)
    name = re.sub(r"[ôö]", "o", name)
    name = re.sub(r"[ç]", "c", name)
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"[\s]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:60]


def load_processed_urls() -> set:
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
        except Exception:
            return set()
    return set()


def save_processed_urls(urls: set):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(urls), f, ensure_ascii=False, indent=2)


async def scrape_query(page, query: str, processed_urls: set, max_results: int = 10) -> list:
    """Scrape Google Maps for a given query and return businesses without websites."""
    results = []
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"

    print(f"  Searching: {query}")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Accept cookies if prompted
        try:
            consent_btn = page.locator('button:has-text("Tout accepter"), button:has-text("Accept all"), form[action*="consent"] button').first
            if await consent_btn.is_visible(timeout=3000):
                await consent_btn.click()
                await asyncio.sleep(2)
        except Exception:
            pass

        # Scroll to load more results
        results_panel = page.locator('[role="feed"]')
        for _ in range(5):
            try:
                await results_panel.evaluate("el => el.scrollTop += 600")
                await asyncio.sleep(1.5)
            except Exception:
                break

        # Get all place cards
        cards = await page.locator('[role="feed"] > div').all()
        print(f"  Found {len(cards)} cards in feed")

        for card in cards[:max_results]:
            try:
                # Click on card to get details
                link_el = card.locator('a[href*="/maps/place/"]').first
                if not await link_el.is_visible(timeout=1000):
                    continue

                maps_url = await link_el.get_attribute("href") or ""
                if not maps_url or maps_url in processed_urls:
                    continue

                await link_el.click()
                await asyncio.sleep(2)

                # Extract details from detail panel
                name = ""
                try:
                    name_el = page.locator('h1.DUwDvf, h1[class*="fontHeadlineLarge"]').first
                    name = (await name_el.text_content(timeout=3000) or "").strip()
                except Exception:
                    pass

                if not name:
                    continue

                # Check for website — skip if has one
                has_website = False
                try:
                    website_btn = page.locator('a[data-item-id="authority"], a[aria-label*="site"], a[data-tooltip*="site"]').first
                    if await website_btn.is_visible(timeout=1000):
                        has_website = True
                except Exception:
                    pass

                if has_website:
                    print(f"  Skip (has website): {name}")
                    processed_urls.add(maps_url)
                    continue

                # Extract rating
                rating = 0.0
                try:
                    rating_el = page.locator('span[aria-hidden="true"].MW4etd, div[class*="fontDisplayLarge"]').first
                    rating_text = (await rating_el.text_content(timeout=2000) or "0").strip().replace(",", ".")
                    rating = float(rating_text)
                except Exception:
                    pass

                if rating < 3.8:
                    print(f"  Skip (low rating {rating}): {name}")
                    processed_urls.add(maps_url)
                    continue

                # Extract review count
                review_count = 0
                try:
                    review_el = page.locator('span[aria-label*="avis"], span[aria-label*="reviews"]').first
                    review_text = (await review_el.text_content(timeout=2000) or "0")
                    # Extract only first number to avoid concatenation artifacts
                    nums = re.findall(r"\d+", review_text.replace(" ", "").replace(" ", "").replace(" ", ""))
                    review_count = int(nums[0]) if nums else 0
                except Exception:
                    pass
                # Sanity: small businesses rarely have >50k reviews
                if review_count > 50000:
                    review_count = review_count % 10000 or 500

                if review_count < 15:
                    print(f"  Skip (few reviews {review_count}): {name}")
                    processed_urls.add(maps_url)
                    continue

                # Check permanently closed
                try:
                    closed_el = page.locator('span:has-text("Définitivement fermé"), span:has-text("Permanently closed")').first
                    if await closed_el.is_visible(timeout=1000):
                        print(f"  Skip (closed): {name}")
                        processed_urls.add(maps_url)
                        continue
                except Exception:
                    pass

                # Extract address
                address = ""
                try:
                    addr_el = page.locator('button[data-item-id="address"] .Io6YTe, [data-tooltip="Copier l\'adresse"] .Io6YTe').first
                    address = (await addr_el.text_content(timeout=2000) or "").strip()
                except Exception:
                    pass
                if not address:
                    try:
                        addr_el = page.locator('[data-item-id="address"]').first
                        address = (await addr_el.text_content(timeout=2000) or "").strip()
                    except Exception:
                        pass

                # Extract phone
                phone = ""
                try:
                    phone_el = page.locator('button[data-item-id*="phone"] .Io6YTe, [data-tooltip="Copier le numéro de téléphone"] .Io6YTe').first
                    phone = (await phone_el.text_content(timeout=2000) or "").strip()
                except Exception:
                    pass

                # Extract category
                category = query.split()[0].capitalize() if query else "Restaurant"
                try:
                    cat_el = page.locator('button[jsaction*="category"] span, div.skqShb, span.DkEaL').first
                    cat_text = (await cat_el.text_content(timeout=2000) or "").strip()
                    if cat_text:
                        category = clean_category(cat_text)
                except Exception:
                    pass

                # Extract image
                image_url = ""
                try:
                    img_el = page.locator('img[decoding="async"][src*="googleusercontent"]').first
                    image_url = await img_el.get_attribute("src", timeout=2000) or ""
                except Exception:
                    pass

                # Extract hours
                hours = []
                try:
                    hours_rows = await page.locator('table.eK4R0e tr').all()
                    for row in hours_rows[:7]:
                        row_text = (await row.text_content(timeout=1000) or "").strip()
                        if row_text:
                            hours.append(row_text)
                except Exception:
                    pass

                slug = slugify(name)
                if not slug:
                    continue

                business = {
                    "name": name,
                    "category": category,
                    "address": address,
                    "phone": phone,
                    "rating": rating,
                    "review_count": review_count,
                    "google_maps_url": maps_url,
                    "image_url": image_url,
                    "hours": hours,
                    "slug": slug,
                }
                print(f"  ✅ FOUND: {name} ({rating}★, {review_count} avis)")
                results.append(business)
                processed_urls.add(maps_url)

                if len(results) >= 3:
                    break

                # Go back to results list
                await page.go_back()
                await asyncio.sleep(2)

            except Exception as e:
                print(f"  Error processing card: {e}")
                try:
                    await page.go_back()
                    await asyncio.sleep(1)
                except Exception:
                    pass
                continue

    except Exception as e:
        print(f"  Query error: {e}")

    return results


async def main():
    processed_urls = load_processed_urls()
    print(f"Already processed: {len(processed_urls)} URLs")

    # Select query by day rotation
    query_index = date.today().toordinal() % len(SEARCH_QUERIES)

    all_leads = []
    tried_queries = set()

    for i in range(len(SEARCH_QUERIES)):
        idx = (query_index + i) % len(SEARCH_QUERIES)
        query = SEARCH_QUERIES[idx]
        if query in tried_queries:
            continue
        tried_queries.add(query)

        print(f"\nQuery [{idx}]: {query}")

        try:
            async with async_playwright() as p:
                # Try Firefox first, fall back to Chromium
                browser = None
                try:
                    browser = await p.firefox.launch(headless=True)
                    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
                except Exception as fe:
                    print(f"  Firefox unavailable ({fe}), trying Chromium...")
                    try:
                        browser = await p.chromium.launch(headless=True)
                        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                    except Exception as ce:
                        print(f"  Chromium also unavailable: {ce}")
                        browser = None

                if browser is None:
                    print("  No browser available, skipping live scraping")
                    break

                context = await browser.new_context(
                    user_agent=ua,
                    viewport={"width": 1280, "height": 900},
                    locale="fr-FR",
                    timezone_id="Europe/Paris",
                )
                page = await context.new_page()

                try:
                    leads = await scrape_query(page, query, processed_urls)
                    all_leads.extend(leads)
                finally:
                    await browser.close()
        except Exception as browser_error:
            print(f"  Browser error: {browser_error}")

        if len(all_leads) >= 3:
            break

    scraped_new = bool(all_leads)

    if not all_leads:
        # Don't overwrite existing real leads — keep them for today's run
        if LEADS_FILE.exists():
            existing = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
            if existing:
                print(f"\n⚠️  Live scraping failed. Keeping existing {len(existing)} lead(s) from {LEADS_FILE.name}")
                all_leads = existing
            else:
                print("\n⚠️  No leads found and file is empty — nothing to do.")
                return False
        else:
            print("\n⚠️  No leads found and no existing file — nothing to do.")
            return False

    # Save leads only when we have freshly scraped data
    if scraped_new:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_leads, f, ensure_ascii=False, indent=2)

    # Update processed URLs
    save_processed_urls(processed_urls)

    print(f"\n✅ Saved {len(all_leads)} leads to {LEADS_FILE}")
    for lead in all_leads:
        print(f"  • {lead['name']} ({lead['rating']}★) — {lead['address']}")

    return len(all_leads) > 0


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)  # always exit 0 — workflow checks the JSON file for results
