#!/usr/bin/env python3
"""
template_site.py — World-class single-file HTML site generator.
Michelin-star level design: GSAP, custom cursor, parallax, 3D cards.
Uses __MARKER__ placeholders to avoid conflicts with CSS/JS braces.
"""
import sys, io, json, pathlib, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── THEMES ────────────────────────────────────────────────────────────────────
THEMES = {
    "boulangerie": {
        "bg": "#0D0B08", "surface": "#161310", "accent": "#C9A84C",
        "acc2": "#8B6914", "text": "#F0EAD6", "muted": "#7A6E5F",
        "fd": "Cormorant Garamond", "fb": "Inter",
        "tag": "Artisan Boulanger", "tagline": "L'art du pain depuis des générations",
        "pc": "201,168,76",
    },
    "patisserie": {
        "bg": "#0C0810", "surface": "#140F18", "accent": "#C084BD",
        "acc2": "#8B4A85", "text": "#F5EEF5", "muted": "#7A5F78",
        "fd": "Playfair Display", "fb": "Inter",
        "tag": "Maître Pâtissier", "tagline": "Créations sucrées d'exception",
        "pc": "192,132,189",
    },
    "restaurant": {
        "bg": "#070A0F", "surface": "#0E1219", "accent": "#B8976A",
        "acc2": "#7A5E3A", "text": "#EEE8DC", "muted": "#6E6455",
        "fd": "Cormorant Garamond", "fb": "Inter",
        "tag": "Restaurant Gastronomique", "tagline": "Une expérience culinaire inoubliable",
        "pc": "184,151,106",
    },
    "cafe": {
        "bg": "#09080A", "surface": "#121015", "accent": "#A07850",
        "acc2": "#6B4E2A", "text": "#EDE8E0", "muted": "#6A5C50",
        "fd": "Cormorant Garamond", "fb": "Inter",
        "tag": "Café de Spécialité", "tagline": "L'heure du café, un moment précieux",
        "pc": "160,120,80",
    },
    "default": {
        "bg": "#080A0D", "surface": "#0F1215", "accent": "#C9A84C",
        "acc2": "#8B6914", "text": "#F0EAD6", "muted": "#6E6860",
        "fd": "Cormorant Garamond", "fb": "Inter",
        "tag": "Commerce d'Exception", "tagline": "Un savoir-faire unique",
        "pc": "201,168,76",
    },
}

def get_theme(category):
    cat = (category or "").lower()
    # Normalize French accents for matching
    cat_norm = cat.replace("â","a").replace("é","e").replace("è","e").replace("ê","e").replace("î","i")
    mapping = [("boulangerie","boulangerie"), ("patisserie","patisserie"),
               ("restaurant","restaurant"), ("cafe","cafe"), ("café","cafe")]
    for key, theme_key in mapping:
        if key in cat_norm or key in cat:
            return THEMES[theme_key]
    return THEMES["default"]

# ── OFFERINGS PER CATEGORY ────────────────────────────────────────────────────
OFFERINGS = {
    "boulangerie": [
        ("🥖", "Pain au Levain", "Fermentation lente 24h, croûte dorée, mie alvéolée"),
        ("🥐", "Viennoiseries", "Beurre AOC Charentes-Poitou, feuilletage 27 couches"),
        ("🎂", "Pièces de Fête", "Créations sur-mesure pour vos occasions uniques"),
    ],
    "patisserie": [
        ("🎂", "Entremets", "Architecture sucrée, textures contrastées"),
        ("🍫", "Chocolats Grand Cru", "Ganaches signature, origine unique"),
        ("🧁", "Petits Fours", "L'élégance française à portée de main"),
    ],
    "restaurant": [
        ("🍽️", "Menu Dégustation", "7 services, accords mets et vins"),
        ("🥗", "Carte de Saison", "Produits frais sélectionnés chaque matin"),
        ("🍷", "Cave à Vins", "Plus de 200 références, sommelier dédié"),
    ],
    "cafe": [
        ("☕", "Single Origin", "Grains de spécialité, torréfaction artisanale"),
        ("🧁", "Pâtisseries Maison", "Recettes du chef revisitées chaque semaine"),
        ("🫖", "Sélection de Thés", "Collection de jardins du monde entier"),
    ],
}

def get_offerings(category):
    cat = (category or "").lower()
    cat_norm = cat.replace("â","a").replace("é","e").replace("è","e").replace("î","i")
    for key in OFFERINGS:
        if key in cat_norm or key in cat:
            return OFFERINGS[key]
    return OFFERINGS["restaurant"]

# ── STARS HTML ────────────────────────────────────────────────────────────────
def stars_html(rating):
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    s = ""
    for _ in range(full):  s += '<span class="star">★</span>'
    for _ in range(half):  s += '<span class="star" style="opacity:.45">★</span>'
    for _ in range(empty): s += '<span class="star" style="opacity:.18">★</span>'
    return s

# ── HTML TEMPLATE ─────────────────────────────────────────────────────────────
# Uses __MARKER__ tokens — safe from CSS/JS curly brace conflicts.
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__NAME__ — __TAG__</title>
<meta name="description" content="__NAME__, __TAG__ à __CITY__. __TAGLINE__. Noté __RATING__/5 par __REVIEWS__ clients.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;overflow-x:hidden}
:root{
  --bg:__BG__;
  --surface:__SURFACE__;
  --acc:__ACCENT__;
  --text:__TEXT__;
  --muted:__MUTED__;
}
body{
  background:var(--bg);color:var(--text);
  font-family:'__FB__',sans-serif;font-weight:300;
  overflow-x:hidden;cursor:none;
}
::selection{background:var(--acc);color:var(--bg)}
::-webkit-scrollbar{width:2px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--acc)}

/* CURSOR */
#cur-dot,#cur-ring{
  position:fixed;top:0;left:0;z-index:9999;pointer-events:none;
  border-radius:50%;mix-blend-mode:difference;
}
#cur-dot{width:6px;height:6px;background:#fff;transform:translate(-50%,-50%)}
#cur-ring{
  width:38px;height:38px;border:1px solid rgba(255,255,255,.32);
  transform:translate(-50%,-50%);
  transition:width .35s,height .35s,opacity .35s;
}
.has-hover #cur-ring{width:62px;height:62px;opacity:.75}

/* NOISE OVERLAY */
.noise{
  position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.032;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:200px;animation:noiseShift 8s steps(1) infinite;
}
@keyframes noiseShift{
  0%{background-position:0 0}20%{background-position:-45px 28px}
  40%{background-position:28px -18px}60%{background-position:-8px 48px}
  80%{background-position:48px 8px}100%{background-position:0 0}
}

/* PRELOADER */
#preloader{
  position:fixed;inset:0;z-index:9998;background:var(--bg);
  display:flex;align-items:center;justify-content:center;flex-direction:column;gap:22px;
}
#pre-name{
  font-family:'__FD__',serif;font-size:clamp(1.8rem,5.5vw,4.2rem);
  font-weight:300;letter-spacing:.18em;color:var(--acc);
  opacity:0;transform:translateY(22px);
}
#pre-bar{height:1px;width:0;background:var(--acc);max-width:170px}
#pre-pct{font-size:.6rem;letter-spacing:.28em;color:var(--muted);opacity:0;margin-top:-8px}

/* NAV */
nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  padding:26px 6vw;display:flex;align-items:center;justify-content:space-between;
  transition:padding .4s,background .4s,backdrop-filter .4s;
}
nav.scrolled{
  padding:14px 6vw;
  background:rgba(8,8,10,.9);backdrop-filter:blur(22px);
  border-bottom:1px solid rgba(255,255,255,.04);
}
.nav-logo{
  font-family:'__FD__',serif;font-size:1.2rem;letter-spacing:.12em;
  color:var(--acc);text-decoration:none;font-weight:400;
}
.nav-links{display:flex;gap:38px;list-style:none}
.nav-links a{
  font-size:.66rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted);text-decoration:none;transition:color .3s;
}
.nav-links a:hover{color:var(--acc)}
@media(max-width:768px){.nav-links{display:none}}

/* HERO */
#hero{
  position:relative;height:100svh;min-height:600px;
  display:flex;align-items:center;justify-content:center;overflow:hidden;
}
#hero-canvas{position:absolute;inset:0;z-index:0}
.hero-content{position:relative;z-index:2;text-align:center;padding:0 5vw}
.hero-eye{
  font-size:.63rem;letter-spacing:.38em;text-transform:uppercase;
  color:var(--acc);margin-bottom:26px;opacity:0;transform:translateY(10px);
}
.hero-title{
  font-family:'__FD__',serif;
  font-size:clamp(3rem,8.5vw,8.5rem);
  font-weight:300;line-height:.9;letter-spacing:-.02em;
  margin-bottom:26px;overflow:visible;
}
.hc{display:inline-block;opacity:0;transform:translateY(80%)}
.hero-sub{
  font-size:clamp(.78rem,1.35vw,.98rem);letter-spacing:.1em;
  color:var(--muted);font-style:italic;margin-bottom:46px;
  opacity:0;transform:translateY(10px);
}
.hero-cta{
  display:inline-flex;align-items:center;gap:13px;
  font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--acc);text-decoration:none;opacity:0;transition:gap .35s;
}
.hero-cta:hover{gap:21px}
.hcta-line{width:34px;height:1px;background:var(--acc);display:block;transition:width .35s}
.hero-cta:hover .hcta-line{width:54px}
.scroll-hint{
  position:absolute;bottom:34px;left:50%;transform:translateX(-50%);
  display:flex;flex-direction:column;align-items:center;gap:8px;
  font-size:.56rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--muted);opacity:0;z-index:2;
}
.scroll-bar{
  width:1px;height:52px;
  background:linear-gradient(var(--acc),transparent);
  animation:sPulse 1.6s ease-in-out infinite;
}
@keyframes sPulse{
  0%{transform:scaleY(0);transform-origin:top}
  50%{transform:scaleY(1);transform-origin:top}
  51%{transform:scaleY(1);transform-origin:bottom}
  100%{transform:scaleY(0);transform-origin:bottom}
}

/* STATS */
.stats{
  display:grid;grid-template-columns:repeat(3,1fr);
  border-top:1px solid rgba(255,255,255,.05);
  border-bottom:1px solid rgba(255,255,255,.05);
  gap:1px;background:rgba(255,255,255,.05);
}
.stat{
  background:var(--bg);padding:42px 4vw;text-align:center;
  opacity:0;transform:translateY(18px);
}
.stat-big{
  font-family:'__FD__',serif;font-size:clamp(2rem,3.8vw,3.8rem);
  font-weight:300;color:var(--acc);display:block;line-height:1;margin-bottom:8px;
}
.stat-lbl{font-size:.58rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted)}
.stars-row{display:flex;justify-content:center;gap:3px;font-size:1.1rem;color:var(--acc);margin-bottom:6px}

/* SECTIONS */
section{padding:108px 6vw;position:relative}
.sec-tag{
  font-size:.6rem;letter-spacing:.32em;text-transform:uppercase;
  color:var(--acc);margin-bottom:16px;display:block;
}
.sec-title{
  font-family:'__FD__',serif;
  font-size:clamp(1.9rem,4.2vw,3.6rem);
  font-weight:300;line-height:1.1;margin-bottom:26px;
}
.sec-title em{font-style:italic;color:var(--acc)}
.rw{overflow:hidden;display:block}
.ri{display:inline-block;transform:translateY(105%)}

/* ABOUT */
.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:76px;align-items:center}
@media(max-width:900px){.about-grid{grid-template-columns:1fr}}
.about-body p{color:var(--muted);line-height:1.95;font-size:.88rem;margin-bottom:16px}
.about-img{
  position:relative;overflow:hidden;aspect-ratio:4/5;
  clip-path:inset(100% 0 0 0);
}
.about-img-fill{
  width:100%;height:100%;
  background:linear-gradient(135deg,__SURFACE__ 0%,rgba(__PC__,.1) 50%,__SURFACE__ 100%);
  display:flex;align-items:center;justify-content:center;
  font-family:'__FD__',serif;font-size:5.5rem;color:var(--acc);opacity:.1;
}
.about-img::after{
  content:'';position:absolute;inset:0;
  border:1px solid rgba(__PC__,.1);pointer-events:none;
}

/* OFFERINGS */
#offerings{background:var(--surface)}
.off-grid{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:2px;margin-top:52px;
}
@media(max-width:900px){.off-grid{grid-template-columns:1fr}}
.off-card{
  background:var(--bg);padding:42px 34px;position:relative;
  overflow:hidden;transition:background .4s;
  opacity:0;transform:translateY(38px);
}
.off-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(__PC__,.06) 0%,transparent 60%);
  opacity:0;transition:opacity .4s;
}
.off-card:hover{background:#0e0d0a}
.off-card:hover::before{opacity:1}
.off-num{
  position:absolute;top:26px;right:26px;
  font-family:'__FD__',serif;font-size:2.6rem;font-weight:300;
  color:rgba(255,255,255,.035);line-height:1;
}
.off-icon{font-size:1.7rem;margin-bottom:18px;display:block}
.off-name{
  font-family:'__FD__',serif;font-size:1.35rem;font-weight:400;
  margin-bottom:9px;transition:color .3s;
}
.off-card:hover .off-name{color:var(--acc)}
.off-desc{font-size:.8rem;color:var(--muted);line-height:1.75}

/* QUOTE SECTION */
#quote-sec{
  min-height:62vh;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(180deg,var(--bg) 0%,rgba(__PC__,.055) 50%,var(--bg) 100%);
  text-align:center;padding:90px 6vw;
}
.big-quote{
  font-family:'__FD__',serif;
  font-size:clamp(1.6rem,3.5vw,2.9rem);
  font-weight:300;line-height:1.45;font-style:italic;
  color:var(--text);max-width:800px;
}
.div-line{width:50px;height:1px;background:var(--acc);margin:28px auto}

/* INFO */
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:76px;margin-top:52px}
@media(max-width:900px){.info-grid{grid-template-columns:1fr}}
.info-block h3{
  font-family:'__FD__',serif;font-size:1.55rem;
  font-weight:300;margin-bottom:26px;
}
.hr{
  display:flex;justify-content:space-between;align-items:center;
  padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);
  font-size:.8rem;color:var(--muted);
  opacity:0;transform:translateX(-18px);
}
.ci{
  display:flex;align-items:flex-start;gap:14px;
  padding:16px 0;border-bottom:1px solid rgba(255,255,255,.05);
  opacity:0;transform:translateX(-18px);
}
.ci-icon{
  width:28px;height:28px;border:1px solid rgba(__PC__,.28);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.8rem;flex-shrink:0;color:var(--acc);
}
.ci-label{font-size:.56rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.ci-val{font-size:.84rem;color:var(--text)}
.ci-val a{color:inherit;text-decoration:none;transition:color .3s}
.ci-val a:hover{color:var(--acc)}

/* CTA */
#cta{
  text-align:center;padding:124px 6vw;
  background:var(--surface);overflow:hidden;position:relative;
}
#cta-glow{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:650px;height:650px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(__PC__,.065) 0%,transparent 70%);
  pointer-events:none;
}
.cta-title{
  font-family:'__FD__',serif;
  font-size:clamp(2.2rem,5.5vw,5.2rem);
  font-weight:300;line-height:.95;margin-bottom:44px;
}
.cta-btns{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.btn{
  display:inline-flex;align-items:center;gap:9px;
  padding:15px 34px;border:1px solid var(--acc);
  color:var(--acc);font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;
  text-decoration:none;position:relative;overflow:hidden;transition:color .4s;
}
.btn::before{
  content:'';position:absolute;inset:0;background:var(--acc);
  transform:translateX(-102%);transition:transform .4s cubic-bezier(.76,0,.24,1);
}
.btn:hover{color:var(--bg)}
.btn:hover::before{transform:translateX(0)}
.btn span{position:relative;z-index:1}

/* FOOTER */
footer{
  padding:48px 6vw;border-top:1px solid rgba(255,255,255,.05);
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;
}
.ft-logo{font-family:'__FD__',serif;font-size:1rem;color:var(--acc);letter-spacing:.1em}
.ft-copy{font-size:.62rem;color:var(--muted);letter-spacing:.08em}
</style>
</head>
<body>

<div id="cur-dot"></div>
<div id="cur-ring"></div>
<div class="noise"></div>

<!-- PRELOADER -->
<div id="preloader">
  <div id="pre-name">__NAME__</div>
  <div id="pre-bar"></div>
  <div id="pre-pct">0%</div>
</div>

<!-- NAV -->
<nav id="nav">
  <a href="#" class="nav-logo">__INITIAL__.</a>
  <ul class="nav-links">
    <li><a href="#about">À propos</a></li>
    <li><a href="#offerings">Spécialités</a></li>
    <li><a href="#info">Contact</a></li>
  </ul>
</nav>

<!-- HERO -->
<section id="hero">
  <canvas id="hero-canvas"></canvas>
  <div class="hero-content">
    <p class="hero-eye">__CITY__ &nbsp;·&nbsp; __TAG__</p>
    <h1 class="hero-title" id="hero-title">__NAME__</h1>
    <p class="hero-sub">__TAGLINE__</p>
    <a href="#about" class="hero-cta">
      <span class="hcta-line"></span>
      <span>Découvrir</span>
    </a>
  </div>
  <div class="scroll-hint">
    <span>Scroll</span>
    <div class="scroll-bar"></div>
  </div>
</section>

<!-- STATS -->
<div class="stats">
  <div class="stat" id="stat-0">
    <div class="stars-row">__STARS__</div>
    <span class="stat-big" id="cnt-rating">__RATING__</span>
    <span class="stat-lbl">Note Google</span>
  </div>
  <div class="stat" id="stat-1">
    <span class="stat-big" id="cnt-reviews">0</span>
    <span class="stat-lbl">Avis clients</span>
  </div>
  <div class="stat" id="stat-2">
    <span class="stat-big" style="font-size:clamp(1rem,2.4vw,1.7rem)">#__CITY12__</span>
    <span class="stat-lbl">__CITY__</span>
  </div>
</div>

<!-- ABOUT -->
<section id="about">
  <div class="about-grid">
    <div class="about-body">
      <span class="sec-tag">Notre histoire</span>
      <h2 class="sec-title">
        <span class="rw"><span class="ri">Un savoir-faire</span></span><br>
        <span class="rw"><span class="ri"><em>d'exception</em></span></span>
      </h2>
      <p>Chez <strong>__NAME__</strong>, chaque création est le fruit d'une passion
         transmise et d'une exigence absolue envers la qualité. Nous sélectionnons
         les meilleurs ingrédients et appliquons des techniques ancestrales
         revisitées avec modernité.</p>
      <p>Reconnus par __REVIEWS__ clients avec une note de __RATING__/5, nous
         incarnons l'excellence artisanale française.</p>
      <p style="margin-top:30px">
        <a href="#offerings" class="hero-cta" style="opacity:1">
          <span class="hcta-line"></span><span>Nos spécialités</span>
        </a>
      </p>
    </div>
    <div class="about-img" id="about-img">
      <div class="about-img-fill">✦</div>
    </div>
  </div>
</section>

<!-- OFFERINGS -->
<section id="offerings">
  <span class="sec-tag">Ce que nous offrons</span>
  <h2 class="sec-title">
    <span class="rw"><span class="ri">Nos <em>spécialités</em></span></span>
  </h2>
  <div class="off-grid">
__OFFERING_CARDS__
  </div>
</section>

<!-- QUOTE -->
<section id="quote-sec">
  <div>
    <div class="div-line"></div>
    <p class="big-quote">
      « __TAGLINE__. Une adresse incontournable à __CITY__. »
    </p>
    <div class="div-line"></div>
    <span class="sec-tag" style="display:block;text-align:center">— __NAME__, __CITY__</span>
  </div>
</section>

<!-- INFO -->
<section id="info">
  <span class="sec-tag">Nous trouver</span>
  <h2 class="sec-title">
    <span class="rw"><span class="ri">Horaires &amp; <em>Contact</em></span></span>
  </h2>
  <div class="info-grid">
    <div class="info-block">
      <h3>Horaires d'ouverture</h3>
__HOURS_ROWS__
    </div>
    <div class="info-block">
      <h3>Informations</h3>
__CONTACT_ITEMS__
    </div>
  </div>
</section>

<!-- CTA -->
<section id="cta">
  <div id="cta-glow"></div>
  <h2 class="cta-title">
    <span class="rw"><span class="ri">Venez nous</span></span><br>
    <span class="rw"><span class="ri"><em>rendre visite</em></span></span>
  </h2>
  <div class="cta-btns">
__CTA_BTNS__
  </div>
</section>

<!-- FOOTER -->
<footer>
  <span class="ft-logo">__NAME__</span>
  <span class="ft-copy">__ADDRESS__</span>
  <span class="ft-copy">© __NAME__ · __CITY__</span>
</footer>

<script>
gsap.registerPlugin(ScrollTrigger);

/* CURSOR */
const dot = document.getElementById('cur-dot');
const ring = document.getElementById('cur-ring');
let mx=0, my=0, rx=0, ry=0;
document.addEventListener('mousemove', e => { mx=e.clientX; my=e.clientY; });
document.querySelectorAll('a,button').forEach(el => {
  el.addEventListener('mouseenter', () => document.body.classList.add('has-hover'));
  el.addEventListener('mouseleave', () => document.body.classList.remove('has-hover'));
});
(function tick() {
  rx += (mx-rx)*.11; ry += (my-ry)*.11;
  dot.style.left=mx+'px'; dot.style.top=my+'px';
  ring.style.left=rx+'px'; ring.style.top=ry+'px';
  requestAnimationFrame(tick);
})();

/* PARTICLE CANVAS */
const canvas = document.getElementById('hero-canvas');
const ctx = canvas.getContext('2d');
let W, H, pts = [];
function resize() { W=canvas.width=innerWidth; H=canvas.height=innerHeight; }
resize();
window.addEventListener('resize', () => { resize(); initPts(); });
function mkPt() {
  return {
    x:Math.random()*W, y:Math.random()*H,
    vx:(Math.random()-.5)*.25, vy:(Math.random()-.5)*.25,
    r:Math.random()*1.4+.4, a:Math.random()*.42+.08,
    life:Math.random()*240+100, age:0
  };
}
function initPts() { pts=[]; for(let i=0;i<90;i++) pts.push(mkPt()); }
initPts();
function frame() {
  ctx.clearRect(0,0,W,H);
  const g = ctx.createRadialGradient(W/2,H*.38,0,W/2,H*.38,W*.55);
  g.addColorStop(0,'rgba(__PC__,.07)');
  g.addColorStop(1,'transparent');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  pts.forEach((p,i) => {
    p.x+=p.vx; p.y+=p.vy; p.age++;
    if(p.age>p.life){ pts[i]=mkPt(); return; }
    const f=p.age<25?p.age/25:p.age>p.life-25?(p.life-p.age)/25:1;
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle=`rgba(__PC__,${p.a*f})`; ctx.fill();
  });
  for(let i=0;i<pts.length;i++) {
    for(let j=i+1;j<pts.length;j++) {
      const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<110) {
        ctx.beginPath();
        ctx.moveTo(pts[i].x,pts[i].y);
        ctx.lineTo(pts[j].x,pts[j].y);
        ctx.strokeStyle=`rgba(__PC__,${.1*(1-d/110)})`;
        ctx.lineWidth=.4; ctx.stroke();
      }
    }
  }
  requestAnimationFrame(frame);
}
frame();

/* PRELOADER */
const pre = document.getElementById('preloader');
const preName = document.getElementById('pre-name');
const preBar = document.getElementById('pre-bar');
const prePct = document.getElementById('pre-pct');
gsap.to(preName, { opacity:1, y:0, duration:.7, ease:'power3.out', delay:.1 });
gsap.to(prePct, { opacity:1, duration:.4, delay:.3 });
gsap.fromTo({ v:0 }, { v:100 }, {
  duration:1.2, delay:.2, ease:'power2.inOut',
  onUpdate: function() {
    const p = Math.round(this.targets()[0].v);
    prePct.textContent = p + '%';
    preBar.style.width = p + 'px';
  },
  onComplete: () => {
    gsap.to(pre, {
      opacity:0, duration:.5, delay:.12,
      onComplete: () => { pre.remove(); startAnims(); }
    });
  }
});

/* MAIN ANIMATIONS */
function startAnims() {

  /* Hero title char-by-char */
  const titleEl = document.getElementById('hero-title');
  const raw = titleEl.textContent;
  titleEl.innerHTML = raw.split('').map(c =>
    c.trim() === '' ? ' ' : `<span class="hc">${c}</span>`
  ).join('');
  gsap.to('.hc', { opacity:1, y:0, stagger:.04, duration:.7, ease:'power3.out', delay:.05 });
  gsap.to('.hero-eye', { opacity:1, y:0, duration:.7, delay:.4 });
  gsap.to('.hero-sub', { opacity:1, y:0, duration:.7, delay:.65 });
  gsap.to('.hero-cta', { opacity:1, duration:.7, delay:.88 });
  gsap.to('.scroll-hint', { opacity:1, duration:.7, delay:1.1 });

  /* Nav on scroll */
  ScrollTrigger.create({
    trigger:'body', start:'80px top',
    onEnter:()=>document.getElementById('nav').classList.add('scrolled'),
    onLeaveBack:()=>document.getElementById('nav').classList.remove('scrolled'),
  });

  /* Stats reveal */
  [0,1,2].forEach(i => {
    gsap.to(`#stat-${i}`, {
      opacity:1, y:0, duration:.7, ease:'power3.out', delay:i*.1,
      scrollTrigger:{ trigger:'.stats', start:'top 87%' }
    });
  });

  /* Reviews counter */
  ScrollTrigger.create({ trigger:'.stats', start:'top 87%', once:true, onEnter: () => {
    gsap.fromTo({ v:0 }, { v:__REVIEWS_NUM__ }, {
      duration:1.8, ease:'power2.out',
      onUpdate: function() {
        document.getElementById('cnt-reviews').textContent = Math.round(this.targets()[0].v);
      }
    });
  }});

  /* Reveal lines */
  document.querySelectorAll('.ri').forEach(el => {
    gsap.to(el, { y:0, duration:.9, ease:'power3.out',
      scrollTrigger:{ trigger:el, start:'top 92%' }
    });
  });

  /* About image clip reveal */
  gsap.to('#about-img', {
    clipPath:'inset(0% 0 0 0)', duration:1.3, ease:'power4.inOut',
    scrollTrigger:{ trigger:'#about-img', start:'top 80%' }
  });

  /* Offering cards */
  gsap.to('.off-card', {
    opacity:1, y:0, stagger:.14, duration:.8, ease:'power3.out',
    scrollTrigger:{ trigger:'.off-grid', start:'top 83%' }
  });

  /* Hours + contact rows */
  gsap.to('.hr,.ci', {
    opacity:1, x:0, stagger:.07, duration:.6, ease:'power2.out',
    scrollTrigger:{ trigger:'#info', start:'top 80%' }
  });

  /* CTA parallax glow */
  gsap.to('#cta-glow', { y:-55, ease:'none',
    scrollTrigger:{ trigger:'#cta', scrub:1 }
  });

  /* Magnetic buttons */
  document.querySelectorAll('.btn,.hero-cta').forEach(btn => {
    btn.addEventListener('mousemove', e => {
      const r = btn.getBoundingClientRect();
      const x = (e.clientX - r.left - r.width/2) * .17;
      const y = (e.clientY - r.top - r.height/2) * .17;
      gsap.to(btn, { x, y, duration:.3, ease:'power2.out' });
    });
    btn.addEventListener('mouseleave', () =>
      gsap.to(btn, { x:0, y:0, duration:.6, ease:'elastic.out(1,.35)' })
    );
  });
}
</script>
</body>
</html>
"""

# ── GENERATOR ────────────────────────────────────────────────────────────────
def generate_html(lead, github_url=""):
    name     = lead.get("name", "")
    category = lead.get("category", "")
    address  = lead.get("address", "")
    phone    = lead.get("phone", "")
    rating   = float(lead.get("rating") or 4.8)
    reviews  = int(lead.get("review_count") or 0)
    maps_url = lead.get("maps_url") or lead.get("google_maps_url", "")
    hours    = lead.get("hours") or []
    city     = address.split(",")[-2].strip() if "," in address else "France"
    initial  = name[0].upper() if name else "A"

    t = get_theme(category)
    items = get_offerings(category)

    # Offering cards HTML
    cards = ""
    for i, (icon, title, desc) in enumerate(items):
        cards += (f'    <div class="off-card">\n'
                  f'      <span class="off-num">0{i+1}</span>\n'
                  f'      <span class="off-icon">{icon}</span>\n'
                  f'      <h3 class="off-name">{title}</h3>\n'
                  f'      <p class="off-desc">{desc}</p>\n'
                  f'    </div>\n')

    # Hours rows
    hr_rows = ""
    if hours:
        for h in hours:
            hr_rows += f'    <div class="hr"><span>{h}</span></div>\n'
    else:
        hr_rows = ('    <div class="hr"><span>Lun – Ven</span><span>07h – 20h</span></div>\n'
                   '    <div class="hr"><span>Samedi</span><span>07h – 21h</span></div>\n'
                   '    <div class="hr"><span>Dimanche</span><span>08h – 18h</span></div>\n')

    # Contact items
    ci = (f'    <div class="ci">\n'
          f'      <div class="ci-icon">📍</div>\n'
          f'      <div><div class="ci-label">Adresse</div>'
          f'<div class="ci-val">{address}</div></div>\n'
          f'    </div>\n')
    if phone:
        ci += (f'    <div class="ci">\n'
               f'      <div class="ci-icon">📞</div>\n'
               f'      <div><div class="ci-label">Téléphone</div>'
               f'<div class="ci-val"><a href="tel:{phone}">{phone}</a></div></div>\n'
               f'    </div>\n')
    if maps_url:
        ci += (f'    <div class="ci">\n'
               f'      <div class="ci-icon">🗺</div>\n'
               f'      <div><div class="ci-label">Itinéraire</div>'
               f'<div class="ci-val"><a href="{maps_url}" target="_blank" rel="noopener">'
               f'Voir sur Google Maps →</a></div></div>\n'
               f'    </div>\n')

    # CTA buttons
    btns = ""
    if phone:
        btns += f'    <a href="tel:{phone}" class="btn"><span>📞 Appeler</span></a>\n'
    if maps_url:
        btns += (f'    <a href="{maps_url}" target="_blank" rel="noopener" class="btn">'
                 f'<span>📍 Itinéraire</span></a>\n')
    if not btns:
        btns = '    <a href="#info" class="btn"><span>Nous contacter</span></a>\n'

    html = HTML_TEMPLATE
    replacements = {
        "__NAME__":          name,
        "__TAG__":           t["tag"],
        "__TAGLINE__":       t["tagline"],
        "__CITY__":          city,
        "__CITY12__":        city.replace(" ", "")[:12],
        "__INITIAL__":       initial,
        "__ADDRESS__":       address,
        "__RATING__":        str(rating),
        "__REVIEWS__":       str(reviews),
        "__REVIEWS_NUM__":   str(reviews),
        "__STARS__":         stars_html(rating),
        "__BG__":            t["bg"],
        "__SURFACE__":       t["surface"],
        "__ACCENT__":        t["accent"],
        "__TEXT__":          t["text"],
        "__MUTED__":         t["muted"],
        "__PC__":            t["pc"],
        "__FD__":            t["fd"],
        "__FB__":            t["fb"],
        "__OFFERING_CARDS__": cards,
        "__HOURS_ROWS__":    hr_rows,
        "__CONTACT_ITEMS__": ci,
        "__CTA_BTNS__":      btns,
    }
    for marker, value in replacements.items():
        html = html.replace(marker, str(value))
    return html

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("leads_file")
    parser.add_argument("output_dir")
    parser.add_argument("--github-username", default="")
    args = parser.parse_args()

    leads = json.loads(pathlib.Path(args.leads_file).read_text(encoding='utf-8'))
    out_base = pathlib.Path(args.output_dir)

    for lead in leads:
        slug = lead.get("slug", "")
        site_dir = out_base / slug
        site_dir.mkdir(parents=True, exist_ok=True)

        github_url = (f"https://{args.github_username}.github.io/{slug}-site"
                      if args.github_username else "")
        html = generate_html(lead, github_url)
        (site_dir / "index.html").write_text(html, encoding='utf-8')
        (site_dir / ".nojekyll").touch()

        info = {k: lead.get(k) for k in
                ["name", "category", "address", "phone", "rating", "review_count", "slug"]}
        info["public_site"] = github_url
        (site_dir / "client_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"✅ Generated: {slug}")

if __name__ == "__main__":
    main()
