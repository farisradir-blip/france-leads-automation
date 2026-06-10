#!/usr/bin/env python3
"""
template_site.py — World-class single-file HTML site generator.
Inspired by taste-skill (anti-slop), ui-ux-pro-max (67 styles, 161 palettes),
vercel web-design-guidelines. Three.js 3D + Lenis smooth scroll + GSAP.
"""
import sys, io, json, pathlib, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

THEMES = {
    "boulangerie": {
        "bg":"#0A0905","s1":"#12100A","s2":"#1A1710",
        "acc":"#D4A843","acc2":"#8B6A1F","acc3":"#F0D080",
        "txt":"#F2ECE0","muted":"#7A6E5A","border":"rgba(212,168,67,.12)",
        "fd":"Cormorant Garamond","fb":"DM Sans",
        "tag":"Artisan Boulanger","city_tag":"Boulangerie de Quartier",
        "tagline":"L'art du pain depuis des générations",
        "philosophy":"Chaque levain est une promesse. Chaque fournée, un hommage.",
        "pc":"212,168,67","geo_color":"0.83,0.66,0.26",
        "items":[
            ("Pain au Levain","Fermentation 48h, croûte dorée, mie alvéolée — notre signature."),
            ("Viennoiseries","Beurre AOP, feuilletage 27 tours. L'excellence à chaque bouchée."),
            ("Créations Saisonnières","Spécialités éphémères selon les saisons et l'inspiration du chef."),
        ],
    },
    "patisserie": {
        "bg":"#09080C","s1":"#110F16","s2":"#17141E",
        "acc":"#C87DC8","acc2":"#8B4A8B","acc3":"#E8B8E8",
        "txt":"#F5F0F8","muted":"#7A6878","border":"rgba(200,125,200,.12)",
        "fd":"Playfair Display","fb":"DM Sans",
        "tag":"Maître Pâtissier","city_tag":"Pâtisserie d'Excellence",
        "tagline":"Créations sucrées d'exception, élevées au rang d'art",
        "philosophy":"Le sucre est notre matière. La beauté, notre obsession.",
        "pc":"200,125,200","geo_color":"0.78,0.49,0.78",
        "items":[
            ("Entremets","Architecture sucrée, textures contrastées, saveurs complexes."),
            ("Chocolats Grand Cru","Origine unique, ganaches signature, finitions à la feuille d'or."),
            ("Petits Fours","L'élégance française condensée en une bouchée parfaite."),
        ],
    },
    "restaurant": {
        "bg":"#07080C","s1":"#0D0F15","s2":"#13151C",
        "acc":"#B89060","acc2":"#7A5A30","acc3":"#D4B888",
        "txt":"#EDE8DC","muted":"#6E6455","border":"rgba(184,144,96,.12)",
        "fd":"Cormorant Garamond","fb":"DM Sans",
        "tag":"Restaurant Gastronomique","city_tag":"Table d'Exception",
        "tagline":"Une expérience culinaire qui transcende le repas",
        "philosophy":"Chaque assiette est un voyage. Chaque service, une histoire.",
        "pc":"184,144,96","geo_color":"0.72,0.56,0.38",
        "items":[
            ("Menu Dégustation","7 actes, 7 émotions. Accords mets et vins sur demande."),
            ("Carte de Saison","Producteurs sélectionnés, cueillette du matin, exécution du soir."),
            ("Table du Chef","Expérience privilégiée en cuisine, face aux fourneaux."),
        ],
    },
    "cafe": {
        "bg":"#090807","s1":"#110F0D","s2":"#181512",
        "acc":"#A07848","acc2":"#6B4E28","acc3":"#C89868",
        "txt":"#EDE8E0","muted":"#6A5C50","border":"rgba(160,120,72,.12)",
        "fd":"Cormorant Garamond","fb":"DM Sans",
        "tag":"Café de Spécialité","city_tag":"Café Artisanal",
        "tagline":"L'heure du café élevée au rang de rituel",
        "philosophy":"Un grain. Un terroir. Un instant suspendu.",
        "pc":"160,120,72","geo_color":"0.63,0.47,0.28",
        "items":[
            ("Single Origin","Grains de spécialité, torréfaction artisanale en micro-lots."),
            ("Pâtisseries Maison","Recettes exclusives du chef, renouvelées chaque semaine."),
            ("Sélection de Thés","Jardins du monde entier, préparation au gramme près."),
        ],
    },
    "default": {
        "bg":"#08090C","s1":"#0F1015","s2":"#15161C",
        "acc":"#C9A84C","acc2":"#8B6914","acc3":"#E8C870",
        "txt":"#F0EAD6","muted":"#6E6860","border":"rgba(201,168,76,.12)",
        "fd":"Cormorant Garamond","fb":"DM Sans",
        "tag":"Commerce d'Exception","city_tag":"Adresse Incontournable",
        "tagline":"Un savoir-faire unique, transmis avec passion",
        "philosophy":"L'excellence n'est pas un accident. C'est un choix quotidien.",
        "pc":"201,168,76","geo_color":"0.79,0.66,0.30",
        "items":[
            ("Notre Signature","L'expertise de nos artisans au service de votre satisfaction."),
            ("Sélection Exclusive","Des produits et services soigneusement choisis pour vous."),
            ("Service Personnalisé","Une attention particulière pour chaque client, chaque visite."),
        ],
    },
}

def get_theme(cat):
    c = (cat or "").lower()
    cn = c.replace("â","a").replace("é","e").replace("è","e").replace("ê","e")
    for k in ["boulangerie","patisserie","restaurant","cafe"]:
        if k in cn or k in c: return THEMES[k]
    return THEMES["default"]

def stars_svg(r):
    f=int(r); h=1 if r-f>=0.5 else 0; e=5-f-h
    return "".join(["★"]*f + (["⯨"] if h else []) + ["☆"]*e)

HTML = """\
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__NAME__ — __TAG__</title>
<meta name="description" content="__NAME__, __TAG__ à __CITY__. __TAGLINE__. Note __RATING__/5.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Playfair+Display:ital,wght@0,400;0,500;0,700;1,400;1,700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://unpkg.com/@studio-freight/lenis@1.0.42/dist/lenis.min.js"></script>
<style>
/* ── RESET & BASE ─────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{overflow-x:hidden}
:root{
  --bg:__BG__;--s1:__S1__;--s2:__S2__;
  --acc:__ACC__;--acc2:__ACC2__;--acc3:__ACC3__;
  --txt:__TXT__;--muted:__MUTED__;--border:__BORDER__;
  --fd:'__FD__';--fb:'__FB__';
}
body{
  background:var(--bg);color:var(--txt);
  font-family:var(--fb),sans-serif;font-weight:300;
  overflow-x:hidden;cursor:none;
}
::selection{background:var(--acc);color:var(--bg)}
::-webkit-scrollbar{width:1px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--acc)}

/* ── CURSOR ───────────────────────────────────── */
#c1,#c2{
  position:fixed;border-radius:50%;pointer-events:none;
  z-index:10000;mix-blend-mode:difference;top:0;left:0;
}
#c1{width:7px;height:7px;background:#fff;transform:translate(-50%,-50%)}
#c2{
  width:36px;height:36px;border:1px solid rgba(255,255,255,.3);
  transform:translate(-50%,-50%);
  transition:width .4s,height .4s,border-color .4s;
}
.is-hovering #c2{width:56px;height:56px;border-color:rgba(255,255,255,.6)}

/* ── NOISE ────────────────────────────────────── */
#noise{
  position:fixed;inset:0;z-index:2;pointer-events:none;
  opacity:.04;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E");
  background-size:256px;animation:ns 6s steps(1) infinite;
}
@keyframes ns{
  0%{background-position:0 0}16%{background-position:-40px 20px}
  33%{background-position:20px -30px}50%{background-position:-10px 40px}
  66%{background-position:30px 10px}83%{background-position:-20px -10px}
}

/* ── PRELOADER ────────────────────────────────── */
#loader{
  position:fixed;inset:0;z-index:9999;background:var(--bg);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:0;
}
.l-line{width:1px;height:0;background:var(--acc);position:absolute;top:0}
.l-line-h{height:1px;width:0;background:var(--acc);position:absolute;left:0}
#l-name{
  font-family:var(--fd),serif;
  font-size:clamp(1.5rem,5vw,3.5rem);
  letter-spacing:.3em;font-weight:300;
  color:var(--acc);opacity:0;
  text-transform:uppercase;
}
#l-tag{
  font-size:.6rem;letter-spacing:.5em;text-transform:uppercase;
  color:var(--muted);opacity:0;margin-top:16px;
}
#l-bar{
  position:absolute;bottom:0;left:0;
  height:1px;width:0;background:var(--acc);
}

/* ── NAV ──────────────────────────────────────── */
#nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  padding:28px 5vw;
  display:flex;align-items:center;justify-content:space-between;
  transition:padding .5s,background .5s,backdrop-filter .5s;
}
#nav.stuck{
  padding:14px 5vw;
  background:rgba(8,8,8,.85);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
}
.nav-logo{
  font-family:var(--fd),serif;font-size:1.1rem;
  letter-spacing:.15em;color:var(--acc);text-decoration:none;
}
.nav-r{display:flex;gap:36px;list-style:none}
.nav-r a{
  font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--muted);text-decoration:none;transition:color .3s;
}
.nav-r a:hover{color:var(--acc)}
@media(max-width:768px){.nav-r{display:none}}

/* ── HERO ─────────────────────────────────────── */
#hero{
  position:relative;height:100svh;min-height:640px;
  display:flex;flex-direction:column;
  align-items:flex-start;justify-content:flex-end;
  padding:0 5vw 6vh;overflow:hidden;
}
#hero-3d{position:absolute;inset:0;z-index:0}
.hero-bg-grad{
  position:absolute;inset:0;z-index:1;
  background:radial-gradient(ellipse 80% 80% at 60% 40%, rgba(__PC__,.06) 0%, transparent 70%),
             linear-gradient(180deg, transparent 40%, rgba(__BG_RAW__,.9) 100%);
}
.hero-eyebrow{
  position:relative;z-index:3;
  font-size:.6rem;letter-spacing:.45em;text-transform:uppercase;
  color:var(--acc);margin-bottom:20px;
  opacity:0;transform:translateY(8px);
}
.hero-name{
  position:relative;z-index:3;
  font-family:var(--fd),serif;
  font-size:clamp(4rem,11vw,11rem);
  line-height:.85;font-weight:300;letter-spacing:-.03em;
  margin-bottom:28px;
}
.hn-word{display:block;overflow:hidden}
.hn-inner{display:block;transform:translateY(110%)}
.hero-desc{
  position:relative;z-index:3;
  font-size:clamp(.8rem,1.3vw,.95rem);
  color:var(--muted);letter-spacing:.06em;font-style:italic;
  max-width:420px;line-height:1.7;margin-bottom:40px;
  opacity:0;
}
.hero-actions{
  position:relative;z-index:3;
  display:flex;align-items:center;gap:24px;opacity:0;
}
.btn-primary{
  padding:14px 32px;border:1px solid var(--acc);
  color:var(--acc);font-size:.65rem;letter-spacing:.22em;text-transform:uppercase;
  text-decoration:none;position:relative;overflow:hidden;
  transition:color .45s;
}
.btn-primary::after{
  content:'';position:absolute;inset:0;background:var(--acc);
  transform:translateX(-101%);transition:transform .45s cubic-bezier(.77,0,.18,1);
}
.btn-primary:hover{color:var(--bg)}
.btn-primary:hover::after{transform:translateX(0)}
.btn-primary span{position:relative;z-index:1}
.btn-ghost{
  font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--muted);text-decoration:none;
  display:flex;align-items:center;gap:10px;transition:color .3s,gap .3s;
}
.btn-ghost:hover{color:var(--acc);gap:16px}
.bg-line{width:28px;height:1px;background:currentColor;transition:width .3s}
.btn-ghost:hover .bg-line{width:44px}
.hero-scroll{
  position:absolute;right:5vw;bottom:6vh;z-index:3;
  display:flex;flex-direction:column;align-items:center;gap:10px;
  font-size:.55rem;letter-spacing:.28em;text-transform:uppercase;
  color:var(--muted);opacity:0;writing-mode:vertical-rl;
}
.h-scroll-bar{
  width:1px;height:60px;position:relative;overflow:hidden;
  background:rgba(255,255,255,.08);
}
.h-scroll-fill{
  position:absolute;top:0;left:0;right:0;background:var(--acc);
  animation:scrollFill 1.8s ease-in-out infinite;
}
@keyframes scrollFill{
  0%{top:100%;bottom:0%} 50%{top:0%;bottom:0%} 100%{top:0%;bottom:100%}
}

/* ── MARQUEE ──────────────────────────────────── */
.marquee-wrap{
  border-top:1px solid var(--border);border-bottom:1px solid var(--border);
  overflow:hidden;padding:14px 0;background:var(--s1);
}
.marquee-track{
  display:flex;gap:0;white-space:nowrap;
  animation:marquee 22s linear infinite;
}
.marquee-track:hover{animation-play-state:paused}
.m-item{
  font-family:var(--fd),serif;font-size:1.1rem;font-style:italic;
  color:var(--muted);padding:0 40px;flex-shrink:0;
}
.m-sep{color:var(--acc);padding:0;font-style:normal}
@keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* ── SECTIONS ─────────────────────────────────── */
section{padding:120px 5vw;position:relative}
.stag{
  font-size:.58rem;letter-spacing:.38em;text-transform:uppercase;
  color:var(--acc);display:block;margin-bottom:18px;
}
.stitle{
  font-family:var(--fd),serif;
  font-size:clamp(2rem,4vw,3.6rem);
  font-weight:300;line-height:1.1;
}
.stitle em{font-style:italic;color:var(--acc)}
.rw{overflow:hidden;display:block}
.ri{display:inline-block;transform:translateY(108%)}

/* ── PHILOSOPHY ───────────────────────────────── */
#phil{
  background:var(--s1);
  display:flex;flex-direction:column;align-items:center;
  text-align:center;
}
.phil-quote{
  font-family:var(--fd),serif;
  font-size:clamp(1.8rem,4vw,4rem);
  font-weight:300;font-style:italic;line-height:1.35;
  max-width:900px;color:var(--txt);
}
.phil-quote em{color:var(--acc);font-style:italic}
.acc-line{width:1px;height:80px;background:var(--acc);margin:40px auto}

/* ── ABOUT ────────────────────────────────────── */
#about .g{
  display:grid;grid-template-columns:1fr 1fr;
  gap:0;margin-top:64px;
}
@media(max-width:900px){#about .g{grid-template-columns:1fr}}
.about-visual{
  position:relative;overflow:hidden;
  background:var(--s1);
  display:flex;align-items:center;justify-content:center;
  min-height:480px;
}
.about-visual canvas{position:absolute;inset:0}
.about-vis-text{
  position:relative;z-index:2;
  font-family:var(--fd),serif;
  font-size:clamp(5rem,12vw,14rem);
  font-weight:300;color:transparent;
  -webkit-text-stroke:1px rgba(__ACC_RAW__,.15);
  letter-spacing:-.04em;line-height:1;
  user-select:none;pointer-events:none;
}
.about-body{padding:64px 5vw;display:flex;flex-direction:column;justify-content:center}
.about-body p{
  color:var(--muted);line-height:1.95;font-size:.88rem;
  margin-bottom:16px;max-width:480px;
}
.about-stat{
  display:flex;gap:40px;margin-top:40px;
  padding-top:32px;border-top:1px solid var(--border);
}
.a-stat-n{
  font-family:var(--fd),serif;font-size:2.8rem;
  font-weight:300;color:var(--acc);line-height:1;display:block;
}
.a-stat-l{font-size:.58rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-top:4px;display:block}

/* ── OFFERINGS ─────────────────────────────────── */
#off{background:var(--s2);overflow:hidden}
.off-intro{max-width:600px;margin-bottom:64px}
.off-intro p{color:var(--muted);font-size:.9rem;line-height:1.8;margin-top:20px}
.off-cards{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:1px;background:var(--border);
}
@media(max-width:900px){.off-cards{grid-template-columns:1fr}}
.off-card{
  background:var(--s2);padding:48px 36px;
  position:relative;overflow:hidden;
  transition:background .5s;
  opacity:0;transform:translateY(32px);
}
.off-card::before{
  content:'';position:absolute;inset:0;z-index:0;
  background:linear-gradient(135deg,rgba(__PC__,.06) 0%,transparent 55%);
  opacity:0;transition:opacity .5s;
}
.off-card:hover{background:var(--s1)}
.off-card:hover::before{opacity:1}
.off-n{
  position:absolute;bottom:24px;right:28px;
  font-family:var(--fd),serif;font-size:5rem;
  font-weight:300;line-height:1;
  color:rgba(255,255,255,.025);user-select:none;
}
.off-icon-wrap{
  width:48px;height:48px;border:1px solid var(--border);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:1.3rem;margin-bottom:24px;position:relative;z-index:1;
  transition:border-color .3s,transform .3s;
}
.off-card:hover .off-icon-wrap{border-color:rgba(__PC__,.4);transform:scale(1.05)}
.off-title{
  font-family:var(--fd),serif;font-size:1.45rem;font-weight:400;
  margin-bottom:12px;position:relative;z-index:1;
  transition:color .3s;
}
.off-card:hover .off-title{color:var(--acc)}
.off-desc{font-size:.82rem;color:var(--muted);line-height:1.75;position:relative;z-index:1}

/* ── ATMOSPHERE ────────────────────────────────── */
#atmo{
  min-height:70vh;display:flex;align-items:center;
  overflow:hidden;position:relative;padding:100px 5vw;
}
.atmo-bg{
  position:absolute;inset:0;z-index:0;
  background:radial-gradient(ellipse 90% 60% at 30% 50%, rgba(__PC__,.05) 0%,transparent 70%);
}
.atmo-content{position:relative;z-index:1;max-width:700px}
.atmo-label{
  font-size:.58rem;letter-spacing:.42em;text-transform:uppercase;
  color:var(--acc);display:block;margin-bottom:24px;
}
.atmo-text{
  font-family:var(--fd),serif;
  font-size:clamp(2rem,4.5vw,4.5rem);
  font-weight:300;line-height:1.25;font-style:italic;
}
.atmo-text strong{font-style:normal;font-weight:300;color:var(--acc)}
.atmo-sig{
  margin-top:40px;display:flex;align-items:center;gap:16px;
  font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);
}
.atmo-line{width:40px;height:1px;background:var(--acc)}

/* ── INFO ──────────────────────────────────────── */
#info .g2{
  display:grid;grid-template-columns:1fr 1fr;
  gap:80px;margin-top:56px;
}
@media(max-width:900px){#info .g2{grid-template-columns:1fr}}
.info-block h3{
  font-family:var(--fd),serif;font-size:1.5rem;
  font-weight:300;margin-bottom:28px;
}
.hr-row{
  display:flex;justify-content:space-between;
  padding:12px 0;border-bottom:1px solid var(--border);
  font-size:.8rem;color:var(--muted);
  opacity:0;transform:translateX(-16px);
}
.ci-row{
  display:flex;align-items:flex-start;gap:14px;
  padding:16px 0;border-bottom:1px solid var(--border);
  opacity:0;transform:translateX(-16px);
}
.ci-icon{
  width:28px;height:28px;border:1px solid rgba(__PC__,.25);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.75rem;color:var(--acc);flex-shrink:0;
}
.ci-lbl{font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:3px}
.ci-val{font-size:.85rem;color:var(--txt)}
.ci-val a{color:inherit;text-decoration:none;transition:color .3s}
.ci-val a:hover{color:var(--acc)}

/* ── CTA ───────────────────────────────────────── */
#cta{
  text-align:center;padding:140px 5vw;
  background:var(--s1);position:relative;overflow:hidden;
}
.cta-glow{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:800px;height:800px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(__PC__,.07) 0%,transparent 65%);
  pointer-events:none;
}
.cta-pre{
  font-size:.62rem;letter-spacing:.42em;text-transform:uppercase;
  color:var(--acc);display:block;margin-bottom:24px;
}
.cta-title{
  font-family:var(--fd),serif;
  font-size:clamp(2.4rem,6vw,6rem);
  font-weight:300;line-height:.9;
  margin-bottom:52px;
}
.cta-title em{font-style:italic;color:var(--acc)}
.cta-btns{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}

/* ── FOOTER ────────────────────────────────────── */
footer{
  padding:48px 5vw;border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:16px;
}
.ft-logo{
  font-family:var(--fd),serif;font-size:1rem;
  color:var(--acc);letter-spacing:.12em;
}
.ft-copy{font-size:.6rem;color:var(--muted);letter-spacing:.08em}
</style>
</head>
<body>
<div id="c1"></div><div id="c2"></div>
<div id="noise"></div>

<!-- PRELOADER -->
<div id="loader">
  <div id="l-name">__NAME__</div>
  <div id="l-tag">__TAG__</div>
  <div id="l-bar"></div>
</div>

<!-- NAV -->
<nav id="nav">
  <a href="#" class="nav-logo">__INITIAL__.</a>
  <ul class="nav-r">
    <li><a href="#about">À propos</a></li>
    <li><a href="#off">Spécialités</a></li>
    <li><a href="#info">Contact</a></li>
  </ul>
</nav>

<!-- HERO -->
<section id="hero">
  <canvas id="hero-3d"></canvas>
  <div class="hero-bg-grad"></div>
  <p class="hero-eyebrow">__CITY__ &nbsp;·&nbsp; __TAG__</p>
  <h1 class="hero-name" id="hero-name">__HERO_NAME_HTML__</h1>
  <p class="hero-desc">__TAGLINE__</p>
  <div class="hero-actions">
    <a href="#about" class="btn-primary"><span>Découvrir</span></a>
    <a href="#info" class="btn-ghost"><span class="bg-line"></span><span>Nous trouver</span></a>
  </div>
  <div class="hero-scroll">
    <div class="h-scroll-bar"><div class="h-scroll-fill"></div></div>
    <span>Scroll</span>
  </div>
</section>

<!-- MARQUEE -->
<div class="marquee-wrap">
  <div class="marquee-track" id="mq-track">
    <span class="m-item">__NAME__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__CITY_TAG__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__CITY__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__RATING__ / 5</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__REVIEWS__ Avis</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__NAME__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__CITY_TAG__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__CITY__</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__RATING__ / 5</span>
    <span class="m-sep">✦</span>
    <span class="m-item">__REVIEWS__ Avis</span>
    <span class="m-sep">✦</span>
  </div>
</div>

<!-- PHILOSOPHY -->
<section id="phil">
  <div class="acc-line"></div>
  <p class="phil-quote" id="phil-q">«&nbsp;<em>__PHILOSOPHY__</em>&nbsp;»</p>
  <div class="acc-line"></div>
  <span class="stag" style="margin-bottom:0">— __NAME__, __CITY__</span>
</section>

<!-- ABOUT -->
<section id="about">
  <span class="stag">Notre histoire</span>
  <h2 class="stitle" style="margin-bottom:0">
    <span class="rw"><span class="ri">Un savoir-faire</span></span>
    <span class="rw"><span class="ri"><em>transmis avec passion</em></span></span>
  </h2>
  <div class="g">
    <div class="about-visual" id="about-vis">
      <canvas id="about-canvas"></canvas>
      <span class="about-vis-text">__INITIAL__</span>
    </div>
    <div class="about-body">
      <p>Chez <strong>__NAME__</strong>, chaque création reflète des années de passion, de recherche et d'exigence absolue. Nous sélectionnons les meilleurs ingrédients et respectons les techniques ancestrales tout en embrassant la modernité.</p>
      <p>Notre engagement envers l'excellence se traduit par la fidélité de notre clientèle et leur confiance renouvelée jour après jour.</p>
      <div class="about-stat">
        <div>
          <span class="a-stat-n" id="cnt-r">__RATING__</span>
          <span class="a-stat-l">Note Google</span>
        </div>
        <div>
          <span class="a-stat-n" id="cnt-v">0</span>
          <span class="a-stat-l">Avis clients</span>
        </div>
        <div>
          <span class="a-stat-n" style="font-size:1.4rem">__STARS__</span>
          <span class="a-stat-l">Excellence</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- OFFERINGS -->
<section id="off">
  <div class="off-intro">
    <span class="stag">Ce que nous offrons</span>
    <h2 class="stitle">
      <span class="rw"><span class="ri">Nos <em>créations</em></span></span>
    </h2>
    <p>Chaque produit est le fruit d'une attention méticuleuse, d'ingrédients soigneusement sélectionnés et d'un savoir-faire qui ne cède rien aux compromis.</p>
  </div>
  <div class="off-cards">
__OFF_CARDS__
  </div>
</section>

<!-- ATMOSPHERE -->
<section id="atmo">
  <div class="atmo-bg"></div>
  <div class="atmo-content">
    <span class="atmo-label">Notre engagement</span>
    <p class="atmo-text" id="atmo-txt">
      «&nbsp;<strong>__NAME__</strong> — une adresse qui incarne l'excellence de l'artisanat français à __CITY__.&nbsp;»
    </p>
    <div class="atmo-sig">
      <span class="atmo-line"></span>
      <span>__CITY__ · __TAG__</span>
    </div>
  </div>
</section>

<!-- INFO -->
<section id="info">
  <span class="stag">Nous trouver</span>
  <h2 class="stitle">
    <span class="rw"><span class="ri">Horaires &amp; <em>Contact</em></span></span>
  </h2>
  <div class="g2">
    <div class="info-block">
      <h3>Horaires d'ouverture</h3>
__HOURS__
    </div>
    <div class="info-block">
      <h3>Informations</h3>
__CONTACT__
    </div>
  </div>
</section>

<!-- CTA -->
<section id="cta">
  <div class="cta-glow"></div>
  <span class="cta-pre">Venez nous rendre visite</span>
  <h2 class="cta-title">
    <span class="rw"><span class="ri">Vivez l'expérience</span></span><br>
    <span class="rw"><span class="ri"><em>__NAME__</em></span></span>
  </h2>
  <div class="cta-btns">
__CTA_BTNS__
  </div>
</section>

<footer>
  <span class="ft-logo">__NAME__</span>
  <span class="ft-copy">__ADDRESS__</span>
  <span class="ft-copy">© __NAME__ · __CITY__</span>
</footer>

<script>
/* ── SMOOTH SCROLL ──────────────────────────── */
const lenis = new Lenis({ duration:1.4, easing:t=>Math.min(1,1.001-Math.pow(2,-10*t)) });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t*1000));
gsap.ticker.lagSmoothing(0);
gsap.registerPlugin(ScrollTrigger);

/* ── CURSOR ──────────────────────────────────── */
const c1=document.getElementById('c1'), c2=document.getElementById('c2');
let mx=0,my=0,rx=0,ry=0;
window.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});
document.querySelectorAll('a,button').forEach(el=>{
  el.addEventListener('mouseenter',()=>document.body.classList.add('is-hovering'));
  el.addEventListener('mouseleave',()=>document.body.classList.remove('is-hovering'));
});
(function loop(){
  rx+=(mx-rx)*.1; ry+=(my-ry)*.1;
  c1.style.left=mx+'px'; c1.style.top=my+'px';
  c2.style.left=rx+'px'; c2.style.top=ry+'px';
  requestAnimationFrame(loop);
})();

/* ── THREE.JS HERO ───────────────────────────── */
(function(){
  const canvas=document.getElementById('hero-3d');
  const r=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true});
  r.setPixelRatio(Math.min(window.devicePixelRatio,2));
  const W=()=>canvas.parentElement.offsetWidth;
  const H=()=>canvas.parentElement.offsetHeight;
  r.setSize(W(),H());
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(60,W()/H(),.1,100);
  cam.position.set(0,0,5);

  // Wireframe icosahedron — premium geometric feel
  const geo1=new THREE.IcosahedronGeometry(2.2,1);
  const mat1=new THREE.MeshBasicMaterial({
    color:new THREE.Color(__GEO_COLOR__),
    wireframe:true,transparent:true,opacity:.09
  });
  const mesh1=new THREE.Mesh(geo1,mat1); scene.add(mesh1);

  // Outer ring
  const geo2=new THREE.TorusGeometry(3.5,.005,2,80);
  const mat2=new THREE.MeshBasicMaterial({
    color:new THREE.Color(__GEO_COLOR__),transparent:true,opacity:.07
  });
  const mesh2=new THREE.Mesh(geo2,mat2);
  mesh2.rotation.x=Math.PI/4; scene.add(mesh2);

  // Particles
  const pGeo=new THREE.BufferGeometry();
  const N=400, pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){
    pos[i*3]=(Math.random()-.5)*12;
    pos[i*3+1]=(Math.random()-.5)*12;
    pos[i*3+2]=(Math.random()-.5)*6;
  }
  pGeo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const pMat=new THREE.PointsMaterial({
    color:new THREE.Color(__GEO_COLOR__),size:.025,transparent:true,opacity:.5
  });
  scene.add(new THREE.Points(pGeo,pMat));

  let mx2=0,my2=0;
  window.addEventListener('mousemove',e=>{mx2=(e.clientX/window.innerWidth-.5)*2;my2=-(e.clientY/window.innerHeight-.5)*2;});
  window.addEventListener('resize',()=>{r.setSize(W(),H());cam.aspect=W()/H();cam.updateProjectionMatrix();});

  const clock=new THREE.Clock();
  (function animate(){
    requestAnimationFrame(animate);
    const t=clock.getElapsedTime();
    mesh1.rotation.x=t*.06+my2*.15;
    mesh1.rotation.y=t*.09+mx2*.15;
    mesh2.rotation.z=t*.04;
    mesh2.rotation.y=mx2*.08;
    cam.position.x+=(mx2*.3-cam.position.x)*.03;
    cam.position.y+=(my2*.3-cam.position.y)*.03;
    r.render(scene,cam);
  })();
})();

/* ── ABOUT CANVAS (animated gradient mesh) ── */
(function(){
  const cv=document.getElementById('about-canvas');
  const ctx=cv.getContext('2d');
  const el=cv.parentElement;
  function resize(){cv.width=el.offsetWidth;cv.height=el.offsetHeight;}
  resize(); window.addEventListener('resize',resize);
  const orbs=[
    {x:.3,y:.4,r:.5,vx:.0008,vy:.0006},
    {x:.7,y:.6,r:.4,vx:-.0006,vy:.0008},
    {x:.5,y:.2,r:.3,vx:.0007,vy:-.0007},
  ];
  function draw(){
    const W=cv.width,H=cv.height;
    ctx.clearRect(0,0,W,H);
    orbs.forEach(o=>{
      o.x+=o.vx; o.y+=o.vy;
      if(o.x<0||o.x>1)o.vx*=-1;
      if(o.y<0||o.y>1)o.vy*=-1;
      const g=ctx.createRadialGradient(o.x*W,o.y*H,0,o.x*W,o.y*H,o.r*Math.max(W,H));
      g.addColorStop(0,'rgba(__PC__,.09)');
      g.addColorStop(1,'transparent');
      ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── PRELOADER ───────────────────────────────── */
const loader=document.getElementById('loader');
const lName=document.getElementById('l-name');
const lTag=document.getElementById('l-tag');
const lBar=document.getElementById('l-bar');
const tl=gsap.timeline({onComplete:()=>{
  gsap.to(loader,{opacity:0,duration:.6,onComplete:()=>{loader.remove();startPage();}});
}});
tl.to(lName,{opacity:1,y:0,duration:.7,ease:'power3.out'},0)
  .to(lTag,{opacity:1,duration:.5},'.4')
  .to(lBar,{width:'100%',duration:1,ease:'power2.inOut'},'.3')
  .to([lName,lTag],{opacity:0,y:-10,duration:.4,stagger:.1},'-=.1');

/* ── PAGE ANIMATIONS ─────────────────────────── */
function startPage(){
  // Nav stick
  ScrollTrigger.create({trigger:'body',start:'100px top',
    onEnter:()=>document.getElementById('nav').classList.add('stuck'),
    onLeaveBack:()=>document.getElementById('nav').classList.remove('stuck'),
  });

  // Hero name words
  document.querySelectorAll('.hn-inner').forEach((el,i)=>{
    gsap.to(el,{y:0,duration:.9,ease:'power3.out',delay:.1+i*.15});
  });
  gsap.to('.hero-eyebrow',{opacity:1,y:0,duration:.7,delay:.3});
  gsap.to('.hero-desc',{opacity:1,duration:.7,delay:.7});
  gsap.to('.hero-actions',{opacity:1,duration:.7,delay:.9});
  gsap.to('.hero-scroll',{opacity:1,duration:.7,delay:1.1});

  // Reveal lines on scroll
  document.querySelectorAll('.ri').forEach(el=>{
    gsap.to(el,{y:0,duration:.9,ease:'power3.out',
      scrollTrigger:{trigger:el,start:'top 94%'}});
  });

  // Philosophy quote words
  gsap.fromTo('#phil-q',{opacity:0,y:30},{opacity:1,y:0,duration:1,ease:'power2.out',
    scrollTrigger:{trigger:'#phil-q',start:'top 80%'}});

  // About visual clip
  gsap.fromTo('#about-vis',
    {clipPath:'inset(0 100% 0 0)'},
    {clipPath:'inset(0 0% 0 0)',duration:1.4,ease:'power4.inOut',
      scrollTrigger:{trigger:'#about-vis',start:'top 75%'}});

  // Counters
  ScrollTrigger.create({trigger:'#about',start:'top 70%',once:true,onEnter:()=>{
    gsap.fromTo({v:0},{v:__REVIEWS_NUM__},{duration:2,ease:'power2.out',
      onUpdate:function(){document.getElementById('cnt-v').textContent=Math.round(this.targets()[0].v);}});
  }});

  // Offering cards
  gsap.to('.off-card',{opacity:1,y:0,stagger:.12,duration:.8,ease:'power3.out',
    scrollTrigger:{trigger:'.off-cards',start:'top 82%'}});

  // Atmosphere text
  gsap.fromTo('#atmo-txt',{opacity:0,x:-30},{opacity:1,x:0,duration:1,ease:'power2.out',
    scrollTrigger:{trigger:'#atmo-txt',start:'top 80%'}});

  // Info rows
  gsap.to('.hr-row,.ci-row',{opacity:1,x:0,stagger:.06,duration:.6,ease:'power2.out',
    scrollTrigger:{trigger:'#info',start:'top 80%'}});

  // CTA glow parallax
  gsap.to('.cta-glow',{y:-80,ease:'none',
    scrollTrigger:{trigger:'#cta',scrub:1.5}});

  // Magnetic buttons
  document.querySelectorAll('.btn-primary,.btn-ghost').forEach(btn=>{
    btn.addEventListener('mousemove',e=>{
      const rc=btn.getBoundingClientRect();
      gsap.to(btn,{x:(e.clientX-rc.left-rc.width/2)*.18,
                   y:(e.clientY-rc.top-rc.height/2)*.18,
                   duration:.3,ease:'power2.out'});
    });
    btn.addEventListener('mouseleave',()=>
      gsap.to(btn,{x:0,y:0,duration:.7,ease:'elastic.out(1,.4)'}));
  });

  // Scroll-linked hero parallax
  gsap.to('#hero-name',{y:80,ease:'none',
    scrollTrigger:{trigger:'#hero',start:'top top',end:'bottom top',scrub:1}});
}
</script>
</body>
</html>
"""

# ── GENERATOR ────────────────────────────────────────────────────────────────
def generate_html(lead, github_url=""):
    name     = lead.get("name","")
    category = lead.get("category","")
    address  = lead.get("address","")
    phone    = lead.get("phone","")
    rating   = float(lead.get("rating") or 4.8)
    reviews  = int(lead.get("review_count") or 0)
    maps_url = lead.get("maps_url") or lead.get("google_maps_url","")
    hours    = lead.get("hours") or []
    city     = address.split(",")[-2].strip() if "," in address else "France"
    initial  = name[0].upper() if name else "A"

    t = get_theme(category)

    # Hero name — each word on its own line with reveal span
    words = name.split()
    hero_name_html = "".join(
        f'<span class="hn-word"><span class="hn-inner">{w}</span></span>'
        for w in words
    )

    # Offering cards
    off_html = ""
    for i, (title, desc) in enumerate(t["items"]):
        icons = ["✦","◈","✿"]
        off_html += (
            f'    <div class="off-card">\n'
            f'      <span class="off-n">0{i+1}</span>\n'
            f'      <div class="off-icon-wrap">{icons[i%3]}</div>\n'
            f'      <h3 class="off-title">{title}</h3>\n'
            f'      <p class="off-desc">{desc}</p>\n'
            f'    </div>\n'
        )

    # Hours
    if hours:
        hrs = "".join(f'    <div class="hr-row"><span>{h}</span></div>\n' for h in hours)
    else:
        hrs = ('    <div class="hr-row"><span>Lun – Ven</span><span>07h – 20h</span></div>\n'
               '    <div class="hr-row"><span>Samedi</span><span>07h – 21h</span></div>\n'
               '    <div class="hr-row"><span>Dimanche</span><span>08h – 19h</span></div>\n')

    # Contact
    con = (f'    <div class="ci-row"><div class="ci-icon">📍</div>'
           f'<div><span class="ci-lbl">Adresse</span>'
           f'<span class="ci-val">{address}</span></div></div>\n')
    if phone:
        con += (f'    <div class="ci-row"><div class="ci-icon">📞</div>'
                f'<div><span class="ci-lbl">Téléphone</span>'
                f'<span class="ci-val"><a href="tel:{phone}">{phone}</a></span></div></div>\n')
    if maps_url:
        con += (f'    <div class="ci-row"><div class="ci-icon">🗺</div>'
                f'<div><span class="ci-lbl">Itinéraire</span>'
                f'<span class="ci-val"><a href="{maps_url}" target="_blank" rel="noopener">'
                f'Voir sur Google Maps →</a></span></div></div>\n')

    # CTA buttons
    btns = ""
    if phone:
        btns += f'    <a href="tel:{phone}" class="btn-primary"><span>📞 Appeler</span></a>\n'
    if maps_url:
        btns += (f'    <a href="{maps_url}" target="_blank" rel="noopener" class="btn-primary">'
                 f'<span>📍 Itinéraire</span></a>\n')
    if not btns:
        btns = '    <a href="#info" class="btn-primary"><span>Nous contacter</span></a>\n'

    # Three.js color — "r,g,b" float format
    gc = t["geo_color"]  # e.g. "0.83,0.66,0.26"
    geo_color = f"new THREE.Color({gc})"

    # Raw hex bg for gradient (strip #)
    bg_raw = t["bg"].lstrip("#")
    # Convert hex to r,g,b integers
    bg_r = int(bg_raw[0:2],16)
    bg_g = int(bg_raw[2:4],16)
    bg_b = int(bg_raw[4:6],16)
    bg_raw_css = f"{bg_r},{bg_g},{bg_b}"

    # accent raw for CSS
    ac_raw = t["acc"].lstrip("#")
    acc_rgb = f"{int(ac_raw[0:2],16)},{int(ac_raw[2:4],16)},{int(ac_raw[4:6],16)}"

    html = HTML
    reps = {
        "__NAME__":         name,
        "__TAG__":          t["tag"],
        "__CITY_TAG__":     t["city_tag"],
        "__TAGLINE__":      t["tagline"],
        "__PHILOSOPHY__":   t["philosophy"],
        "__CITY__":         city,
        "__CITY12__":       city.replace(" ","")[:12],
        "__INITIAL__":      initial,
        "__ADDRESS__":      address,
        "__RATING__":       str(rating),
        "__REVIEWS__":      str(reviews),
        "__REVIEWS_NUM__":  str(reviews),
        "__STARS__":        stars_svg(rating),
        "__HERO_NAME_HTML__": hero_name_html,
        "__BG__":           t["bg"],
        "__BG_RAW__":       bg_raw_css,
        "__S1__":           t["s1"],
        "__S2__":           t["s2"],
        "__ACC__":          t["acc"],
        "__ACC2__":         t["acc2"],
        "__ACC3__":         t["acc3"],
        "__TXT__":          t["txt"],
        "__MUTED__":        t["muted"],
        "__BORDER__":       t["border"],
        "__PC__":           t["pc"],
        "__FD__":           t["fd"],
        "__FB__":           t["fb"],
        "__ACC_RAW__":      acc_rgb,
        "__GEO_COLOR__":    gc,
        "__OFF_CARDS__":    off_html,
        "__HOURS__":        hrs,
        "__CONTACT__":      con,
        "__CTA_BTNS__":     btns,
    }
    for k, v in reps.items():
        html = html.replace(k, str(v))
    return html

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("leads_file")
    p.add_argument("output_dir")
    p.add_argument("--github-username", default="")
    args = p.parse_args()

    leads = json.loads(pathlib.Path(args.leads_file).read_text(encoding="utf-8"))
    out = pathlib.Path(args.output_dir)

    for lead in leads:
        slug = lead.get("slug","")
        d = out / slug
        d.mkdir(parents=True, exist_ok=True)
        gh = (f"https://{args.github_username}.github.io/{slug}-site"
              if args.github_username else "")
        html = generate_html(lead, gh)
        (d / "index.html").write_text(html, encoding="utf-8")
        (d / ".nojekyll").touch()
        info = {k: lead.get(k) for k in
                ["name","category","address","phone","rating","review_count","slug"]}
        info["public_site"] = gh
        (d / "client_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Generated: {slug}")

if __name__ == "__main__":
    main()
