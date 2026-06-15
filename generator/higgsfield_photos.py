"""
higgsfield_photos.py — Generate AI photos for a business using Higgsfield CLI.

Usage:
    python higgsfield_photos.py --category boulangerie --city Marseille --name "Bonne Miette" --out photos.json

Requires: hf.exe authenticated (run: hf auth login)
"""

import argparse
import json
import pathlib
import subprocess
import sys

HF_EXE = str(pathlib.Path.home() / "higgsfield" / "hf.exe")

# Prompts tuned per business category — cinematic, photorealistic, French aesthetic
PROMPTS = {
    "boulangerie": {
        "hero":      "French boulangerie facade in {city}, warm morning sunlight, golden stone building, freshly baked baguettes in window, inviting, photorealistic",
        "about":     "Artisan baker in white apron inside French bakery, kneading dough, rustic wooden table, warm amber light, photorealistic portrait",
        "menu_hero": "Elegant display of French pastries and baguettes on marble counter, soft natural light, photorealistic",
        "gallery":   [
            "Fresh croissants and pain au chocolat on rustic wooden board, warm golden light, closeup, photorealistic",
            "Rows of sourdough loaves on bakery shelves, artisan French boulangerie, photorealistic",
            "French baguettes cooling on wire rack, bakery interior, morning light, photorealistic",
            "Display case with colorful macarons and tarts, French patisserie, photorealistic",
            "Baker sliding bread into stone oven, traditional French boulangerie, photorealistic",
            "Rustic French breakfast: croissant, jam, coffee on marble table, morning light, photorealistic",
        ],
    },
    "patisserie": {
        "hero":      "Elegant French patisserie facade in {city}, luxury window display with macarons and cakes, warm evening light, photorealistic",
        "about":     "Pastry chef decorating elegant cake in professional kitchen, white uniform, artistic, photorealistic",
        "menu_hero": "Luxury French pastry assortment on glass display, colorful macarons, eclairs, tarts, photorealistic",
        "gallery":   [
            "Row of colorful French macarons on white marble, photorealistic",
            "Elegant layered mille-feuille pastry, close-up, delicate layers, photorealistic",
            "French Opera cake slice, coffee and chocolate layers, artistic plating, photorealistic",
            "Strawberry tart with fresh berries and cream, French patisserie, photorealistic",
            "Chocolate eclairs glazed on pastry display, French bakery, photorealistic",
            "Paris-Brest pastry ring with praline cream, classic French dessert, photorealistic",
        ],
    },
    "restaurant": {
        "hero":      "Elegant French restaurant exterior in {city}, bistro chairs on sidewalk, evening ambiance, warm lights, photorealistic",
        "about":     "Chef in white jacket plating an elegant French dish, professional kitchen, artistic presentation, photorealistic",
        "menu_hero": "Beautifully plated French cuisine dish, fine dining, artistic presentation, warm lighting, photorealistic",
        "gallery":   [
            "Classic French onion soup in rustic bowl, melted gruyere cheese, photorealistic",
            "Duck confit with roasted vegetables, French bistro dish, warm plating, photorealistic",
            "Coq au vin in cast iron pot, rustic French cooking, photorealistic",
            "Elegant French restaurant interior, candlelit tables, warm atmosphere, photorealistic",
            "Charcuterie board with French cheeses and cured meats, photorealistic",
            "Crème brûlée with caramelized sugar top, classic French dessert, photorealistic",
        ],
    },
    "cafe": {
        "hero":      "Charming French cafe in {city}, outdoor terrace with bistro chairs, morning light, photorealistic",
        "about":     "Barista preparing cappuccino in cozy French cafe, warm light, artisan coffee, photorealistic",
        "menu_hero": "Flat white coffee and croissant on wooden table, French cafe morning, warm tones, photorealistic",
        "gallery":   [
            "Espresso macchiato with latte art in ceramic cup, French cafe, photorealistic",
            "Cozy French cafe interior, wooden chairs, chalkboard menu, warm atmosphere, photorealistic",
            "French press coffee and fresh pastries on marble table, morning light, photorealistic",
            "Iced coffee drinks on outdoor cafe table, sunny Paris street, photorealistic",
            "Cafe terrace with Parisian street view, bistro culture, golden hour, photorealistic",
            "Colorful macarons and coffee on cafe table, French aesthetic, photorealistic",
        ],
    },
}

PROMPTS["default"] = PROMPTS["restaurant"]


def run_hf(args: list[str]) -> dict:
    cmd = [HF_EXE] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"hf error: {result.stderr.strip()}")
    return json.loads(result.stdout)


def generate_one(prompt: str, model: str = "flux_2") -> str:
    """Generate one image and return the result URL."""
    data = run_hf(["generate", "create", model, "--prompt", prompt, "--wait"])
    if isinstance(data, list):
        data = data[0]
    url = data.get("result_url", "")
    if not url:
        raise RuntimeError(f"No result_url in response: {data}")
    return url


def generate_photos(category: str, city: str, name: str, model: str = "flux_2") -> dict:
    """Generate all photos for a business. Returns dict matching PHOTOS schema."""
    cat = category.lower()
    if cat not in PROMPTS:
        cat = "default"
    tmpl = PROMPTS[cat]

    def fmt(p: str) -> str:
        return p.replace("{city}", city).replace("{name}", name)

    print(f"  Generating hero photo...")
    hero_url = generate_one(fmt(tmpl["hero"]), model)

    print(f"  Generating about photo...")
    about_url = generate_one(fmt(tmpl["about"]), model)

    print(f"  Generating menu hero photo...")
    menu_url = generate_one(fmt(tmpl["menu_hero"]), model)

    gallery_urls = []
    for i, g in enumerate(tmpl["gallery"]):
        print(f"  Generating gallery photo {i+1}/{len(tmpl['gallery'])}...")
        gallery_urls.append(generate_one(fmt(g), model))

    return {
        "hero":      hero_url,
        "about":     about_url,
        "menu_hero": menu_url,
        "gallery":   gallery_urls,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate AI photos for a business using Higgsfield")
    parser.add_argument("--category", required=True, help="Business category (boulangerie/patisserie/restaurant/cafe)")
    parser.add_argument("--city", default="France", help="City name for prompts")
    parser.add_argument("--name", default="", help="Business name for prompts")
    parser.add_argument("--model", default="flux_2", help="Higgsfield model to use (default: flux_2 = 1 credit/image)")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    parser.add_argument("--check-credits", action="store_true", help="Show credits and estimated cost, then exit")
    args = parser.parse_args()

    # Count images to generate
    cat = args.category.lower()
    if cat not in PROMPTS:
        cat = "default"
    n_gallery = len(PROMPTS[cat]["gallery"])
    total = 3 + n_gallery  # hero + about + menu_hero + gallery

    if args.check_credits:
        cost_data = run_hf(["generate", "cost", args.model, "--prompt", "test"])
        cost_per = int(str(cost_data).strip().split()[0]) if isinstance(cost_data, str) else 1
        print(f"Model: {args.model}")
        print(f"Images to generate: {total} (3 main + {n_gallery} gallery)")
        print(f"Estimated cost: {total * cost_per} credits")
        status = run_hf(["account", "status"])
        print(f"Account: {status}")
        sys.exit(0)

    print(f"Generating {total} photos for '{args.name}' ({args.category}, {args.city}) using {args.model}...")
    photos = generate_photos(args.category, args.city, args.name, args.model)

    out = pathlib.Path(args.out)
    out.write_text(json.dumps(photos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to {out}")
    print(f"Hero:     {photos['hero']}")
    print(f"About:    {photos['about']}")
    print(f"Menu:     {photos['menu_hero']}")
    print(f"Gallery:  {len(photos['gallery'])} photos")


if __name__ == "__main__":
    main()
