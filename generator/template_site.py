#!/usr/bin/env python3
"""
template_site.py — Generate a complete static HTML website from business data.
No Claude, no npm required. Works on GitHub Actions.
Usage: python3 template_site.py <leads.json> <output_dir>
"""
import sys, io, json, pathlib, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

THEMES = {
    "Boulangerie": {"primary": "#8B4513", "accent": "#D4AF37", "bg": "#FFF8F0", "emoji": "🥖", "tag": "Artisan Boulanger"},
    "Pâtisserie":  {"primary": "#C2185B", "accent": "#F8BBD9", "bg": "#FFF0F5", "emoji": "🍰", "tag": "Pâtisserie Artisanale"},
    "Restaurant":  {"primary": "#1A237E", "accent": "#FFD700", "bg": "#F8F9FF", "emoji": "🍽️", "tag": "Restaurant"},
    "Café":        {"primary": "#4E342E", "accent": "#BCAAA4", "bg": "#FFF8F5", "emoji": "☕", "tag": "Café"},
    "Pharmacie":   {"primary": "#1B5E20", "accent": "#81C784", "bg": "#F1F8F1", "emoji": "💊", "tag": "Pharmacie"},
    "Coiffeur":    {"primary": "#4A148C", "accent": "#CE93D8", "bg": "#F9F0FF", "emoji": "✂️", "tag": "Salon de Coiffure"},
    "default":     {"primary": "#1A237E", "accent": "#FFD700", "bg": "#F8F9FF", "emoji": "🏪", "tag": "Commerce Local"},
}

def get_theme(category):
    for key in THEMES:
        if key.lower() in (category or "").lower():
            return THEMES[key]
    return THEMES["default"]

def stars_html(rating):
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty

def hours_html(hours):
    if not hours:
        return ""
    rows = "".join(f'<tr><td style="padding:4px 12px 4px 0;color:#666;">{h}</td></tr>' for h in hours)
    return f'<table style="border-collapse:collapse;margin-top:8px;">{rows}</table>'

def generate_html(lead, github_url=""):
    name     = lead.get("name", "")
    category = lead.get("category", "")
    address  = lead.get("address", "")
    phone    = lead.get("phone", "")
    rating   = lead.get("rating", 4.5)
    reviews  = lead.get("review_count", 0)
    maps_url = lead.get("maps_url") or lead.get("google_maps_url", "")
    hours    = lead.get("hours", [])
    slug     = lead.get("slug", "")

    t = get_theme(category)
    p = t["primary"]
    a = t["accent"]
    bg = t["bg"]
    emoji = t["emoji"]
    tag = t["tag"]

    stars = stars_html(rating)
    hours_block = hours_html(hours)

    phone_link = f'<a href="tel:{phone}" style="color:{p};font-weight:600;text-decoration:none;font-size:1.1rem;">{phone}</a>' if phone else "<em style='color:#999'>Non communiqué</em>"
    maps_link  = f'<a href="{maps_url}" target="_blank" rel="noopener" style="display:inline-block;margin-top:8px;padding:10px 20px;background:{p};color:#fff;border-radius:8px;text-decoration:none;font-weight:600;">📍 Voir sur Google Maps</a>' if maps_url else ""
    admin_note = f'<!-- Site géré via admin local: {github_url} -->' if github_url else ""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {tag}</title>
<meta name="description" content="{name} — {tag} à {address}. Notés {rating}/5 par {reviews} clients Google.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
{admin_note}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',sans-serif;background:{bg};color:#333;line-height:1.6}}
.hero{{background:linear-gradient(135deg,{p} 0%,{p}dd 100%);color:#fff;padding:80px 20px;text-align:center}}
.hero-emoji{{font-size:4rem;display:block;margin-bottom:16px}}
.hero h1{{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.5rem);margin-bottom:12px}}
.hero .subtitle{{font-size:1.2rem;opacity:0.85;margin-bottom:20px}}
.badge{{display:inline-block;background:{a};color:#333;padding:6px 18px;border-radius:999px;font-weight:600;font-size:0.9rem}}
.stars{{color:{a};font-size:1.4rem;letter-spacing:2px}}
.reviews{{color:rgba(255,255,255,0.75);font-size:0.9rem;margin-top:4px}}
.container{{max-width:860px;margin:0 auto;padding:40px 20px}}
.card{{background:#fff;border-radius:16px;padding:32px;margin-bottom:28px;box-shadow:0 2px 16px rgba(0,0,0,0.06)}}
.card h2{{font-family:'Playfair Display',serif;color:{p};font-size:1.5rem;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid {a}40}}
.info-row{{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;font-size:1rem}}
.info-row .icon{{font-size:1.3rem;min-width:28px}}
.cta{{background:linear-gradient(135deg,{p},{p}cc);color:#fff;border-radius:16px;padding:40px;text-align:center;margin-bottom:28px}}
.cta h2{{font-family:'Playfair Display',serif;font-size:1.8rem;margin-bottom:12px}}
.cta p{{opacity:0.9;margin-bottom:20px}}
.btn{{display:inline-block;padding:14px 32px;border-radius:10px;font-weight:700;font-size:1rem;text-decoration:none;margin:6px}}
.btn-light{{background:#fff;color:{p}}}
.btn-outline{{background:transparent;color:#fff;border:2px solid rgba(255,255,255,0.6)}}
footer{{text-align:center;padding:30px 20px;color:#999;font-size:0.85rem;border-top:1px solid #eee}}
@media(max-width:600px){{.hero{{padding:50px 16px}}.card{{padding:20px}}}}
</style>
</head>
<body>

<header class="hero">
  <span class="hero-emoji">{emoji}</span>
  <h1>{name}</h1>
  <p class="subtitle">{tag}</p>
  <span class="badge">{category}</span>
  <div style="margin-top:20px">
    <div class="stars">{stars}</div>
    <div class="reviews">{rating}/5 — {reviews} avis Google</div>
  </div>
</header>

<main class="container">

  <div class="card">
    <h2>📋 Informations</h2>
    <div class="info-row"><span class="icon">📍</span><span>{address}</span></div>
    <div class="info-row"><span class="icon">📞</span><span>{phone_link}</span></div>
    <div class="info-row"><span class="icon">⭐</span><span><strong>{rating}/5</strong> — {reviews} avis clients</span></div>
    {f'<div class="info-row"><span class="icon">🗺️</span><span>{maps_link}</span></div>' if maps_url else ""}
  </div>

  {f'''<div class="card">
    <h2>🕐 Horaires</h2>
    {hours_block}
  </div>''' if hours else ""}

  <div class="cta">
    <h2>Nous contacter</h2>
    <p>Réservation, renseignements ou toute autre demande — nous sommes disponibles.</p>
    {f'<a href="tel:{phone}" class="btn btn-light">📞 Appeler</a>' if phone else ""}
    {f'<a href="{maps_url}" target="_blank" class="btn btn-outline">📍 Itinéraire</a>' if maps_url else ""}
  </div>

  <div class="card" style="text-align:center">
    <h2>À propos de {name}</h2>
    <p style="color:#555;max-width:600px;margin:0 auto;">
      Bienvenue chez <strong>{name}</strong>, votre {tag.lower()} de confiance.
      Avec <strong>{reviews} avis positifs</strong> et une note de <strong>{rating}/5</strong>,
      nous mettons tout notre savoir-faire au service de nos clients.
    </p>
  </div>

</main>

<footer>
  <p>© {name} — {address}</p>
  <p style="margin-top:4px">Site créé automatiquement · Powered by France Leads Automation</p>
</footer>

</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("leads_file", help="Path to leads JSON file")
    parser.add_argument("output_dir", help="Output directory for generated sites")
    parser.add_argument("--github-username", default="")
    args = parser.parse_args()

    leads = json.loads(pathlib.Path(args.leads_file).read_text(encoding='utf-8'))
    out_base = pathlib.Path(args.output_dir)

    for lead in leads:
        slug = lead["slug"]
        site_dir = out_base / slug
        site_dir.mkdir(parents=True, exist_ok=True)

        github_url = f"https://{args.github_username}.github.io/{slug}-site" if args.github_username else ""
        html = generate_html(lead, github_url)

        index_file = site_dir / "index.html"
        index_file.write_text(html, encoding='utf-8')

        # .nojekyll required for GitHub Pages
        (site_dir / ".nojekyll").touch()

        # client_info.json for local admin
        client_info = {
            "name": lead.get("name"),
            "category": lead.get("category"),
            "address": lead.get("address"),
            "phone": lead.get("phone"),
            "rating": lead.get("rating"),
            "review_count": lead.get("review_count"),
            "maps_url": lead.get("maps_url") or lead.get("google_maps_url"),
            "public_site": github_url,
            "slug": slug,
        }
        (site_dir / "client_info.json").write_text(
            json.dumps(client_info, ensure_ascii=False, indent=2), encoding='utf-8'
        )

        print(f"✅ Generated: {slug} → {index_file}")

if __name__ == "__main__":
    main()
