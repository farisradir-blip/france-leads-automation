#!/usr/bin/env python3
"""
run_daily.py — Daily orchestrator for France Leads Automation
Runs at 08:00 Paris time via Windows Task Scheduler
"""
import sys, io, os, json, subprocess, pathlib, time, urllib.request, urllib.parse, urllib.error, logging
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = pathlib.Path.home() / "france-leads-automation"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)

# File logger — appends to logs/YYYY-MM-DD.log
_log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(str(_log_file), encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("leads")

def L(msg):
    log.info(msg)
SITES = BASE / "sites"
BUSINESSES = pathlib.Path.home() / "أعمالي"  # ~/أعمالي
LEADS_FILE = BASE / "scraper" / "today_leads.json"
ENV_FILE = BASE / ".env"

def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        L(f"Telegram error: {e}")
        return False

def run(cmd, cwd=None, env_extra=None, timeout=600):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=timeout, env=env
    )
    return result

def already_processed(slug):
    """Check if this slug was already deployed today."""
    marker = BUSINESSES / slug / ".deployed"
    if not marker.exists():
        return False
    content = marker.read_text(encoding='utf-8').strip()
    from datetime import date
    return content == str(date.today())

def mark_deployed(slug):
    from datetime import date
    marker = BUSINESSES / slug / ".deployed"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(date.today()), encoding='utf-8')

def step_scrape():
    L("[1/4] SCRAPING Google Maps...")
    result = run(
        f'python3 "{BASE / "scraper" / "scrape_maps.py"}"',
        cwd=str(BASE / "scraper")
    )
    if result.returncode != 0:
        L(f"Scraper FAILED:\n{result.stderr[-500:]}")
        return False
    L(f"Scraper done.")
    return True

def step_generate_site(lead, env_vars):
    slug = lead['slug']
    name = lead['name']
    category = lead.get('category', 'Commerce')
    address = lead.get('address', '')
    phone = lead.get('phone', '')
    rating = lead.get('rating', 4.5)
    reviews = lead.get('review_count', 100)
    maps_url = lead.get('maps_url', '')

    out_dir = SITES / slug / "public-site" / "out"
    if out_dir.exists() and (out_dir / "index.html").exists():
        L(f"[2/4] Site already built for {slug}, skipping.")
        return True

    L(f"[2/4] GENERATING SITE for {name}...")
    script = BASE / "generator" / "generate_site.sh"
    cmd = f'bash "{script}" "{name}" "{category}" "{address}" "{phone}" "{rating}" "{reviews}" "{maps_url}" "{slug}"'
    result = run(cmd, cwd=str(BASE), env_extra=env_vars, timeout=600)
    if result.returncode != 0:
        L(f"generate_site.sh FAILED:\n{result.stderr[-800:]}")
        return False
    L(f"Site generated OK.")
    return True

def step_generate_admin(lead, env_vars):
    slug = lead['slug']
    name = lead['name']
    admin_dir = BUSINESSES / slug / "admin"

    if admin_dir.exists() and (admin_dir / "prisma" / "dev.db").exists():
        L(f"[3/4] Admin already exists for {slug}, skipping.")
        return True

    L(f"[3/4] GENERATING ADMIN for {name}...")
    script = BASE / "generator" / "generate_admin.sh"
    cmd = f'bash "{script}" "{slug}" "{name}"'
    result = run(cmd, cwd=str(BASE), env_extra=env_vars, timeout=600)
    if result.returncode != 0:
        L(f"generate_admin.sh FAILED:\n{result.stderr[-800:]}")
        return False
    L(f"Admin generated OK.")
    return True

def step_deploy(lead, env_vars):
    slug = lead['slug']
    L(f"[4/4] DEPLOYING {slug} to GitHub Pages...")
    script = BASE / "deployer" / "deploy_github.sh"
    cmd = f'bash "{script}" "{slug}"'
    result = run(cmd, cwd=str(BASE), env_extra=env_vars, timeout=300)
    if result.returncode != 0:
        L(f"deploy FAILED:\n{result.stderr[-800:]}")
        return None

    lines = result.stdout.strip().splitlines()
    url = None
    for line in lines:
        if line.startswith("https://") and "github.io" in line:
            url = line.strip()
    if not url:
        username = load_env().get('GITHUB_USERNAME', '')
        url = f"https://{username}.github.io/{slug}-site"

    L(f"Deployed: {url}")
    return url

def main():
    import pytz
    paris = pytz.timezone('Europe/Paris')
    now = datetime.now(paris)
    L(f"{'='*50}")
    L(f"France Leads Automation — {now.strftime('%Y-%m-%d %H:%M')} Paris")
    L(f"Log file: {_log_file}")
    L(f"{'='*50}")

    env = load_env()
    token = env.get('TELEGRAM_BOT_TOKEN')
    chat_id = env.get('TELEGRAM_CHAT_ID')
    env_vars = {k: v for k, v in env.items()}

    ok = step_scrape()
    if not ok:
        msg = "⚠️ France Leads: Scraper failed today. Check logs."
        if token and chat_id:
            send_telegram(token, chat_id, msg)
        return 1

    if not LEADS_FILE.exists():
        L("No leads file found.")
        return 1

    leads = json.loads(LEADS_FILE.read_text(encoding='utf-8'))
    if not leads:
        L("No leads found today.")
        if token and chat_id:
            send_telegram(token, chat_id, "ℹ️ France Leads: Aucun lead trouvé aujourd'hui.")
        return 0

    L(f"Found {len(leads)} lead(s) to process.")
    results = []

    for i, lead in enumerate(leads):
        slug = lead['slug']
        name = lead['name']
        L(f"--- Lead {i+1}/{len(leads)}: {name} ({slug}) ---")

        if already_processed(slug):
            L(f"Already processed today, skipping.")
            continue

        if not step_generate_site(lead, env_vars):
            continue
        if not step_generate_admin(lead, env_vars):
            continue

        url = step_deploy(lead, env_vars)
        if not url:
            continue

        mark_deployed(slug)
        results.append({'lead': lead, 'url': url})

        if token and chat_id:
            category = lead.get('category', 'Business')
            address = lead.get('address', '')
            rating = lead.get('rating', '')
            phone = lead.get('phone', '')
            admin_path = str(BUSINESSES / slug / "admin")
            msg = (
                f"🇫🇷 <b>Nouveau site déployé!</b>\n\n"
                f"🏢 <b>{name}</b>\n"
                f"📂 {category}\n"
                f"📍 {address}\n"
                f"⭐ {rating}/5\n"
                f"📞 {phone}\n\n"
                f"🌐 <b>Site public:</b> {url}\n"
                f"🔐 <b>Admin local:</b> {admin_path}\n"
                f"   Login: admin / admin123\n"
                f"   Port: 3001\n\n"
                f"💡 Démarrer admin:\n"
                f"<code>cd \"{admin_path}\" && npm run dev -- --port 3001</code>"
            )
            send_telegram(token, chat_id, msg)
            L(f"Telegram notification sent.")

        if i < len(leads) - 1:
            L("Waiting 30s before next lead...")
            time.sleep(30)

    if results:
        L(f"DONE — {len(results)} site(s) deployed today.")
        if token and chat_id:
            summary = f"✅ <b>Récapitulatif du jour</b>\n{len(results)} site(s) déployé(s):\n"
            for r in results:
                summary += f"• {r['lead']['name']} → {r['url']}\n"
            send_telegram(token, chat_id, summary)
    else:
        L("No new sites deployed today (all already processed or errors).")

    return 0

if __name__ == '__main__':
    sys.exit(main())
