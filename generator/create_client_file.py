#!/usr/bin/env python3
"""
create_client_file.py — Create client contact file in ~/أعمالي/{slug}/
Called after site deployment with the public URL.
Usage: python3 create_client_file.py <slug> <public_url>
"""
import sys, io, json, pathlib, datetime, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def create_client_file(slug, public_url, leads_file=None):
    BUSINESSES = pathlib.Path.home() / "أعمالي"
    slug_dir = BUSINESSES / slug
    slug_dir.mkdir(parents=True, exist_ok=True)

    # Load lead data if available
    lead = {}
    if leads_file and pathlib.Path(leads_file).exists():
        leads = json.loads(pathlib.Path(leads_file).read_text(encoding='utf-8'))
        for l in leads:
            if l.get("slug") == slug:
                lead = l
                break

    name     = lead.get("name", slug)
    category = lead.get("category", "")
    address  = lead.get("address", "")
    phone    = lead.get("phone", "")
    rating   = lead.get("rating", "")
    reviews  = lead.get("review_count", "")
    maps_url = lead.get("maps_url") or lead.get("google_maps_url", "")
    today    = datetime.date.today().isoformat()

    # JSON file (for programmatic use)
    info = {
        "slug": slug,
        "name": name,
        "category": category,
        "address": address,
        "phone": phone,
        "rating": rating,
        "review_count": reviews,
        "maps_url": maps_url,
        "public_site": public_url,
        "admin_path": str(slug_dir / "admin"),
        "admin_login": {"username": "admin", "password": "admin123", "port": 3001},
        "created_at": today,
    }
    (slug_dir / "client_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    # Human-readable text file (the one the user asked for)
    content = f"""╔══════════════════════════════════════════════╗
  {name}
  Créé le {today}
╚══════════════════════════════════════════════╝

INFORMATIONS CLIENT
───────────────────
Nom          : {name}
Catégorie    : {category}
Adresse      : {address}
Téléphone    : {phone}
Google Maps  : {maps_url}
Note Google  : {rating}/5 ({reviews} avis)

SITE WEB PUBLIC
───────────────
URL          : {public_url}
Hébergement  : GitHub Pages (GRATUIT)
Mise à jour  : git push → déploiement automatique

TABLEAU DE BORD ADMIN (local)
──────────────────────────────
Dossier      : {slug_dir / "admin"}
Démarrer     : cd "{slug_dir / "admin"}" && npm run dev -- --port 3001
URL          : http://localhost:3001/admin
Login        : admin
Mot de passe : admin123

FONCTIONNALITÉS ADMIN
──────────────────────
✓ Réservations en ligne (avec notification Telegram)
✓ Messages / demandes de contact
✓ Statistiques de visites
✓ Paramètres du site

NOTES
──────
- Le site public est accessible 24/7 sans allumer votre PC
- L'admin se lance uniquement sur votre PC local
- Les réservations arrivent aussi sur Telegram en temps réel
"""

    info_file = slug_dir / "CONTACT.txt"
    info_file.write_text(content, encoding='utf-8')
    print(f"✅ Client file created: {info_file}")
    return str(info_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("public_url")
    parser.add_argument("--leads-file", default=None)
    args = parser.parse_args()
    create_client_file(args.slug, args.public_url, args.leads_file)
