#!/usr/bin/env python3
"""
template_site.py — Canonical world-class French business website generator.
6 pages: index, menu, reservation, galerie, contact, admin
All Unsplash photo IDs are HTTP-200 verified. onerror fallback on every image.
WebGL1 domain-warping shader, GSAP 3.12 + ScrollTrigger, Lenis smooth scroll.
Quality validator runs after every generation.
"""
import sys, io, json, pathlib, argparse, re, hashlib
try:
    from photo_library import load_library, get_photos_for_site as _lib_photos
    _PHOTO_LIB = load_library()
except Exception:
    _PHOTO_LIB = {}
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── VERIFIED UNSPLASH PHOTO IDs (HTTP-200 confirmed) ──────────────────────────
# Universal fallback used in onerror — always exists
FALLBACK_PHOTO = "photo-1414235077428-338989a2e8c0"

PHOTOS = {
    "boulangerie": {
        "about":     "photo-1509440159596-0249088772ff",
        "menu_hero": "photo-1555507036-ab1f4038808a",
        "gallery": [
            "photo-1549931319-a545dcf3bc73",
            "photo-1555507036-ab1f4038808a",
            "photo-1517686469429-8bdb88b9f907",
            "photo-1509440159596-0249088772ff",
            "photo-1529543544282-ea669407fca3",
            "photo-1558961363-fa8fdf82db35",
            "photo-1567620905732-2d1ec7ab7445",
            "photo-1612392166886-ee8475b03af2",
        ],
    },
    "patisserie": {
        "about":     "photo-1551024601-bec78aea704b",
        "menu_hero": "photo-1488477181946-6428a0291777",
        "gallery": [
            "photo-1488477181946-6428a0291777",
            "photo-1551024601-bec78aea704b",
            "photo-1528975604071-b4dc52a2d18c",
            "photo-1562967914-608f82629710",
            "photo-1490645935967-10de6ba17061",
            "photo-1556742049-0cfed4f6a45d",
            "photo-1574071318508-1cdbab80d002",
            "photo-1543339308-43e59d6b73a6",
        ],
    },
    "restaurant": {
        "about":     "photo-1559339352-11d035aa65de",
        "menu_hero": "photo-1414235077428-338989a2e8c0",
        "gallery": [
            "photo-1414235077428-338989a2e8c0",
            "photo-1559339352-11d035aa65de",
            "photo-1504674900247-0877df9cc836",
            "photo-1551218372-a8789b81b253",
            "photo-1546069901-ba9599a7e63c",
            "photo-1565299585323-38d6b0865b47",
            "photo-1603133872878-684f208fb84b",
            "photo-1568901346375-23c9450c58cd",
        ],
    },
    "cafe": {
        "about":     "photo-1495474472287-4d71bcdd2085",
        "menu_hero": "photo-1501339847302-ac426a4a7cbb",
        "gallery": [
            "photo-1501339847302-ac426a4a7cbb",
            "photo-1495474472287-4d71bcdd2085",
            "photo-1528975604071-b4dc52a2d18c",
            "photo-1624374053855-39a5a1a41402",
            "photo-1608198093002-ad4e005484ec",
            "photo-1562967914-608f82629710",
            "photo-1565958011703-44f9829ba187",
            "photo-1543339308-43e59d6b73a6",
        ],
    },
    "default": {
        "about":     "photo-1559339352-11d035aa65de",
        "menu_hero": "photo-1414235077428-338989a2e8c0",
        "gallery": [
            "photo-1414235077428-338989a2e8c0",
            "photo-1504674900247-0877df9cc836",
            "photo-1546069901-ba9599a7e63c",
            "photo-1551218372-a8789b81b253",
            "photo-1528975604071-b4dc52a2d18c",
            "photo-1562967914-608f82629710",
            "photo-1556742049-0cfed4f6a45d",
            "photo-1543339308-43e59d6b73a6",
        ],
    },
}

# ── THEMES ─────────────────────────────────────────────────────────────────────
THEMES = {
    "boulangerie": {
        "bg":"#0A0905","s1":"#131008","s2":"#1C1810",
        "acc":"#D4A843","acc2":"#8B6A1F","acc3":"#F0D080",
        "txt":"#F2ECE0","muted":"#8A7A62","border":"rgba(212,168,67,.13)",
        "fd":"Cormorant Garamond",
        "tag":"Artisan Boulanger","city_tag":"Boulangerie de Quartier",
        "tagline":"L'art du pain depuis des générations",
        "philosophy":"Chaque levain est une promesse.\nChaque fournée, un hommage.",
        "pc":"212,168,67",
        "sh_c1":"0.55,0.32,0.04","sh_c2":"0.20,0.11,0.01","sh_c3":"0.72,0.50,0.10",
        "menu_cats":[
            ("Pains","🥖",[
                ("Pain au Levain","Fermentation 48h, croûte dorée, mie alvéolée — notre signature."),
                ("Pain de Campagne","Farine T80, mie rustique, notes de noisette."),
                ("Pain aux Céréales","Graines sélectionnées, profil riche et nourrissant."),
                ("Baguette Tradition","Recette classique, croustillante à souhait."),
            ]),
            ("Viennoiseries","🥐",[
                ("Croissant Pur Beurre","Beurre AOP, feuilletage 27 tours, doré à la perfection."),
                ("Pain au Chocolat","Chocolat Valrhona, croustillant, fondant à cœur."),
                ("Brioche Parisienne","Moelleuse, parfumée à la fleur d'oranger."),
                ("Chausson aux Pommes","Pommes confites, pâte feuilletée maison."),
            ]),
            ("Pâtisseries","🎂",[
                ("Tarte aux Fruits","Pâte sablée, crème pâtissière, fruits de saison."),
                ("Paris-Brest","Choux, crème pralinée, amandes torréfiées."),
                ("Éclair Café","Pâte à choux, crème café, glaçage brillant."),
                ("Mille-Feuille","Feuilletage caramélisé, vanille Bourbon Madagascar."),
            ]),
        ],
    },
    "patisserie": {
        "bg":"#09080C","s1":"#110F16","s2":"#181420",
        "acc":"#C87DC8","acc2":"#8B4A8B","acc3":"#E8B8E8",
        "txt":"#F5F0F8","muted":"#8A7888","border":"rgba(200,125,200,.13)",
        "fd":"Playfair Display",
        "tag":"Maître Pâtissier","city_tag":"Pâtisserie d'Excellence",
        "tagline":"Créations sucrées d'exception, élevées au rang d'art",
        "philosophy":"Le sucre est notre matière.\nLa beauté, notre obsession.",
        "pc":"200,125,200",
        "sh_c1":"0.45,0.18,0.45","sh_c2":"0.15,0.06,0.22","sh_c3":"0.62,0.28,0.62",
        "menu_cats":[
            ("Entremets","🎂",[
                ("Framboise Chocolat","Mousse intense, coulis framboise, feuille or."),
                ("Citron Yuzu","Tarte moderne, crème yuzu, meringue torchée."),
                ("Praliné Noisette","Dacquoise, ganache noisette Piémont."),
                ("Fraise Basilic","Fraîcheur estivale, saveurs contrastées."),
            ]),
            ("Chocolats","🍫",[
                ("Ganache Grand Cru","Cacao Pur Origen Venezuela 72%."),
                ("Caramel Fleur de Sel","Praliné, caramel onctueux, texture soyeuse."),
                ("Framboise Poivre","Acidité, épice, harmonie parfaite."),
                ("Gianduja Piémont","Noisette Piémont, chocolat lait Jivara."),
            ]),
            ("Petits Fours","🧁",[
                ("Macaron Maison","15 parfums exclusifs, recette secrète."),
                ("Financier Beurre Noisette","Amandes, beurre noisette, texture moelleuse."),
                ("Canelé Bordelais","Rhum, vanille, croûte caramélisée."),
                ("Madeleine Citron","Bosse parfaite, zeste confit."),
            ]),
        ],
    },
    "restaurant": {
        "bg":"#07080C","s1":"#0D0F15","s2":"#13151E",
        "acc":"#B89060","acc2":"#7A5A30","acc3":"#D4B080",
        "txt":"#EDE8DC","muted":"#8A7A65","border":"rgba(184,144,96,.13)",
        "fd":"Cormorant Garamond",
        "tag":"Restaurant Gastronomique","city_tag":"Table d'Exception",
        "tagline":"Une expérience culinaire qui transcende le repas",
        "philosophy":"Chaque assiette est un voyage.\nChaque service, une histoire.",
        "pc":"184,144,96",
        "sh_c1":"0.42,0.28,0.08","sh_c2":"0.14,0.09,0.02","sh_c3":"0.58,0.40,0.14",
        "menu_cats":[
            ("Entrées","🥗",[
                ("Foie Gras Poêlé","Chutney de figues, brioche toastée, gel vinaigre."),
                ("Carpaccio de Saint-Jacques","Agrumes, herbes fraîches, huile d'argan."),
                ("Velouté de Truffe","Émulsion au parmesan, truffe noire du Périgord."),
                ("Tartare de Thon Rouge","Avocat, ponzu, sésame noir grillé."),
            ]),
            ("Plats","🍽️",[
                ("Filet de Bœuf Rossini","Sauce périgueux, pomme soufflée, truffe."),
                ("Homard Bleu Breton","Bisque légère, fenouil caramélisé."),
                ("Agneau des Pyrénées","Jus corsé, légumes primeurs de saison."),
                ("Risotto Truffé","Arborio, parmesan 36 mois, truffe noire."),
            ]),
            ("Desserts","🍮",[
                ("Soufflé Grand Marnier","Chaud, servi à la minute, glace vanille."),
                ("Vacherin Glacé Maison","Meringue, sorbet framboise, coulis."),
                ("Tarte Tatin du Chef","Caramel beurre salé, crème fraîche."),
                ("Mignardises du Chef","Coffret surprise, petit café offert."),
            ]),
        ],
    },
    "cafe": {
        "bg":"#090807","s1":"#120F0C","s2":"#181410",
        "acc":"#A07848","acc2":"#6B4E28","acc3":"#C09860",
        "txt":"#EDE8E0","muted":"#8A7868","border":"rgba(160,120,72,.13)",
        "fd":"Cormorant Garamond",
        "tag":"Café de Spécialité","city_tag":"Café Artisanal",
        "tagline":"L'heure du café élevée au rang de rituel",
        "philosophy":"Un grain. Un terroir.\nUn instant suspendu.",
        "pc":"160,120,72",
        "sh_c1":"0.38,0.22,0.08","sh_c2":"0.14,0.08,0.02","sh_c3":"0.52,0.32,0.12",
        "menu_cats":[
            ("Cafés","☕",[
                ("Espresso Arabica","Grain Éthiopie, fruité, floral, persistant."),
                ("Flat White","Double ristretto, micro-mousse soyeuse."),
                ("Pour Over V60","Extraction lente, profil délicat, ultra-propre."),
                ("Cold Brew 24h","Infusion à froid, concentré doux et frais."),
            ]),
            ("Autres Boissons","🫖",[
                ("Matcha Latte Cérémonie","Grade A, lait d'avoine, sans sucre ajouté."),
                ("Thé Single Estate","Jardin Darjeeling, première récolte."),
                ("Limonade Maison","Citron Menton, gingembre, menthe fraîche."),
                ("Kombucha Maison","Fermentation naturelle, gingembre yuzu."),
            ]),
            ("À Manger","🧁",[
                ("Banana Bread","Noix de pécan, miel sauvage."),
                ("Scone Cranberries","Confiture maison, clotted cream."),
                ("Croissant Artisan","Livraison boulangerie chaque matin."),
                ("Cookie Valrhona","Chocolat 70%, fleur de sel, fondant."),
            ]),
        ],
    },
    "default": {
        "bg":"#08090C","s1":"#0F1015","s2":"#15161E",
        "acc":"#C9A84C","acc2":"#8B6914","acc3":"#E8C870",
        "txt":"#F0EAD6","muted":"#8A7E68","border":"rgba(201,168,76,.13)",
        "fd":"Cormorant Garamond",
        "tag":"Commerce d'Exception","city_tag":"Adresse Incontournable",
        "tagline":"Un savoir-faire unique, transmis avec passion",
        "philosophy":"L'excellence n'est pas un accident.\nC'est un choix quotidien.",
        "pc":"201,168,76",
        "sh_c1":"0.50,0.35,0.08","sh_c2":"0.18,0.12,0.02","sh_c3":"0.65,0.48,0.14",
        "menu_cats":[
            ("Notre Sélection","✦",[
                ("Spécialité Maison","Notre création signature, revisitée chaque saison."),
                ("Choix du Jour","Selon arrivage et inspiration du chef."),
                ("Menu Découverte","Pour les curieux et les gourmets exigeants."),
                ("Option Végétarienne","Frais, équilibré, savoureux."),
            ]),
            ("Exclusivités","◈",[
                ("Édition Limitée","En quantité très restreinte, sur place uniquement."),
                ("Sur Commande","Préparé spécialement pour vous sous 48h."),
                ("Coffret Cadeau","Emballage premium, idéal pour offrir."),
                ("Formule Groupe","Sur réservation, devis personnalisé gratuit."),
            ]),
        ],
    },
}


# -- THEME VARIANTS (4 per category, slug picks one deterministically) --------
THEME_VARIANTS = {
    "boulangerie": [
        {"bg":"#0A0905","s1":"#131008","s2":"#1C1810","acc":"#D4A843","acc2":"#8B6A1F","acc3":"#F0D080",
         "txt":"#F2ECE0","muted":"#8A7A62","border":"rgba(212,168,67,.13)","fd":"Cormorant Garamond",
         "pc":"212,168,67","sh_c1":"0.55,0.32,0.04","sh_c2":"0.20,0.11,0.01","sh_c3":"0.72,0.50,0.10",
         "tag":"Artisan Boulanger","city_tag":"Boulangerie de Quartier",
         "tagline":"L'art du pain depuis des générations",
         "philosophy":"Chaque levain est une promesse.\nChaque fournée, un hommage."},
        {"bg":"#0C0805","s1":"#16100A","s2":"#201610","acc":"#C8733A","acc2":"#8B4A1F","acc3":"#E8A070",
         "txt":"#F2EDE5","muted":"#8A7268","border":"rgba(200,115,58,.13)","fd":"Playfair Display",
         "pc":"200,115,58","sh_c1":"0.52,0.22,0.04","sh_c2":"0.22,0.08,0.01","sh_c3":"0.68,0.32,0.08",
         "tag":"Four Artisanal","city_tag":"Boulangerie Traditionnelle",
         "tagline":"Le pain comme autrefois, fait avec amour",
         "philosophy":"La farine, l'eau, le sel et le temps.\nC'est tout. C'est tout nous."},
        {"bg":"#060A07","s1":"#0C1210","s2":"#121A15","acc":"#6B9B5A","acc2":"#3D6B30","acc3":"#90C278",
         "txt":"#EBF2E8","muted":"#728070","border":"rgba(107,155,90,.13)","fd":"EB Garamond",
         "pc":"107,155,90","sh_c1":"0.18,0.38,0.10","sh_c2":"0.06,0.15,0.04","sh_c3":"0.28,0.52,0.16",
         "tag":"Pain Naturel","city_tag":"Boulangerie Bio & Artisanale",
         "tagline":"Des ingredients simples, un savoir-faire exceptionnel",
         "philosophy":"La nature donne. L'artisan transforme.\nNous, nous partageons."},
        {"bg":"#0A0908","s1":"#141210","s2":"#1C1A18","acc":"#B09070","acc2":"#7A6248","acc3":"#CEB898",
         "txt":"#F0EAE0","muted":"#8A7E72","border":"rgba(176,144,112,.13)","fd":"Libre Baskerville",
         "pc":"176,144,112","sh_c1":"0.45,0.35,0.22","sh_c2":"0.18,0.14,0.08","sh_c3":"0.60,0.48,0.32",
         "tag":"Maitre Boulanger","city_tag":"Boulangerie Gastronomique",
         "tagline":"Le luxe du fait-maison, accessible chaque matin",
         "philosophy":"Petrir, faconner, cuire.\nUn metier. Une vocation. Un art."},
    ],
    "patisserie": [
        {"bg":"#09080C","s1":"#110F16","s2":"#181420","acc":"#C87DC8","acc2":"#8B4A8B","acc3":"#E8B8E8",
         "txt":"#F5F0F8","muted":"#8A7888","border":"rgba(200,125,200,.13)","fd":"Playfair Display",
         "pc":"200,125,200","sh_c1":"0.45,0.18,0.45","sh_c2":"0.15,0.06,0.22","sh_c3":"0.62,0.28,0.62",
         "tag":"Maitre Patissier","city_tag":"Patisserie d'Excellence",
         "tagline":"Creations sucrees d'exception, elevees au rang d'art",
         "philosophy":"Le sucre est notre matiere.\nLa beaute, notre obsession."},
        {"bg":"#0C0809","s1":"#160F11","s2":"#1E1518","acc":"#D4829A","acc2":"#9B4A62","acc3":"#EEB8C8",
         "txt":"#F8F0F2","muted":"#8A7278","border":"rgba(212,130,154,.13)","fd":"Cormorant Garamond",
         "pc":"212,130,154","sh_c1":"0.52,0.18,0.30","sh_c2":"0.20,0.06,0.12","sh_c3":"0.68,0.28,0.44",
         "tag":"Creatrice de Douceurs","city_tag":"Patisserie Romantique",
         "tagline":"Des saveurs qui font battre le coeur",
         "philosophy":"Chaque gateau est une declaration.\nChaque bouchee, une emotion."},
        {"bg":"#0A0809","s1":"#130F12","s2":"#1A141A","acc":"#9B78C0","acc2":"#6A4A8B","acc3":"#C0A0E0",
         "txt":"#F2EEF8","muted":"#827A8A","border":"rgba(155,120,192,.13)","fd":"EB Garamond",
         "pc":"155,120,192","sh_c1":"0.32,0.18,0.52","sh_c2":"0.12,0.06,0.22","sh_c3":"0.48,0.28,0.70",
         "tag":"Artisan Chocolatier","city_tag":"Atelier de Patisserie",
         "tagline":"L'alchimie du sucre et de la passion",
         "philosophy":"Transformer le beurre en magie.\nC'est notre quotidien."},
        {"bg":"#0C0B09","s1":"#161410","s2":"#1E1C16","acc":"#C8A86A","acc2":"#8B7038","acc3":"#E8C890",
         "txt":"#F5F0E8","muted":"#8A8070","border":"rgba(200,168,106,.13)","fd":"Libre Baskerville",
         "pc":"200,168,106","sh_c1":"0.48,0.38,0.14","sh_c2":"0.18,0.14,0.04","sh_c3":"0.65,0.52,0.20",
         "tag":"Confiseur d'Exception","city_tag":"Patisserie Gastronomique",
         "tagline":"Le raffinement a la francaise, sublimé",
         "philosophy":"Le luxe nait du detail.\nNous aimons les details."},
    ],
    "restaurant": [
        {"bg":"#07080C","s1":"#0D0F15","s2":"#13151E","acc":"#B89060","acc2":"#7A5A30","acc3":"#D4B080",
         "txt":"#EDE8DC","muted":"#8A7A65","border":"rgba(184,144,96,.13)","fd":"Cormorant Garamond",
         "pc":"184,144,96","sh_c1":"0.42,0.28,0.08","sh_c2":"0.14,0.09,0.02","sh_c3":"0.58,0.40,0.14",
         "tag":"Restaurant Gastronomique","city_tag":"Table d'Exception",
         "tagline":"Une experience culinaire qui transcende le repas",
         "philosophy":"Chaque assiette est un voyage.\nChaque service, une histoire."},
        {"bg":"#0A0607","s1":"#140C0E","s2":"#1C1014","acc":"#A83850","acc2":"#6B1E30","acc3":"#CC5870",
         "txt":"#F2EAE8","muted":"#8A6872","border":"rgba(168,56,80,.13)","fd":"Playfair Display",
         "pc":"168,56,80","sh_c1":"0.42,0.08,0.14","sh_c2":"0.18,0.02,0.06","sh_c3":"0.58,0.14,0.22",
         "tag":"Bistrot Gastronomique","city_tag":"Cave & Cuisine",
         "tagline":"Le vin et la table, une histoire d'amour francaise",
         "philosophy":"Un bon plat sans bon vin\nest comme un jour sans soleil."},
        {"bg":"#060A07","s1":"#0C1410","s2":"#101C16","acc":"#3D8B5A","acc2":"#1E5A35","acc3":"#60B080",
         "txt":"#E8F2EC","muted":"#688078","border":"rgba(61,139,90,.13)","fd":"EB Garamond",
         "pc":"61,139,90","sh_c1":"0.10,0.35,0.18","sh_c2":"0.04,0.15,0.08","sh_c3":"0.16,0.52,0.28",
         "tag":"Restaurant de Terroir","city_tag":"Cuisine du Marche",
         "tagline":"Du producteur a l'assiette, avec amour et respect",
         "philosophy":"La terre nourrit.\nLe chef sublime. Vous savourez."},
        {"bg":"#060810","s1":"#0C1018","s2":"#101820","acc":"#4A7AB5","acc2":"#2A4A7A","acc3":"#70A0D8",
         "txt":"#E8EEFC","muted":"#6878A0","border":"rgba(74,122,181,.13)","fd":"Libre Baskerville",
         "pc":"74,122,181","sh_c1":"0.08,0.18,0.48","sh_c2":"0.02,0.06,0.22","sh_c3":"0.14,0.30,0.65",
         "tag":"Grande Table","city_tag":"Restaurant Etoile",
         "tagline":"L'excellence francaise dans toute sa splendeur",
         "philosophy":"La perfection est notre seuil minimum.\nL'excellence, notre signature."},
    ],
    "cafe": [
        {"bg":"#090807","s1":"#120F0C","s2":"#181410","acc":"#A07848","acc2":"#6B4E28","acc3":"#C09860",
         "txt":"#EDE8E0","muted":"#8A7868","border":"rgba(160,120,72,.13)","fd":"Cormorant Garamond",
         "pc":"160,120,72","sh_c1":"0.38,0.22,0.08","sh_c2":"0.14,0.08,0.02","sh_c3":"0.52,0.32,0.12",
         "tag":"Cafe de Specialite","city_tag":"Cafe Artisanal",
         "tagline":"L'heure du cafe elevee au rang de rituel",
         "philosophy":"Un grain. Un terroir.\nUn instant suspendu."},
        {"bg":"#0C0806","s1":"#180E0A","s2":"#201410","acc":"#C45C3A","acc2":"#8B3A1E","acc3":"#E08060",
         "txt":"#F2EAE5","muted":"#8A6860","border":"rgba(196,92,58,.13)","fd":"Playfair Display",
         "pc":"196,92,58","sh_c1":"0.50,0.18,0.08","sh_c2":"0.22,0.06,0.02","sh_c3":"0.65,0.28,0.12",
         "tag":"Cafe & Brunch","city_tag":"Bruncherie du Quartier",
         "tagline":"Le cafe qui reveille, le brunch qui inspire",
         "philosophy":"Le matin commence ici.\nLe reste suit naturellement."},
        {"bg":"#060B0B","s1":"#0C1616","s2":"#101E1E","acc":"#3D8888","acc2":"#1E5858","acc3":"#60AAAA",
         "txt":"#E8F2F2","muted":"#688080","border":"rgba(61,136,136,.13)","fd":"EB Garamond",
         "pc":"61,136,136","sh_c1":"0.08,0.35,0.35","sh_c2":"0.02,0.14,0.14","sh_c3":"0.12,0.50,0.50",
         "tag":"Cafe Concept","city_tag":"Espace Cafe & Culture",
         "tagline":"Un espace ou le cafe devient conversation",
         "philosophy":"Le cafe rassemble.\nLes idees s'epanouissent ici."},
        {"bg":"#060908","s1":"#0C1410","s2":"#101C16","acc":"#4A8A68","acc2":"#2A5A42","acc3":"#70AA88",
         "txt":"#E8F0EC","muted":"#688078","border":"rgba(74,138,104,.13)","fd":"Libre Baskerville",
         "pc":"74,138,104","sh_c1":"0.10,0.35,0.22","sh_c2":"0.04,0.15,0.08","sh_c3":"0.16,0.50,0.32",
         "tag":"Cafe Eco-Responsable","city_tag":"Cafe Durable & Local",
         "tagline":"Cafe de qualite, conscience en eveil",
         "philosophy":"Chaque tasse est un choix.\nNous choisissons l'essentiel."},
    ],
}

# ── HELPERS ────────────────────────────────────────────────────────────────────
def get_theme_key(cat):
    c = (cat or "").lower()
    c = c.replace("â","a").replace("é","e").replace("è","e").replace("ê","e").replace("î","i").replace("ô","o")
    for k in ["boulangerie","patisserie","restaurant","cafe"]:
        if k in c:
            return k
    return "default"

def get_theme(cat, slug=""):
    base = THEMES[get_theme_key(cat)].copy()
    key  = get_theme_key(cat)
    variants = THEME_VARIANTS.get(key)
    if variants and slug:
        idx = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(variants)
        base.update(variants[idx])
    return base

def get_photos(cat):
    return PHOTOS[get_theme_key(cat)]

def uimg(pid, w=1200, h=800, q=82):
    return f"https://images.unsplash.com/{pid}?w={w}&h={h}&q={q}&auto=format&fit=crop"

def img_tag(pid, w, h, alt, extra_attrs=""):
    # Accepts Unsplash photo IDs (photo-xxx) or full URLs (Higgsfield CDN)
    src = pid if pid.startswith("http") else uimg(pid, w, h)
    fb  = uimg(FALLBACK_PHOTO, w, h)
    err = f"this.onerror=null;this.src='{fb}'"
    return f'<img src="{src}" alt="{alt}" loading="lazy" onerror="{err}"{extra_attrs}>'

def hex_rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"

def stars(r):
    f=int(r); h=1 if r-f>=0.5 else 0
    return "★"*f + ("⯨" if h else "") + "☆"*(5-f-h)

# ── SHARED CSS (injected into every page) ─────────────────────────────────────
def shared_css(t, br):
    fd = t["fd"]; pc = t["pc"]; acc = t["acc"]
    return f"""
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{overflow-x:hidden;scroll-behavior:auto}}
:root{{--bg:{t["bg"]};--s1:{t["s1"]};--s2:{t["s2"]};--acc:{acc};--acc2:{t["acc2"]};--acc3:{t["acc3"]};--txt:{t["txt"]};--mu:{t["muted"]};--br:{t["border"]};--pc:{pc};--fd:'{fd}'}}
body{{background:var(--bg);color:var(--txt);font-family:'DM Sans',sans-serif;font-weight:300;overflow-x:hidden;cursor:none}}
::selection{{background:var(--acc);color:var(--bg)}}
::-webkit-scrollbar{{width:1px}}::-webkit-scrollbar-thumb{{background:var(--acc)}}
#c1,#c2{{position:fixed;border-radius:50%;pointer-events:none;z-index:9999;mix-blend-mode:difference;top:0;left:0;will-change:transform}}
#c1{{width:6px;height:6px;background:#fff;transform:translate(-50%,-50%)}}
#c2{{width:34px;height:34px;border:1px solid rgba(255,255,255,.3);transform:translate(-50%,-50%);transition:width .4s cubic-bezier(.16,1,.3,1),height .4s cubic-bezier(.16,1,.3,1)}}
body.hov #c2{{width:56px;height:56px}}
#noise{{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.034;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E");background-size:200px;animation:ns 8s steps(1) infinite}}
@keyframes ns{{0%{{background-position:0 0}}12%{{background-position:-40px 18px}}25%{{background-position:18px -30px}}37%{{background-position:-10px 40px}}50%{{background-position:30px 6px}}62%{{background-position:-20px -12px}}75%{{background-position:8px 22px}}87%{{background-position:-5px -18px}}}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;padding:28px 5vw;display:flex;align-items:center;justify-content:space-between;transition:padding .5s,background .5s,backdrop-filter .5s}}
nav.stuck{{padding:13px 5vw;background:rgba({br},.88);backdrop-filter:blur(28px);border-bottom:1px solid var(--br)}}
.nl{{font-family:var(--fd),serif;font-size:1.05rem;letter-spacing:.16em;color:var(--acc);text-decoration:none;transition:opacity .3s}}
.nl:hover{{opacity:.65}}
.nr{{display:flex;gap:28px;list-style:none;align-items:center}}
.nr a{{font-size:.57rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mu);text-decoration:none;transition:color .3s;position:relative}}
.nr a::after{{content:'';position:absolute;bottom:-3px;left:0;width:0;height:1px;background:var(--acc);transition:width .3s}}
.nr a:hover,.nr a.active{{color:var(--acc)}}
.nr a:hover::after,.nr a.active::after{{width:100%}}
.nbtn{{padding:9px 20px;border:1px solid var(--acc);color:var(--acc);font-size:.57rem;letter-spacing:.18em;text-transform:uppercase;text-decoration:none;transition:background .3s,color .3s;display:inline-block}}
.nbtn:hover{{background:var(--acc);color:var(--bg)}}
.nbtn::after{{display:none!important}}
@media(max-width:768px){{.nr li:not(:last-child){{display:none}}}}
section{{padding:96px 5vw;position:relative}}
.stag{{font-size:.55rem;letter-spacing:.42em;text-transform:uppercase;color:var(--acc);display:block;margin-bottom:18px}}
.stitle{{font-family:var(--fd),serif;font-size:clamp(1.8rem,3.8vw,3.4rem);font-weight:300;line-height:1.1}}
.stitle em{{font-style:italic;color:var(--acc)}}
.rw{{overflow:hidden;display:block}}.ri{{display:inline-block;transform:translateY(110%)}}
.acc-line{{width:1px;height:68px;background:var(--acc);margin:36px auto;opacity:.55}}
footer{{padding:46px 5vw;border-top:1px solid var(--br);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}}
.fl{{font-family:var(--fd),serif;font-size:.95rem;color:var(--acc);letter-spacing:.14em}}
.fc{{font-size:.57rem;color:var(--mu);letter-spacing:.08em}}
.btn-a{{display:inline-flex;align-items:center;gap:10px;padding:14px 30px;border:1px solid var(--acc);color:var(--acc);font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;text-decoration:none;position:relative;overflow:hidden;transition:color .4s}}
.btn-a::after{{content:'';position:absolute;inset:0;background:var(--acc);transform:translateX(-101%);transition:transform .44s cubic-bezier(.77,0,.18,1)}}
.btn-a:hover{{color:var(--bg)}}.btn-a:hover::after{{transform:translateX(0)}}
.btn-a span{{position:relative;z-index:1}}
.btn-b{{display:inline-flex;align-items:center;gap:10px;font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mu);text-decoration:none;transition:color .3s,gap .4s}}
.btn-b:hover{{color:var(--acc);gap:18px}}
.bbl{{width:28px;height:1px;background:currentColor;display:block;transition:width .4s}}
.btn-b:hover .bbl{{width:44px}}
"""

# ── SHARED JS ──────────────────────────────────────────────────────────────────
SHARED_JS = """
const lenis=new Lenis({duration:1.45,easing:t=>Math.min(1,1.001-Math.pow(2,-10*t)),smoothWheel:true});
lenis.on('scroll',ScrollTrigger.update);
gsap.ticker.add(t=>lenis.raf(t*1000));
gsap.ticker.lagSmoothing(0);
const c1=document.getElementById('c1'),c2=document.getElementById('c2');
let mx=window.innerWidth/2,my=window.innerHeight/2,rx=mx,ry=my;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});
document.querySelectorAll('a,button,input,select,textarea').forEach(el=>{
  el.addEventListener('mouseenter',()=>document.body.classList.add('hov'));
  el.addEventListener('mouseleave',()=>document.body.classList.remove('hov'));
});
(function loop(){rx+=(mx-rx)*.1;ry+=(my-ry)*.1;c1.style.left=mx+'px';c1.style.top=my+'px';c2.style.left=rx+'px';c2.style.top=ry+'px';requestAnimationFrame(loop);})();
ScrollTrigger.create({trigger:'body',start:'80px top',
  onEnter:()=>document.getElementById('nav').classList.add('stuck'),
  onLeaveBack:()=>document.getElementById('nav').classList.remove('stuck')});
document.querySelectorAll('.ri').forEach(el=>gsap.to(el,{y:0,duration:.95,ease:'power3.out',scrollTrigger:{trigger:el,start:'top 93%'}}));
document.querySelectorAll('.btn-a').forEach(btn=>{
  btn.addEventListener('mousemove',e=>{const r=btn.getBoundingClientRect();gsap.to(btn,{x:(e.clientX-r.left-r.width/2)*.18,y:(e.clientY-r.top-r.height/2)*.18,duration:.3,ease:'power2.out'})});
  btn.addEventListener('mouseleave',()=>gsap.to(btn,{x:0,y:0,duration:.7,ease:'elastic.out(1,.4)'}));
});
"""

# ── WEBGL DOMAIN-WARPING SHADER (WebGL1, max compatibility) ────────────────────
def shader_js(t):
    c1=t["sh_c1"]; c2=t["sh_c2"]; c3=t["sh_c3"]
    return f"""
(function(){{
  const cv=document.getElementById('sh');
  if(!cv)return;
  const gl=cv.getContext('webgl')||cv.getContext('experimental-webgl');
  if(!gl)return;
  function rsz(){{cv.width=cv.offsetWidth||innerWidth;cv.height=cv.offsetHeight||innerHeight;gl.viewport(0,0,cv.width,cv.height);}}
  rsz();window.addEventListener('resize',rsz);
  const VS='attribute vec2 p;void main(){{gl_Position=vec4(p,0.,1.);}}';
  const FS='precision highp float;uniform vec2 R;uniform float T;float h(vec2 p){{return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}}float n(vec2 p){{vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1)),u.x),u.y);}}float fbm(vec2 p){{float v=0.,a=.5;mat2 m=mat2(1.6,1.2,-1.2,1.6);for(int i=0;i<6;i++){{v+=a*n(p);p=m*p;a*=.5;}}return v;}}void main(){{vec2 uv=gl_FragCoord.xy/R;uv.x*=R.x/R.y;float t=T*.05;vec2 q=vec2(fbm(uv+t),fbm(uv+1.+t));vec2 r=vec2(fbm(uv+4.*q+vec2(1.7,9.2)+.15*t),fbm(uv+4.*q+vec2(8.3,2.8)+.126*t));float f=fbm(uv+4.*r);vec3 C1=vec3({c1}),C2=vec3({c2}),C3=vec3({c3});vec3 col=mix(mix(C2,C1,clamp(f*2.5,0.,1.)),C3,clamp(length(q),0.,1.));col*=f*1.6+.05;gl_FragColor=vec4(col,1.);}}';
  function mkS(type,src){{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){{console.warn(gl.getShaderInfoLog(s));return null;}}return s;}}
  const prog=gl.createProgram(),vs=mkS(gl.VERTEX_SHADER,VS),fs=mkS(gl.FRAGMENT_SHADER,FS);
  if(!vs||!fs)return;
  gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.linkProgram(prog);gl.useProgram(prog);
  const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  const pa=gl.getAttribLocation(prog,'p');gl.enableVertexAttribArray(pa);gl.vertexAttribPointer(pa,2,gl.FLOAT,false,0,0);
  const uR=gl.getUniformLocation(prog,'R'),uT=gl.getUniformLocation(prog,'T');
  const t0=performance.now();
  (function draw(){{gl.uniform2f(uR,cv.width,cv.height);gl.uniform1f(uT,(performance.now()-t0)/1000);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);requestAnimationFrame(draw);}})();
}})();"""

# ── NAV & FOOTER ───────────────────────────────────────────────────────────────
def nav_html(active, name, initial, t):
    items = [("index.html","Accueil"),("menu.html","Menu"),("galerie.html","Galerie"),
             ("reservation.html","Réserver"),("contact.html","Contact")]
    def nav_item(h, l):
        cls = ' class="active"' if h == active else ""
        return f'<li><a href="./{h}"{cls}>{l}</a></li>'
    lis = "\n    ".join(nav_item(h,l) for h,l in items)
    return f"""<nav id="nav">
  <a href="./index.html" class="nl">{initial}.</a>
  <ul class="nr">{lis}
    <li><a href="./reservation.html" class="nbtn">Réserver</a></li>
  </ul>
</nav>"""

def footer_html(name, address, city, phone, maps_url):
    ph = (f'<a href="tel:{phone}" style="color:var(--mu);text-decoration:none;'
          f'transition:color .3s" onmouseenter="this.style.color=\'var(--acc)\'"'
          f' onmouseleave="this.style.color=\'var(--mu)\'">{phone}</a>') if phone else ""
    mp = (f'<a href="{maps_url}" target="_blank" style="color:var(--acc);'
          f'text-decoration:none;font-size:.6rem;letter-spacing:.1em">Maps →</a>') if maps_url else ""
    sep = "&ensp;·&ensp;" if ph and mp else ""
    return f"""<footer>
  <span class="fl">{name}</span>
  <span class="fc">{address}</span>
  <span style="font-size:.62rem;color:var(--mu)">{ph}{sep}{mp}</span>
  <span class="fc">© {name} · {city}</span>
</footer>"""

# ── PRELOADER ──────────────────────────────────────────────────────────────────
PRELOADER_CSS = """
#ldr{position:fixed;inset:0;z-index:9998;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center}
#ldr-n{font-family:var(--fd),serif;font-size:clamp(1.1rem,3.5vw,2.6rem);letter-spacing:.32em;font-weight:300;color:var(--acc);opacity:0;transform:translateY(16px);text-transform:uppercase}
#ldr-t{font-size:.51rem;letter-spacing:.5em;text-transform:uppercase;color:var(--mu);opacity:0;margin-top:14px}
#ldr-b{position:absolute;bottom:0;left:0;height:1px;width:0;background:var(--acc)}
#ldr-c{position:absolute;bottom:22px;right:5vw;font-size:.58rem;letter-spacing:.18em;color:var(--mu);opacity:0}
"""
PRELOADER_JS = """
(function(){
  const ldr=document.getElementById('ldr');if(!ldr)return;
  const pct={v:0};
  gsap.to('#ldr-n',{opacity:1,y:0,duration:.65,ease:'power3.out',delay:.05});
  gsap.to('#ldr-t',{opacity:1,duration:.5,delay:.22});
  gsap.to('#ldr-c',{opacity:1,duration:.4,delay:.18});
  gsap.to(pct,{v:100,duration:1.0,ease:'power2.inOut',delay:.12,
    onUpdate:()=>{const c=document.getElementById('ldr-c');if(c)c.textContent=Math.round(pct.v)+'%';}});
  gsap.to('#ldr-b',{width:'100%',duration:1.05,ease:'power2.inOut',delay:.12,
    onComplete:()=>gsap.to(ldr,{opacity:0,duration:.5,delay:.06,
      onComplete:()=>{ldr.style.display='none';if(typeof pageInit==='function')pageInit();}})});
})();
"""
def preloader(name, tag):
    return f'<div id="ldr"><span id="ldr-n">{name}</span><span id="ldr-t">{tag}</span><div id="ldr-b"></div><span id="ldr-c">0%</span></div>'

# ── CDN LINKS ──────────────────────────────────────────────────────────────────
CDN = """<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/@studio-freight/lenis@1.0.42/dist/lenis.min.js"></script>"""
GFONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">"""

def head(title, t, extra_css=""):
    br = hex_rgb(t["bg"])
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{GFONTS}
{CDN}
<style>
:root{{--fd:'{t["fd"]}'}}
{shared_css(t,br)}
{extra_css}
</style>
</head>"""

def body_open():
    return '<body>\n<div id="c1"></div><div id="c2"></div>\n<div id="noise"></div>'

def page_foot(nav, footer, js):
    return f"""
{nav}
CONTENT_PLACEHOLDER
{footer}
<script>
gsap.registerPlugin(ScrollTrigger);
{SHARED_JS}
{js}
</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# INDEX
# ══════════════════════════════════════════════════════════════════════════════
def page_index(lead, t, ph, name, city, phone, rating, reviews, maps_url, nav, footer):
    br = hex_rgb(t["bg"]); pc = t["pc"]
    words = name.split()
    hw = "".join(f'<span class="hw"><span class="hwi">{w}</span></span>' for w in words)
    rev_int = max(int(reviews), 0)
    phil = t["philosophy"].replace("\n","<br>")
    _gi_style = ' style="width:100%;height:100%;object-fit:cover;transition:transform .8s ease,filter .6s;filter:brightness(.78) saturate(.85)"'
    gal_imgs = "".join(
        f'<div class="gi"><a href="./galerie.html">{img_tag(ph["gallery"][i],800,550,name,_gi_style)}</a></div>'
        for i in range(min(5, len(ph["gallery"])))
    )
    phone_btn = f'<a href="tel:{phone}" class="btn-a"><span>📞 Appeler</span></a>' if phone else ""
    maps_btn  = f'<a href="{maps_url}" target="_blank" class="btn-a"><span>📍 Itinéraire</span></a>' if maps_url else ""

    css = f"""
#hero{{position:relative;height:100svh;min-height:620px;display:flex;flex-direction:column;justify-content:flex-end;padding:0 5vw 8vh;overflow:hidden}}
canvas#sh{{position:absolute;inset:0;width:100%;height:100%;display:block}}
.hg{{position:absolute;inset:0;background:linear-gradient(155deg,rgba({br},.06) 0%,rgba({br},.93) 72%);pointer-events:none}}
.hey{{position:relative;z-index:2;font-size:.55rem;letter-spacing:.5em;text-transform:uppercase;color:var(--acc);opacity:0;margin-bottom:20px}}
.hn{{position:relative;z-index:2;font-family:var(--fd),serif;font-size:clamp(3.8rem,11vw,11rem);line-height:.84;font-weight:300;letter-spacing:-.025em;margin-bottom:28px}}
.hw{{display:block;overflow:hidden;line-height:1}}.hwi{{display:block;transform:translateY(115%)}}
.hd{{position:relative;z-index:2;max-width:400px;color:var(--mu);font-size:clamp(.76rem,1.2vw,.86rem);line-height:1.88;font-style:italic;margin-bottom:38px;opacity:0}}
.ha{{position:relative;z-index:2;display:flex;align-items:center;gap:22px;opacity:0}}
.hscr{{position:absolute;right:4vw;bottom:7vh;z-index:2;writing-mode:vertical-rl;font-size:.49rem;letter-spacing:.3em;text-transform:uppercase;color:var(--mu);opacity:0;display:flex;flex-direction:column;align-items:center;gap:12px}}
.hsl{{width:1px;height:48px;overflow:hidden;background:rgba(255,255,255,.07);position:relative}}
.hsl::after{{content:'';position:absolute;inset:0 0 auto 0;background:var(--acc);height:100%;animation:sa 1.9s ease-in-out infinite}}
@keyframes sa{{0%{{transform:translateY(-100%)}}50%{{transform:translateY(0)}}100%{{transform:translateY(100%)}}}}
.mq{{overflow:hidden;padding:13px 0;background:var(--s1);border-top:1px solid var(--br);border-bottom:1px solid var(--br)}}
.mqt{{display:flex;white-space:nowrap;animation:mqa 22s linear infinite;width:max-content}}
.mqt:hover{{animation-play-state:paused}}
.mqi{{font-family:var(--fd),serif;font-size:1rem;font-style:italic;color:var(--mu);padding:0 28px;flex-shrink:0}}
.mqs{{color:var(--acc);font-size:.8rem;flex-shrink:0;line-height:1.7}}
@keyframes mqa{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.ag{{display:grid;grid-template-columns:42% 58%;margin-top:52px}}
@media(max-width:900px){{.ag{{grid-template-columns:1fr}}}}
.ai{{position:relative;overflow:hidden;aspect-ratio:3/4}}
.ai img{{width:100%;height:100%;object-fit:cover;filter:brightness(.82) saturate(.88);transition:transform 8s ease}}
.ai:hover img{{transform:scale(1.03)}}
.ai-clip{{position:absolute;inset:0;background:var(--bg);transform-origin:top}}
.ab{{background:var(--s1);padding:54px 5vw;display:flex;flex-direction:column;justify-content:center}}
.ab p{{color:var(--mu);line-height:2;font-size:.84rem;margin-bottom:12px;max-width:480px}}
.ab strong{{color:var(--txt);font-weight:400}}
.sts{{display:flex;gap:32px;margin-top:36px;padding-top:28px;border-top:1px solid var(--br)}}
.sn{{font-family:var(--fd),serif;font-size:2.7rem;font-weight:300;color:var(--acc);display:block;line-height:1}}
.sl{{font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);margin-top:5px;display:block}}
#phil{{background:var(--s2);text-align:center;padding:120px 5vw}}
.pq{{font-family:var(--fd),serif;font-size:clamp(1.9rem,4.2vw,3.8rem);font-weight:300;line-height:1.32;color:var(--txt);max-width:820px;margin:0 auto;font-style:italic}}
.pq em{{color:var(--acc);font-style:normal}}
.gg{{display:grid;grid-template-columns:2fr 1fr 1fr;grid-template-rows:220px 220px;gap:3px;margin-top:46px}}
.gg .gi{{position:relative;overflow:hidden}}.gg .gi:first-child{{grid-row:1/3}}
.gg .gi img{{width:100%;height:100%;object-fit:cover;transition:transform .8s ease,filter .5s;filter:brightness(.78) saturate(.82)}}
.gg .gi:hover img{{transform:scale(1.07);filter:brightness(.55) saturate(.55)}}
.gg .gi a{{position:absolute;inset:0;z-index:1;display:flex;align-items:flex-end;padding:14px;text-decoration:none;opacity:0;transition:opacity .4s}}
.gg .gi:hover a{{opacity:1}}.gg .gi a span{{font-size:.57rem;letter-spacing:.2em;text-transform:uppercase;color:var(--acc)}}
@media(max-width:768px){{.gg{{grid-template-columns:1fr 1fr;grid-template-rows:160px 160px}}.gg .gi:first-child{{grid-row:1;grid-column:1/3}}}}
#ctas{{background:var(--s1);text-align:center;overflow:hidden;padding:128px 5vw;position:relative}}
.cta-aura{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:580px;height:580px;border-radius:50%;background:radial-gradient(ellipse,rgba({pc},.08) 0%,transparent 65%);pointer-events:none}}
.ctat{{font-family:var(--fd),serif;font-size:clamp(2.4rem,6vw,5.5rem);font-weight:300;line-height:.9;margin-bottom:44px}}
.ctat em{{font-style:italic;color:var(--acc)}}
"""
    marquee_items = [name, t["city_tag"], city, f"{rating}/5", f"{reviews} avis"] * 2
    mq_html = "".join(f'<span class="mqi">{x}</span><span class="mqs">✦</span>' for x in marquee_items)

    js = f"""
{shader_js(t)}
{PRELOADER_JS}
function pageInit(){{
  gsap.to('.hwi',{{y:0,duration:.95,ease:'power3.out',stagger:.11,delay:.04}});
  gsap.to('.hey',{{opacity:1,duration:.7,delay:.3}});
  gsap.to('.hd',{{opacity:1,duration:.75,delay:.55}});
  gsap.to('.ha',{{opacity:1,duration:.7,delay:.8}});
  gsap.to('.hscr',{{opacity:1,duration:.7,delay:1.05}});
  gsap.to('.hn',{{y:80,ease:'none',scrollTrigger:{{trigger:'#hero',start:'top top',end:'bottom top',scrub:1}}}});
  gsap.to('.ai-clip',{{scaleY:0,duration:1.4,ease:'power4.inOut',transformOrigin:'top',scrollTrigger:{{trigger:'.ai',start:'top 78%'}}}});
  ScrollTrigger.create({{trigger:'.sts',start:'top 76%',once:true,onEnter:()=>{{
    gsap.fromTo({{v:0}},{{v:{rev_int}}},{{duration:2,ease:'power2.out',onUpdate:function(){{const el=document.getElementById('sv');if(el)el.textContent=Math.round(this.targets()[0].v);}}}});
  }}}});
  gsap.fromTo('.gg .gi',{{opacity:0,scale:.96}},{{opacity:1,scale:1,stagger:.09,duration:.8,ease:'power2.out',scrollTrigger:{{trigger:'.gg',start:'top 82%'}}}});
  gsap.fromTo('.pq',{{opacity:0,y:24}},{{opacity:1,y:0,duration:1.2,ease:'power2.out',scrollTrigger:{{trigger:'#phil',start:'top 78%'}}}});
  gsap.to('.cta-aura',{{y:-80,ease:'none',scrollTrigger:{{trigger:'#ctas',scrub:2}}}});
}}
"""
    return f"""{head(f"{name} — {t['tag']} · {city}", t, css)}
{body_open()}
{preloader(name, t["tag"])}
{nav}
<section id="hero">
  <canvas id="sh"></canvas><div class="hg"></div>
  <p class="hey">{city} &ensp;·&ensp; {t["tag"]}</p>
  <h1 class="hn">{hw}</h1>
  <p class="hd">{t["tagline"]}</p>
  <div class="ha">
    <a href="./reservation.html" class="btn-a"><span>Réserver une table</span></a>
    <a href="#about" class="btn-b"><span class="bbl"></span><span>Découvrir</span></a>
  </div>
  <div class="hscr"><div class="hsl"></div><span>Scroll</span></div>
</section>
<div class="mq"><div class="mqt">{mq_html}</div></div>
<section id="about">
  <span class="stag">Notre histoire</span>
  <h2 class="stitle"><span class="rw"><span class="ri">Passion &amp;</span></span> <span class="rw"><span class="ri"><em>Excellence</em></span></span></h2>
  <div class="ag">
    <div class="ai">{img_tag(ph["about"],1000,1300,name,' style="width:100%;height:100%;object-fit:cover;filter:brightness(.82) saturate(.88);transition:transform 8s ease"')}<div class="ai-clip"></div></div>
    <div class="ab">
      <p>Chez <strong>{name}</strong>, chaque création est le fruit d'années de passion et d'une exigence absolue envers notre métier. Nous sélectionnons les meilleurs ingrédients, respectons les techniques ancestrales tout en embrassant la modernité.</p>
      <p>Notre engagement quotidien se traduit par la fidélité de nos clients et par une reconnaissance que nous renouvelons à chaque service.</p>
      <div class="sts">
        <div><span class="sn">{rating}</span><span class="sl">Note Google</span></div>
        <div><span class="sn" id="sv">0</span><span class="sl">Avis clients</span></div>
        <div><span class="sn" style="font-size:1.1rem;line-height:2;color:var(--acc)">{stars(float(rating))}</span><span class="sl">Satisfaction</span></div>
      </div>
      <div style="margin-top:30px;display:flex;gap:14px;flex-wrap:wrap">
        <a href="./menu.html" class="btn-a"><span>Voir la carte</span></a>
        <a href="./galerie.html" class="btn-b"><span class="bbl"></span><span>Galerie</span></a>
      </div>
    </div>
  </div>
</section>
<section id="phil">
  <div class="acc-line" style="margin-top:0"></div>
  <p class="pq">«&nbsp;<em>{phil}</em>&nbsp;»</p>
  <div class="acc-line"></div>
  <span class="stag" style="text-align:center;display:block;margin-bottom:0">— {name}, {city}</span>
</section>
<section id="gtease">
  <span class="stag">Galerie photo</span>
  <h2 class="stitle"><span class="rw"><span class="ri">Nos <em>instants</em></span></span></h2>
  <div class="gg">{gal_imgs}</div>
</section>
<section id="ctas">
  <div class="cta-aura"></div>
  <span class="stag">Venez nous rendre visite</span>
  <h2 class="ctat"><span class="rw"><span class="ri">Vivez l'expérience</span></span><br><span class="rw"><span class="ri"><em>{name}</em></span></span></h2>
  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
    {phone_btn}<a href="./reservation.html" class="btn-a"><span>📅 Réserver</span></a>{maps_btn}
  </div>
</section>
{footer}
<script>gsap.registerPlugin(ScrollTrigger);{SHARED_JS}{js}</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# MENU
# ══════════════════════════════════════════════════════════════════════════════
def page_menu(lead, t, ph, name, city, nav, footer):
    br = hex_rgb(t["bg"])
    cats = "".join(f"""<div class="mcat">
  <div class="mcat-hd"><span class="mcat-icon">{icon}</span><h3><span class="rw"><span class="ri">{cn}</span></span></h3><div class="mcat-rule"></div></div>
  <div class="mcat-grid">{"".join(f'<article class="mi"><h4 class="mi-name">{n}</h4><p class="mi-desc">{d}</p></article>' for n,d in items)}</div>
</div>""" for cn,icon,items in t["menu_cats"])
    css = f"""
.ph{{position:relative;height:54vh;min-height:360px;overflow:hidden}}
.ph img{{width:100%;height:100%;object-fit:cover;filter:brightness(.5) saturate(.7);transform:scale(1.04)}}
.ph-ov{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-end;padding:0 5vw 7vh;background:linear-gradient(180deg,transparent 20%,rgba({br},.82) 100%)}}
.ph-ov h1{{font-family:var(--fd),serif;font-size:clamp(3rem,8vw,7rem);font-weight:300;letter-spacing:-.02em}}
.ph-ov h1 em{{font-style:italic;color:var(--acc)}}
.ph-ov p{{font-size:.55rem;letter-spacing:.42em;text-transform:uppercase;color:var(--acc);margin-bottom:14px}}
.mcat{{padding:62px 0;border-bottom:1px solid var(--br)}}.mcat:last-child{{border-bottom:none;padding-bottom:0}}
.mcat-hd{{display:flex;align-items:center;gap:18px;margin-bottom:42px}}
.mcat-icon{{font-size:1.55rem}}.mcat-hd h3{{font-family:var(--fd),serif;font-size:clamp(1.7rem,3vw,2.6rem);font-weight:300}}
.mcat-rule{{flex:1;height:1px;background:var(--br)}}
.mcat-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--br)}}
@media(max-width:700px){{.mcat-grid{{grid-template-columns:1fr}}}}
.mi{{background:var(--bg);padding:26px 24px;transition:background .4s;position:relative;overflow:hidden}}
.mi::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--acc);transform:scaleY(0);transform-origin:bottom;transition:transform .4s}}
.mi:hover{{background:var(--s1)}}.mi:hover::before{{transform:scaleY(1)}}
.mi-name{{font-family:var(--fd),serif;font-size:1.1rem;font-weight:400;margin-bottom:7px}}
.mi-desc{{font-size:.77rem;color:var(--mu);line-height:1.72}}
"""
    js = """
gsap.to('.ph img',{scale:1,duration:1.8,ease:'power2.out'});
gsap.fromTo('.mcat',{opacity:0,y:28},{opacity:1,y:0,stagger:.14,duration:.85,ease:'power2.out',
  scrollTrigger:{trigger:'#mc',start:'top 80%'}});
gsap.fromTo('.mi',{opacity:0,y:14},{opacity:1,y:0,stagger:.05,duration:.6,ease:'power2.out',
  scrollTrigger:{trigger:'.mcat-grid',start:'top 85%'}});
"""
    return f"""{head(f"{name} — Menu &amp; Carte", t, css)}
{body_open()}
{nav}
<div class="ph">
  {img_tag(ph["menu_hero"],1800,750,name,' style="width:100%;height:100%;object-fit:cover;filter:brightness(.5) saturate(.7);transform:scale(1.04)"')}
  <div class="ph-ov"><p>Menu · {city}</p><h1><span class="rw"><span class="ri">Notre <em>Carte</em></span></span></h1></div>
</div>
<section id="mc">{cats}</section>
<section style="background:var(--s1);text-align:center">
  <span class="stag">Prêt à passer à table ?</span>
  <h2 class="stitle" style="margin-bottom:32px"><span class="rw"><span class="ri"><em>Réservez</em> votre moment</span></span></h2>
  <a href="./reservation.html" class="btn-a"><span>Réserver maintenant</span></a>
</section>
{footer}
<script>gsap.registerPlugin(ScrollTrigger);{SHARED_JS}{js}</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# RESERVATION
# ══════════════════════════════════════════════════════════════════════════════
def page_reservation(lead, t, name, city, phone, maps_url, nav, footer):
    br = hex_rgb(t["bg"]); pc = t["pc"]
    address = lead.get("address","")
    ph_row  = f'<div class="ir"><div class="ii">📞</div><div><span class="il">Téléphone</span><span class="iv"><a href="tel:{phone}">{phone}</a></span></div></div>' if phone else ""
    mp_row  = f'<div class="ir"><div class="ii">🗺</div><div><span class="il">Itinéraire</span><span class="iv"><a href="{maps_url}" target="_blank">Voir sur Maps →</a></span></div></div>' if maps_url else ""
    css = f"""
#rh{{padding:140px 5vw 58px;background:var(--s1);border-bottom:1px solid var(--br)}}
#rh h1{{font-family:var(--fd),serif;font-size:clamp(2.8rem,7vw,6.5rem);font-weight:300;margin-top:14px;line-height:.9}}
#rh h1 em{{font-style:italic;color:var(--acc)}}
#rm{{display:grid;grid-template-columns:1fr 1.2fr}}
@media(max-width:900px){{#rm{{grid-template-columns:1fr}}}}
#ri{{padding:58px 5vw;background:var(--bg);border-right:1px solid var(--br)}}
#ri h3{{font-family:var(--fd),serif;font-size:1.5rem;font-weight:300;margin-bottom:28px}}
.ir{{display:flex;align-items:flex-start;gap:13px;padding:14px 0;border-bottom:1px solid var(--br);opacity:0;transform:translateX(-12px)}}
.ii{{width:30px;height:30px;border:1px solid rgba({pc},.3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;color:var(--acc);flex-shrink:0;margin-top:1px}}
.il{{font-size:.51rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);display:block;margin-bottom:3px}}
.iv{{font-size:.84rem}}.iv a{{color:inherit;text-decoration:none;transition:color .3s}}.iv a:hover{{color:var(--acc)}}
.inote{{margin-top:26px;padding:18px;border:1px solid var(--br);background:rgba({pc},.04);font-size:.77rem;color:var(--mu);line-height:1.78}}
#rf{{padding:58px 5vw;background:var(--s1)}}
#rf h3{{font-family:var(--fd),serif;font-size:1.5rem;font-weight:300;margin-bottom:30px}}
.fg{{margin-bottom:22px}}
.fl2{{font-size:.53rem;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);display:block;margin-bottom:8px;transition:color .3s}}
.fg:focus-within .fl2{{color:var(--acc)}}
.fi{{width:100%;background:var(--bg);border:1px solid var(--br);color:var(--txt);padding:13px 15px;font-size:.84rem;font-family:'DM Sans',sans-serif;outline:none;transition:border-color .3s;appearance:none}}
.fi:focus{{border-color:var(--acc)}}
.fi::placeholder{{color:var(--mu)}}
textarea.fi{{resize:vertical;min-height:80px}}
.fr2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:580px){{.fr2{{grid-template-columns:1fr}}}}
.slots{{display:flex;flex-wrap:wrap;gap:7px;margin-top:5px}}
.slot{{padding:8px 14px;border:1px solid var(--br);font-size:.67rem;letter-spacing:.1em;color:var(--mu);background:transparent;cursor:none;transition:all .3s;font-family:'DM Sans',sans-serif}}
.slot:hover{{border-color:rgba({pc},.4);color:var(--txt)}}.slot.sel{{background:var(--acc);border-color:var(--acc);color:var(--bg);font-weight:500}}
.gctl{{display:flex;align-items:stretch;width:fit-content}}
.gb{{width:40px;border:1px solid var(--br);background:transparent;color:var(--txt);font-size:1.1rem;cursor:none;transition:all .3s;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif}}
.gb:hover{{border-color:var(--acc);color:var(--acc)}}
#gc{{width:60px;text-align:center;background:var(--bg);border-top:1px solid var(--br);border-bottom:1px solid var(--br);border-left:none;border-right:none;height:40px;color:var(--txt);font-size:.92rem;font-family:'DM Sans',sans-serif;outline:none}}
.fsub{{width:100%;padding:15px;background:transparent;border:1px solid var(--acc);color:var(--acc);font-size:.63rem;letter-spacing:.22em;text-transform:uppercase;cursor:none;position:relative;overflow:hidden;transition:color .4s;margin-top:8px;font-family:'DM Sans',sans-serif}}
.fsub::after{{content:'';position:absolute;inset:0;background:var(--acc);transform:translateX(-101%);transition:transform .44s cubic-bezier(.77,0,.18,1)}}
.fsub:hover{{color:var(--bg)}}.fsub:hover::after{{transform:translateX(0)}}
.fsub span{{position:relative;z-index:1}}
#rsucc{{display:none;flex-direction:column;align-items:center;justify-content:center;padding:72px 32px;text-align:center}}
.sm{{font-family:var(--fd),serif;font-size:3.8rem;color:var(--acc);margin-bottom:22px;line-height:1}}
#rsucc h3{{font-family:var(--fd),serif;font-size:2rem;font-weight:300;color:var(--acc);margin-bottom:14px}}
#rsucc p{{color:var(--mu);line-height:1.92;max-width:420px;font-size:.86rem}}
"""
    slug_safe = re.sub(r'[^a-z0-9]', '_', name.lower())
    js = f"""
document.getElementById('fdate').min=new Date().toISOString().split('T')[0];
const gc=document.getElementById('gc');
document.getElementById('gm').addEventListener('click',()=>{{if(+gc.value>1){{gc.value=+gc.value-1;gsap.fromTo(gc,{{y:-4,opacity:.6}},{{y:0,opacity:1,duration:.2}})}}}});
document.getElementById('gp').addEventListener('click',()=>{{if(+gc.value<20){{gc.value=+gc.value+1;gsap.fromTo(gc,{{y:4,opacity:.6}},{{y:0,opacity:1,duration:.2}})}}}});
document.querySelectorAll('.slot').forEach(btn=>{{
  btn.addEventListener('click',()=>{{
    document.querySelectorAll('.slot').forEach(s=>s.classList.remove('sel'));
    btn.classList.add('sel');document.getElementById('ft').value=btn.dataset.t;
    gsap.fromTo(btn,{{scale:.9}},{{scale:1,duration:.25,ease:'back.out(2)'}});
  }});
}});
document.getElementById('rform').addEventListener('submit',e=>{{
  e.preventDefault();
  const d=new FormData(e.target);
  const obj={{fn:d.get('fn'),ln:d.get('ln'),email:d.get('email'),tel:d.get('tel'),
             date:d.get('date'),guests:d.get('guests'),time:d.get('time'),msg:d.get('msg'),
             business:'{name}',city:'{city}',ts:new Date().toISOString()}};
  if(!obj.fn||!obj.ln||!obj.email||!obj.date||!obj.time){{
    gsap.fromTo('#rform',{{x:-8}},{{x:0,duration:.45,ease:'elastic.out(1,.3)'}});return;
  }}
  const all=JSON.parse(localStorage.getItem('res_{slug_safe}')||'[]');
  all.push(obj);localStorage.setItem('res_{slug_safe}',JSON.stringify(all));
  gsap.to('#rform',{{opacity:0,y:-22,duration:.38,ease:'power2.in',onComplete:()=>{{
    document.getElementById('rform').style.display='none';
    const s=document.getElementById('rsucc');s.style.display='flex';
    const ds=obj.date?new Date(obj.date+'T12:00:00').toLocaleDateString('fr-FR',{{weekday:'long',day:'numeric',month:'long'}}):'';
    document.getElementById('smsg').textContent='Merci '+obj.fn+', demande pour '+ds+(obj.time?' à '+obj.time:'')+' ('+obj.guests+' pers.) enregistrée. Confirmation sous 24h.';
    gsap.fromTo(s,{{opacity:0,y:18}},{{opacity:1,y:0,duration:.65,ease:'power2.out'}});
  }}}});
}});
gsap.to('.ir',{{opacity:1,x:0,stagger:.09,duration:.62,ease:'power2.out',delay:.2}});
gsap.fromTo('#rf',{{opacity:0,x:18}},{{opacity:1,x:0,duration:.72,ease:'power2.out',delay:.12}});
"""
    return f"""{head(f"{name} — Réservation en ligne", t, css)}
{body_open()}
{nav}
<div id="rh"><span class="stag">Réservation en ligne</span>
  <h1><span class="rw"><span class="ri">Réservez votre</span></span><br><span class="rw"><span class="ri"><em>table</em></span></span></h1>
</div>
<div id="rm">
  <div id="ri">
    <h3>Nous trouver</h3>
    <div class="ir"><div class="ii">📍</div><div><span class="il">Adresse</span><span class="iv">{address}</span></div></div>
    {ph_row}{mp_row}
    <div class="ir"><div class="ii">⏰</div><div><span class="il">Horaires</span><span class="iv">Mar–Sam 07h–20h · Dim 08h–18h</span></div></div>
    <div class="inote">Votre demande sera confirmée dans les 24h. Pour une réservation urgente, appelez-nous directement.</div>
  </div>
  <div id="rf">
    <h3>Votre demande</h3>
    <form id="rform" novalidate>
      <div class="fr2">
        <div class="fg"><label class="fl2">Prénom *</label><input class="fi" type="text" name="fn" placeholder="Jean" required autocomplete="given-name"></div>
        <div class="fg"><label class="fl2">Nom *</label><input class="fi" type="text" name="ln" placeholder="Dupont" required autocomplete="family-name"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl2">Email *</label><input class="fi" type="email" name="email" placeholder="jean@email.com" required autocomplete="email"></div>
        <div class="fg"><label class="fl2">Téléphone</label><input class="fi" type="tel" name="tel" placeholder="+33 6 12 34 56 78" autocomplete="tel"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl2">Date *</label><input class="fi" id="fdate" type="date" name="date" required></div>
        <div class="fg"><label class="fl2">Personnes</label>
          <div class="gctl"><button type="button" class="gb" id="gm">−</button><input id="gc" type="number" name="guests" value="2" min="1" max="20" readonly><button type="button" class="gb" id="gp">+</button></div>
        </div>
      </div>
      <div class="fg"><label class="fl2">Créneau *</label>
        <div class="slots">
          <button type="button" class="slot" data-t="12:00">12h00</button>
          <button type="button" class="slot" data-t="12:30">12h30</button>
          <button type="button" class="slot" data-t="13:00">13h00</button>
          <button type="button" class="slot" data-t="13:30">13h30</button>
          <button type="button" class="slot" data-t="19:00">19h00</button>
          <button type="button" class="slot" data-t="19:30">19h30</button>
          <button type="button" class="slot" data-t="20:00">20h00</button>
          <button type="button" class="slot" data-t="20:30">20h30</button>
        </div>
        <input type="hidden" name="time" id="ft">
      </div>
      <div class="fg"><label class="fl2">Message</label><textarea class="fi" name="msg" placeholder="Allergies, occasion spéciale…"></textarea></div>
      <button type="submit" class="fsub"><span>Envoyer la demande ›</span></button>
    </form>
    <div id="rsucc"><div class="sm">✦</div><h3>Merci !</h3><p id="smsg"></p>
      <div style="margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;justify-content:center">
        <a href="./menu.html" class="btn-a"><span>Voir la carte</span></a>
        <a href="./index.html" class="btn-b"><span class="bbl"></span><span>Accueil</span></a>
      </div>
    </div>
  </div>
</div>
{footer}
<script>gsap.registerPlugin(ScrollTrigger);{SHARED_JS}{js}</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# GALERIE
# ══════════════════════════════════════════════════════════════════════════════
def page_galerie(lead, t, ph, name, city, nav, footer):
    br  = hex_rgb(t["bg"]); pc = t["pc"]
    heights = ["320px","480px","265px","375px","295px","440px","285px","360px"]
    items = ""
    lb_photos = []
    for i, pid in enumerate(ph["gallery"]):
        h   = heights[i % len(heights)]
        lb  = uimg(pid, 1500, 1000, 85)
        lb_photos.append(lb)
        src_attr = f' style="width:100%;height:100%;object-fit:cover;display:block;transition:transform .8s ease,filter .6s;filter:brightness(.8) saturate(.85)"'
        items += f'<div class="gi" data-i="{i}" style="height:{h}">{img_tag(pid,900,700,f"{name} photo {i+1}",src_attr)}<div class="gh"><span>⊕</span></div></div>\n'
    lb_json = json.dumps(lb_photos)
    css = f"""
#gh{{padding:140px 5vw 58px;background:var(--s1);border-bottom:1px solid var(--br)}}
#gh h1{{font-family:var(--fd),serif;font-size:clamp(2.8rem,7vw,6.5rem);font-weight:300;margin-top:14px;line-height:.9}}
#gh h1 em{{font-style:italic;color:var(--acc)}}
#gg{{padding:48px 3vw 64px;columns:3 260px;column-gap:4px}}
.gi{{break-inside:avoid;margin-bottom:4px;position:relative;overflow:hidden;cursor:none;opacity:0;transform:translateY(18px)}}
.gi img{{display:block}}
.gi:hover img{{transform:scale(1.06);filter:brightness(.55) saturate(.55)!important}}
.gh{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .4s;background:rgba({br},.2)}}
.gh span{{font-size:2.2rem;color:var(--acc);transform:scale(.7);transition:transform .4s;line-height:1}}
.gi:hover .gh{{opacity:1}}.gi:hover .gh span{{transform:scale(1)}}
#lb{{position:fixed;inset:0;z-index:9500;background:rgba({br},.97);display:none;align-items:center;justify-content:center;backdrop-filter:blur(14px)}}
#lb.open{{display:flex}}
#lb img{{max-width:90vw;max-height:85vh;object-fit:contain;display:block;border:1px solid var(--br)}}
.lbc{{position:fixed;top:22px;right:26px;font-size:1.25rem;color:var(--mu);cursor:none;background:transparent;border:none;padding:10px;transition:color .3s}}
.lbc:hover{{color:var(--acc)}}
.lbn{{position:fixed;top:50%;transform:translateY(-50%);font-size:1.9rem;color:var(--mu);cursor:none;padding:16px;background:transparent;border:none;transition:color .3s;line-height:1}}
.lbn:hover{{color:var(--acc)}}
#lbcnt{{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);font-size:.54rem;letter-spacing:.28em;text-transform:uppercase;color:var(--mu)}}
"""
    js = f"""
const photos={lb_json};let cur=0;
function showPhoto(i,anim){{
  cur=((i%photos.length)+photos.length)%photos.length;
  const img=document.getElementById('lbimg');
  if(anim)gsap.fromTo(img,{{opacity:0,scale:.96}},{{opacity:1,scale:1,duration:.32,ease:'power2.out'}});
  img.src=photos[cur];
  document.getElementById('lbcnt').textContent=(cur+1)+' / '+photos.length;
}}
function openLb(i){{
  const lb=document.getElementById('lb');lb.classList.add('open');
  document.body.style.overflow='hidden';showPhoto(i,true);
}}
function closeLb(){{document.getElementById('lb').classList.remove('open');document.body.style.overflow='';}}
document.querySelectorAll('.gi').forEach(el=>el.addEventListener('click',()=>openLb(+el.dataset.i)));
document.getElementById('lbclose').addEventListener('click',closeLb);
document.getElementById('lbprev').addEventListener('click',()=>showPhoto(cur-1,true));
document.getElementById('lbnext').addEventListener('click',()=>showPhoto(cur+1,true));
document.getElementById('lb').addEventListener('click',e=>{{if(e.target===document.getElementById('lb'))closeLb();}});
document.addEventListener('keydown',e=>{{
  if(!document.getElementById('lb').classList.contains('open'))return;
  if(e.key==='Escape')closeLb();
  if(e.key==='ArrowLeft')showPhoto(cur-1,true);
  if(e.key==='ArrowRight')showPhoto(cur+1,true);
}});
let tx=0;
document.getElementById('lb').addEventListener('touchstart',e=>{{tx=e.touches[0].clientX;}},{{passive:true}});
document.getElementById('lb').addEventListener('touchend',e=>{{const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50)showPhoto(dx>0?cur-1:cur+1,true);}});
gsap.to('.gi',{{opacity:1,y:0,stagger:{{amount:0.55,from:'start'}},duration:.72,ease:'power2.out',scrollTrigger:{{trigger:'#gg',start:'top 88%'}}}});
"""
    return f"""{head(f"{name} — Galerie Photo", t, css)}
{body_open()}
{nav}
<div id="gh"><span class="stag">Galerie photo</span>
  <h1><span class="rw"><span class="ri">Nos <em>instants</em></span></span><br><span class="rw"><span class="ri">capturés</span></span></h1>
</div>
<div id="gg">{items}</div>
<div id="lb" role="dialog" aria-modal="true">
  <button class="lbc" id="lbclose" aria-label="Fermer">✕</button>
  <button class="lbn" id="lbprev" style="left:14px" aria-label="Précédent">‹</button>
  <img id="lbimg" src="" alt="">
  <button class="lbn" id="lbnext" style="right:14px" aria-label="Suivant">›</button>
  <span id="lbcnt"></span>
</div>
{footer}
<script>gsap.registerPlugin(ScrollTrigger);{SHARED_JS}{js}</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# CONTACT
# ══════════════════════════════════════════════════════════════════════════════
def page_contact(lead, t, name, city, phone, maps_url, hours, nav, footer):
    br = hex_rgb(t["bg"]); pc = t["pc"]
    address = lead.get("address",""); rating = lead.get("rating",""); reviews = lead.get("review_count","")
    if hours:
        hrs = "".join(f'<div class="hr"><span class="hd2">{h}</span></div>' for h in hours)
    else:
        hrs = """<div class="hr"><span class="hd2">Lundi</span><span class="ht">Fermé</span></div>
<div class="hr"><span class="hd2">Mar – Ven</span><span class="ht">07h00 – 20h00</span></div>
<div class="hr"><span class="hd2">Samedi</span><span class="ht">07h00 – 21h00</span></div>
<div class="hr"><span class="hd2">Dimanche</span><span class="ht">08h00 – 18h00</span></div>"""
    ph_row  = f'<div class="ci"><div class="cii">📞</div><div><span class="cil">Téléphone</span><span class="civ"><a href="tel:{phone}">{phone}</a></span></div></div>' if phone else ""
    mp_row  = f'<div class="ci"><div class="cii">&#x1F5FA;</div><div><span class="cil">Google Maps</span><span class="civ"><a href="{maps_url}" target="_blank">Voir l\'itin&eacute;raire &rarr;</a></span></div></div>' if maps_url else ""
    rt_row  = f'<div class="ci"><div class="cii">⭐</div><div><span class="cil">Note Google</span><span class="civ">{rating}/5 &mdash; {reviews} avis</span></div></div>' if rating else ""
    addr_enc = address.replace(" ","+").replace(",","%2C") if address else ""
    map_embed = (f'<div style="height:400px;overflow:hidden;border-top:1px solid var(--br);position:relative">'
                 f'<iframe title="Carte {name}" src="https://maps.google.com/maps?q={addr_enc}&output=embed&z=15" '
                 f'width="100%" height="100%" style="border:0;filter:grayscale(80%) brightness(.68) contrast(1.1)" '
                 f'allowfullscreen loading="lazy"></iframe></div>') if address else ""
    css = f"""
#ch{{padding:140px 5vw 58px;background:var(--s2);border-bottom:1px solid var(--br)}}
#ch h1{{font-family:var(--fd),serif;font-size:clamp(2.8rem,7vw,6.5rem);font-weight:300;margin-top:14px;line-height:.9}}
#ch h1 em{{font-style:italic;color:var(--acc)}}
#cm{{display:grid;grid-template-columns:1fr 1fr}}
@media(max-width:900px){{#cm{{grid-template-columns:1fr}}}}
.cc{{padding:58px 5vw;border-right:1px solid var(--br)}}.cc:last-child{{border-right:none;background:var(--s1)}}
.cc h3{{font-family:var(--fd),serif;font-size:1.5rem;font-weight:300;margin-bottom:30px}}
.hr{{display:flex;justify-content:space-between;align-items:baseline;padding:12px 0;border-bottom:1px solid var(--br);font-size:.82rem;opacity:0;transform:translateX(-12px)}}
.hr:last-child{{border-bottom:none}}.hd2{{color:var(--txt)}}.ht{{color:var(--acc);letter-spacing:.06em}}
.ci{{display:flex;align-items:flex-start;gap:13px;padding:14px 0;border-bottom:1px solid var(--br);opacity:0;transform:translateX(12px)}}
.ci:last-of-type{{border-bottom:none}}
.cii{{width:30px;height:30px;border:1px solid rgba({pc},.3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.74rem;color:var(--acc);flex-shrink:0}}
.cil{{font-size:.51rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);display:block;margin-bottom:3px}}
.civ{{font-size:.84rem}}.civ a{{color:inherit;text-decoration:none;transition:color .3s}}.civ a:hover{{color:var(--acc)}}
"""
    js = """
gsap.to('.hr',{opacity:1,x:0,stagger:.08,duration:.62,ease:'power2.out',scrollTrigger:{trigger:'#cm',start:'top 78%'}});
gsap.to('.ci',{opacity:1,x:0,stagger:.1,duration:.62,ease:'power2.out',scrollTrigger:{trigger:'#cm',start:'top 78%'}});
"""
    return f"""{head(f"{name} — Contact &amp; Accès", t, css)}
{body_open()}
{nav}
<div id="ch"><span class="stag">Contact &amp; Accès</span>
  <h1><span class="rw"><span class="ri">Venez nous</span></span><br><span class="rw"><span class="ri"><em>rendre visite</em></span></span></h1>
</div>
<div id="cm">
  <div class="cc"><h3>Horaires</h3>{hrs}</div>
  <div class="cc"><h3>Coordonnées</h3>
    <div class="ci"><div class="cii">📍</div><div><span class="cil">Adresse</span><span class="civ">{address}</span></div></div>
    {ph_row}{mp_row}{rt_row}
    <div style="margin-top:28px;display:flex;gap:12px;flex-wrap:wrap">
      {"" if not phone else f'<a href="tel:{phone}" class="btn-a"><span>📞 Appeler</span></a>'}
      <a href="./reservation.html" class="btn-a"><span>📅 Réserver</span></a>
    </div>
  </div>
</div>
{map_embed}
{footer}
<script>gsap.registerPlugin(ScrollTrigger);{SHARED_JS}{js}</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_admin(lead, t, name, city, phone, maps_url, slug, github_url):
    br = hex_rgb(t["bg"]); pc = t["pc"]
    rating  = lead.get("rating","—")
    reviews = lead.get("review_count","—")
    address = lead.get("address","—")
    slug_safe = re.sub(r'[^a-z0-9]','_', name.lower())
    pages = ["index.html","menu.html","galerie.html","reservation.html","contact.html"]
    page_links = "".join(
        f'<a href="./{p}" target="_blank" class="pl"><span class="pl-icon">↗</span>{p}</a>'
        for p in pages
    )
    css = f"""
body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--txt);min-height:100vh;cursor:auto}}
*{{box-sizing:border-box;margin:0;padding:0}}
::-webkit-scrollbar{{width:1px}}::-webkit-scrollbar-thumb{{background:var(--acc)}}
#adm-head{{background:var(--s1);border-bottom:1px solid var(--br);padding:22px 5vw;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.adm-logo{{font-family:var(--fd),serif;font-size:1.1rem;color:var(--acc);letter-spacing:.18em}}
.adm-sub{{font-size:.56rem;letter-spacing:.3em;text-transform:uppercase;color:var(--mu)}}
.adm-badge{{padding:5px 14px;border:1px solid var(--br);font-size:.54rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mu)}}
#adm-body{{padding:40px 5vw;max-width:1200px;margin:0 auto}}
.sec-title{{font-family:var(--fd),serif;font-size:1.4rem;font-weight:300;color:var(--acc);margin-bottom:20px;letter-spacing:.06em}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:40px}}
.card{{background:var(--s1);border:1px solid var(--br);padding:22px 20px;position:relative;overflow:hidden}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:var(--acc);opacity:.4}}
.card-val{{font-family:var(--fd),serif;font-size:2.4rem;font-weight:300;color:var(--acc);display:block;line-height:1;margin-bottom:6px}}
.card-lbl{{font-size:.52rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mu)}}
.plinks{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:40px}}
.pl{{display:inline-flex;align-items:center;gap:7px;padding:9px 16px;border:1px solid var(--br);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mu);text-decoration:none;transition:all .3s}}
.pl:hover{{border-color:var(--acc);color:var(--acc)}}
.pl-icon{{font-size:.8rem;color:var(--acc)}}
.tbl-wrap{{overflow-x:auto;border:1px solid var(--br);margin-bottom:40px}}
table{{width:100%;border-collapse:collapse;font-size:.78rem}}
thead th{{background:var(--s1);padding:12px 14px;text-align:left;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);font-weight:400;border-bottom:1px solid var(--br);white-space:nowrap}}
tbody tr{{border-bottom:1px solid var(--br);transition:background .3s}}
tbody tr:hover{{background:var(--s1)}}
tbody td{{padding:11px 14px;color:var(--txt);vertical-align:top}}
.empty{{padding:40px;text-align:center;color:var(--mu);font-style:italic;font-size:.82rem}}
.btn-adm{{display:inline-flex;align-items:center;gap:8px;padding:10px 22px;border:1px solid var(--br);font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);background:transparent;cursor:pointer;transition:all .3s;font-family:'DM Sans',sans-serif}}
.btn-adm:hover{{border-color:var(--acc);color:var(--acc)}}
.btn-adm.danger:hover{{border-color:#c0392b;color:#c0392b}}
.adm-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px}}
"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin — {name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:{t["bg"]};--s1:{t["s1"]};--s2:{t["s2"]};--acc:{t["acc"]};--txt:{t["txt"]};--mu:{t["muted"]};--br:{t["border"]};--fd:'{t["fd"]}'}}
{css}
</style>
</head>
<body>
<div id="adm-head">
  <div>
    <div class="adm-logo">{name}</div>
    <div class="adm-sub">Administration · {city}</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
    <span class="adm-badge">{t["tag"]}</span>
    <a href="./index.html" target="_blank" style="color:var(--acc);font-size:.6rem;letter-spacing:.14em;text-decoration:none;text-transform:uppercase">Voir le site ↗</a>
  </div>
</div>
<div id="adm-body">
  <!-- STATS CARDS -->
  <div class="sec-title">Vue d'ensemble</div>
  <div class="cards">
    <div class="card"><span class="card-val" id="cv-res">—</span><span class="card-lbl">Réservations</span></div>
    <div class="card"><span class="card-val">{rating}</span><span class="card-lbl">Note Google</span></div>
    <div class="card"><span class="card-val">{reviews}</span><span class="card-lbl">Avis clients</span></div>
    <div class="card"><span class="card-val">5</span><span class="card-lbl">Pages du site</span></div>
    <div class="card"><span class="card-val" id="cv-guests">—</span><span class="card-lbl">Couverts totaux</span></div>
  </div>
  <!-- PAGE LINKS -->
  <div class="sec-title">Pages du site</div>
  <div class="plinks">{page_links}
    {"" if not github_url else f'<a href="{github_url}" target="_blank" class="pl"><span class="pl-icon">🌐</span>Site en ligne</a>'}
  </div>
  <!-- RESERVATIONS TABLE -->
  <div class="sec-title">Réservations</div>
  <div class="adm-row">
    <button class="btn-adm" onclick="exportCSV()">⬇ Exporter CSV</button>
    <button class="btn-adm danger" onclick="clearAll()">🗑 Effacer tout</button>
    <span id="res-count" style="font-size:.62rem;color:var(--mu);letter-spacing:.1em"></span>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>Prénom</th><th>Nom</th><th>Email</th><th>Téléphone</th>
        <th>Date</th><th>Heure</th><th>Pers.</th><th>Message</th><th>Soumis le</th>
      </tr></thead>
      <tbody id="res-tbody"><tr><td colspan="9" class="empty">Chargement…</td></tr></tbody>
    </table>
  </div>
  <!-- INFO -->
  <div class="sec-title">Informations établissement</div>
  <div style="background:var(--s1);border:1px solid var(--br);padding:22px;font-size:.82rem;line-height:2;color:var(--mu)">
    <div><strong style="color:var(--txt)">Nom :</strong> {name}</div>
    <div><strong style="color:var(--txt)">Adresse :</strong> {address}</div>
    {"" if not phone else f'<div><strong style="color:var(--txt)">Téléphone :</strong> {phone}</div>'}
    {"" if not maps_url else f'<div><strong style="color:var(--txt)">Google Maps :</strong> <a href="{maps_url}" target="_blank" style="color:var(--acc)">{maps_url}</a></div>'}
    <div><strong style="color:var(--txt)">Catégorie :</strong> {t["tag"]}</div>
    {"" if not github_url else f'<div><strong style="color:var(--txt)">Site live :</strong> <a href="{github_url}" target="_blank" style="color:var(--acc)">{github_url}</a></div>'}
  </div>
</div>
<script>
const KEY='res_{slug_safe}';
function loadRes(){{
  const data=JSON.parse(localStorage.getItem(KEY)||'[]');
  const tbody=document.getElementById('res-tbody');
  document.getElementById('cv-res').textContent=data.length;
  document.getElementById('res-count').textContent=data.length+' réservation'+(data.length!==1?'s':'');
  const guests=data.reduce((s,r)=>s+(+r.guests||0),0);
  document.getElementById('cv-guests').textContent=guests||'—';
  if(!data.length){{tbody.innerHTML='<tr><td colspan="9" class="empty">Aucune réservation enregistrée pour le moment.</td></tr>';return;}}
  tbody.innerHTML=data.slice().reverse().map(r=>{{
    const ds=r.date?new Date(r.date+'T12:00:00').toLocaleDateString('fr-FR',{{day:'2-digit',month:'2-digit',year:'numeric'}}):'—';
    const ts=r.ts?new Date(r.ts).toLocaleString('fr-FR',{{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}}):'—';
    return '<tr><td>'+esc(r.fn||'')+'</td><td>'+esc(r.ln||'')+'</td><td>'+esc(r.email||'')+'</td><td>'+esc(r.tel||'—')+'</td><td>'+ds+'</td><td>'+(r.time||'—')+'</td><td>'+(r.guests||'—')+'</td><td>'+esc(r.msg||'—')+'</td><td>'+ts+'</td></tr>';
  }}).join('');
}}
function esc(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}
function exportCSV(){{
  const data=JSON.parse(localStorage.getItem(KEY)||'[]');
  if(!data.length){{alert('Aucune réservation à exporter.');return;}}
  const head='Prénom,Nom,Email,Téléphone,Date,Heure,Personnes,Message,Soumis';
  const rows=data.map(r=>[r.fn,r.ln,r.email,r.tel,r.date,r.time,r.guests,r.msg,r.ts].map(v=>'"'+(v||'').replace(/"/g,'""')+'"').join(','));
  const csv=head+'\\n'+rows.join('\\n');
  const a=document.createElement('a');a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='reservations_{slug_safe}_'+new Date().toISOString().split('T')[0]+'.csv';a.click();
}}
function clearAll(){{
  if(confirm('Effacer toutes les réservations ? Cette action est irréversible.')){{
    localStorage.removeItem(KEY);loadRes();
  }}
}}
loadRes();
</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# QUALITY VALIDATOR
# ══════════════════════════════════════════════════════════════════════════════
def validate_site(output_dir, name):
    out = pathlib.Path(output_dir); ok = True
    required = ["index.html","menu.html","reservation.html","galerie.html","contact.html","admin.html",".nojekyll","client_info.json"]
    for f in required:
        if not (out/f).exists():
            print(f"  ✗ MISSING: {f}"); ok=False
    checks = {
        "index.html":   ["gl_FragColor","fbm","Lenis","ScrollTrigger","unsplash.com","id=\"ldr\"","btn-a"],
        "menu.html":    ["unsplash.com","mcat","btn-a","ScrollTrigger"],
        "reservation.html": ["localStorage","slot","btn-a"],
        "galerie.html": ["unsplash.com","openLb","id=\"lb\"","btn-a"],
        "contact.html": ["btn-a"],
        "admin.html":   ["localStorage","exportCSV","res-tbody"],
    }
    for page, tokens in checks.items():
        p = out/page
        if not p.exists(): continue
        content = p.read_text(encoding="utf-8")
        leftover = re.findall(r'__[A-Z_]{2,}__', content)
        if leftover:
            print(f"  ✗ LEFTOVER MARKERS in {page}: {leftover[:3]}"); ok=False
        for tok in tokens:
            if tok not in content:
                print(f"  ✗ MISSING '{tok}' in {page}"); ok=False
    if ok:
        sizes = {f: (out/f).stat().st_size for f in ["index.html","menu.html","reservation.html","galerie.html","contact.html","admin.html"] if (out/f).exists()}
        total = sum(sizes.values())
        print(f"  ✓ Quality OK — {len(sizes)} pages — {total//1024}KB total")
    return ok

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE FULL SITE
# ══════════════════════════════════════════════════════════════════════════════
def generate_site(lead, output_dir, github_url="", photos_override=None):
    name     = lead.get("name","")
    category = lead.get("category","")
    address  = lead.get("address","")
    phone    = lead.get("phone","")
    rating   = float(lead.get("rating") or 4.8)
    reviews  = int(lead.get("review_count") or 0)
    maps_url = lead.get("maps_url") or lead.get("google_maps_url","")
    hours    = lead.get("hours") or []
    slug     = lead.get("slug","")
    parts    = [p.strip() for p in address.split(",")]
    city     = parts[-2] if len(parts)>=2 else (parts[-1] if parts else "France")
    initial  = name[0].upper() if name else "A"

    t  = get_theme(category, slug)
    # Priority: Higgsfield override > Pexels library > built-in Unsplash
    if photos_override:
        ph = photos_override
    elif _PHOTO_LIB:
        _lib = _lib_photos(category, slug, _PHOTO_LIB)
        ph = _lib if _lib else get_photos(category)
    else:
        ph = get_photos(category)
    out = pathlib.Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    def nav(page): return nav_html(page, name, initial, t)
    def foot():    return footer_html(name, address, city, phone, maps_url)

    pages = {
        "index.html":       page_index(lead, t, ph, name, city, phone, str(rating), str(reviews), maps_url, nav("index.html"), foot()),
        "menu.html":        page_menu(lead, t, ph, name, city, nav("menu.html"), foot()),
        "reservation.html": page_reservation(lead, t, name, city, phone, maps_url, nav("reservation.html"), foot()),
        "galerie.html":     page_galerie(lead, t, ph, name, city, nav("galerie.html"), foot()),
        "contact.html":     page_contact(lead, t, name, city, phone, maps_url, hours, nav("contact.html"), foot()),
        "admin.html":       page_admin(lead, t, name, city, phone, maps_url, slug, github_url),
    }

    for fname, html in pages.items():
        (out/fname).write_text(html, encoding="utf-8")

    (out/".nojekyll").touch()
    (out/"client_info.json").write_text(
        json.dumps({k: lead.get(k) for k in ["name","category","address","phone","rating","review_count","slug"]}
                   | {"public_site":github_url,"pages":list(pages.keys())},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    valid = validate_site(out, name)
    if not valid:
        print(f"  ⚠ Site generated with warnings for: {name}")
    return valid

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Generate world-class French business websites")
    ap.add_argument("leads_file")
    ap.add_argument("output_dir")
    ap.add_argument("--github-username", default="")
    ap.add_argument("--higgsfield", action="store_true", help="Generate AI photos using Higgsfield CLI")
    ap.add_argument("--higgsfield-model", default="flux_2", help="Higgsfield model (default: flux_2 = 1 credit/image)")
    args = ap.parse_args()

    leads = json.loads(pathlib.Path(args.leads_file).read_text(encoding="utf-8"))
    out   = pathlib.Path(args.output_dir)
    total = 0; ok_count = 0

    for lead in leads:
        slug = lead.get("slug","")
        name = lead.get("name","")
        if not slug:
            print(f"  ⚠ Skipping lead with no slug: {name}")
            continue
        gh = (f"https://{args.github_username}.github.io/{slug}-site"
              if args.github_username and slug else "")
        print(f"\n[{total+1}] Generating: {name} ({slug})")
        photos_override = None
        if args.higgsfield:
            try:
                import sys as _sys; _sys.path.insert(0, str(pathlib.Path(__file__).parent))
                import higgsfield_photos as _hfp
                cat        = lead.get("category", "default")
                addr_parts = [x.strip() for x in lead.get("address","").split(",")]
                city_name  = addr_parts[-2] if len(addr_parts) >= 2 else "France"
                print(f"  Higgsfield: generating AI photos ({args.higgsfield_model})...")
                photos_override = _hfp.generate_photos(cat, city_name, name, args.higgsfield_model)
                print(f"  AI photos generated")
            except Exception as _e:
                print(f"  Higgsfield failed ({_e}), falling back to Unsplash")
        ok = generate_site(lead, out/slug, gh, photos_override=photos_override)
        total += 1
        if ok: ok_count += 1

    print(f"\n{'='*50}")
    print(f"Generated {ok_count}/{total} sites successfully.")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()