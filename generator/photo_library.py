"""
photo_library.py — Photo library manager for France Leads Automation.

Sources (in priority order):
  1. photo_library.json  — pre-cached Pexels CDN URLs (primary, unlimited sites)
  2. Higgsfield CDN      — AI-generated, passed via --higgsfield flag
  3. Unsplash            — built-in verified IDs (fallback)

To build/refresh the library:
    python photo_library.py --build --pexels-key YOUR_KEY

Free Pexels API key: https://www.pexels.com/api/ (instant, no approval)
"""

import argparse
import hashlib
import json
import pathlib
import sys
import urllib.parse
import urllib.request

LIBRARY_PATH = pathlib.Path(__file__).parent / "photo_library.json"

# Pexels search queries per category × section
# Each tuple: (query, count_to_fetch)
PEXELS_QUERIES = {
    "boulangerie": {
        "hero":      [("french bakery storefront", 15), ("boulangerie paris", 10)],
        "about":     [("baker artisan bread", 12), ("boulanger farine", 8)],
        "menu_hero": [("croissant baguette display", 12), ("french bread pastry", 10)],
        "gallery":   [
            ("fresh croissant closeup", 10),
            ("sourdough bread artisan", 10),
            ("french bakery interior", 10),
            ("baguette oven bakery", 8),
            ("pain au chocolat", 8),
            ("brioche bread golden", 8),
            ("french breakfast table", 8),
            ("patisserie window display", 8),
        ],
    },
    "patisserie": {
        "hero":      [("french patisserie facade", 12), ("luxury pastry shop", 10)],
        "about":     [("pastry chef decoration", 12), ("confiseur gâteau", 8)],
        "menu_hero": [("french macarons display", 12), ("luxury pastry assortment", 10)],
        "gallery":   [
            ("colorful macarons", 10),
            ("mille feuille pastry", 10),
            ("opera cake chocolate", 8),
            ("strawberry tart french", 8),
            ("eclair chocolate glaze", 8),
            ("paris brest praline", 8),
            ("creme brulee dessert", 8),
            ("french dessert elegant", 8),
        ],
    },
    "restaurant": {
        "hero":      [("french restaurant exterior", 12), ("bistro paris terrace", 10)],
        "about":     [("chef plating french cuisine", 12), ("restaurant kitchen cook", 8)],
        "menu_hero": [("fine dining french food", 12), ("elegant plate presentation", 10)],
        "gallery":   [
            ("french onion soup", 10),
            ("duck confit plated", 10),
            ("coq au vin rustic", 8),
            ("french bistro interior", 10),
            ("charcuterie cheese board", 8),
            ("beef bourguignon", 8),
            ("french restaurant table", 8),
            ("wine food pairing", 8),
        ],
    },
    "cafe": {
        "hero":      [("french cafe terrace", 12), ("paris cafe exterior", 10)],
        "about":     [("barista coffee art", 12), ("coffee shop cozy", 8)],
        "menu_hero": [("coffee croissant morning", 12), ("latte art cup", 10)],
        "gallery":   [
            ("espresso cup ceramic", 10),
            ("cozy cafe interior wooden", 10),
            ("french press coffee", 8),
            ("iced coffee summer", 8),
            ("cafe terrace street", 10),
            ("cappuccino foam art", 8),
            ("breakfast cafe table", 8),
            ("wifi work cafe laptop", 6),
        ],
    },
}

PEXELS_QUERIES["default"] = PEXELS_QUERIES["restaurant"]


def _pexels_search(query: str, count: int, api_key: str, page: int = 1) -> list[str]:
    """Search Pexels and return CDN photo URLs (landscape, high quality)."""
    q = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={q}&per_page={min(count, 80)}&page={page}&orientation=landscape&size=large"
    req = urllib.request.Request(url, headers={"Authorization": api_key, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        urls = []
        for photo in data.get("photos", []):
            src = photo.get("src", {})
            # Use 'large2x' (2560px) or 'large' (1920px) for best quality
            u = src.get("large2x") or src.get("large") or src.get("original", "")
            if u:
                urls.append(u)
        return urls
    except Exception as e:
        print(f"    Pexels error for '{query}': {e}", file=sys.stderr)
        return []


def build_library(api_key: str, verbose: bool = True) -> dict:
    """Fetch photos from Pexels and build the complete library."""
    library = {}
    total_fetched = 0

    for category, sections in PEXELS_QUERIES.items():
        if verbose:
            print(f"\n[{category}]")
        library[category] = {}

        for section, queries in sections.items():
            urls = []
            for query, count in queries:
                if verbose:
                    print(f"  {section}: '{query}' -> ", end="", flush=True)
                fetched = _pexels_search(query, count, api_key)
                # deduplicate within section
                for u in fetched:
                    if u not in urls:
                        urls.append(u)
                if verbose:
                    print(f"{len(fetched)} photos")
                total_fetched += len(fetched)

            library[category][section] = urls

    if verbose:
        print(f"\nTotal: {total_fetched} photos across {len(library)} categories")

    return library


def save_library(library: dict):
    LIBRARY_PATH.write_text(
        json.dumps(library, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved to {LIBRARY_PATH}")


def load_library() -> dict:
    if not LIBRARY_PATH.exists():
        return {}
    return json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))


def get_photos_for_site(category: str, slug: str, library: dict) -> dict | None:
    """
    Return a photo dict for a site from the library.
    Uses slug-based seed so same business always gets same photos (deterministic).
    Returns None if library is empty for this category.
    """
    cat = category.lower()
    # fallback chain
    cat_data = library.get(cat) or library.get("default") or library.get("restaurant")
    if not cat_data:
        return None

    # seed from slug for deterministic selection
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16)

    def pick(urls: list, offset: int = 0) -> str:
        if not urls:
            return ""
        return urls[(seed + offset) % len(urls)]

    def pick_n(urls: list, n: int) -> list:
        if not urls:
            return []
        idxs = [(seed + i) % len(urls) for i in range(n)]
        return [urls[i] for i in idxs]

    return {
        "hero":      pick(cat_data.get("hero", []), 0),
        "about":     pick(cat_data.get("about", []), 1),
        "menu_hero": pick(cat_data.get("menu_hero", []), 2),
        "gallery":   pick_n(cat_data.get("gallery", []), 8),
    }


def library_stats(library: dict):
    """Print stats for each category."""
    print(f"\n{'Category':<15} {'Hero':>6} {'About':>6} {'Menu':>6} {'Gallery':>8} {'Total':>7}")
    print("-" * 55)
    grand = 0
    for cat, sections in library.items():
        hero    = len(sections.get("hero", []))
        about   = len(sections.get("about", []))
        menu    = len(sections.get("menu_hero", []))
        gallery = len(sections.get("gallery", []))
        total   = hero + about + menu + gallery
        grand  += total
        print(f"{cat:<15} {hero:>6} {about:>6} {menu:>6} {gallery:>8} {total:>7}")
    print("-" * 55)
    print(f"{'TOTAL':<15} {'':>6} {'':>6} {'':>6} {'':>8} {grand:>7}")

    # Estimate unique sites possible per category
    print(f"\nUnique sites supportable (gallery variety):")
    for cat, sections in library.items():
        g = len(sections.get("gallery", []))
        print(f"  {cat}: ~{g} unique gallery combinations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build/inspect Pexels photo library")
    parser.add_argument("--build", action="store_true", help="Fetch photos from Pexels and save library")
    parser.add_argument("--pexels-key", help="Pexels API key (or set PEXELS_API_KEY env var)")
    parser.add_argument("--stats", action="store_true", help="Show library statistics")
    parser.add_argument("--test", help="Test photo selection for a slug (e.g. boulangerie:bonne-miette)")
    args = parser.parse_args()

    if args.stats or (not args.build and not args.test):
        lib = load_library()
        if not lib:
            print("Library is empty. Run: python photo_library.py --build --pexels-key YOUR_KEY")
        else:
            library_stats(lib)

    if args.build:
        import os
        key = args.pexels_key or os.environ.get("PEXELS_API_KEY", "")
        if not key:
            print("Error: provide --pexels-key or set PEXELS_API_KEY environment variable")
            print("Get a free key at: https://www.pexels.com/api/")
            sys.exit(1)
        lib = build_library(key)
        save_library(lib)
        library_stats(lib)

    if args.test:
        cat, slug = (args.test.split(":", 1) + ["test-slug"])[:2]
        lib = load_library()
        photos = get_photos_for_site(cat, slug, lib)
        if photos:
            print(json.dumps(photos, indent=2))
        else:
            print(f"No photos found for category '{cat}'")
