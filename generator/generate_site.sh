#!/bin/bash
# generate_site.sh — Build a complete Next.js website for a French business
# Args: $1=name $2=category $3=address $4=phone $5=rating $6=reviews $7=maps_url $8=slug

set -e

NAME="$1"
CATEGORY="$2"
ADDRESS="$3"
PHONE="$4"
RATING="$5"
REVIEWS="$6"
MAPS_URL="$7"
SLUG="$8"

if [ -z "$SLUG" ]; then
  echo "ERROR: Missing arguments. Usage: $0 name category address phone rating reviews maps_url slug"
  exit 1
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  Generating site for: $NAME"
echo "  Slug: $SLUG"
echo "═══════════════════════════════════════════════"

PUBLIC_SITE_DIR="$HOME/france-leads-automation/sites/$SLUG/public-site"
LOCAL_MIRROR_DIR="$HOME/أعمالي/$SLUG/public-site"

# Create directories
mkdir -p "$PUBLIC_SITE_DIR"
mkdir -p "$LOCAL_MIRROR_DIR"

cd "$PUBLIC_SITE_DIR"

# Create Next.js app
echo "→ Creating Next.js app..."
npx create-next-app@latest . --typescript --tailwind --eslint --app --yes --no-git 2>&1 | tail -5

# Build the full prompt for Claude
PROMPT="Build a complete production-ready website. Work in the current directory: $(pwd). Do everything without asking.

Business:
- Name: $NAME
- Type: $CATEGORY
- Address: $ADDRESS
- Phone: $PHONE
- Google Maps: $MAPS_URL
- Rating: $RATING/5 ($REVIEWS avis Google)
- Slug: $SLUG

DO ALL OF THE FOLLOWING IN ORDER:

1. CREATE next.config.js (overwrite existing):
\`\`\`js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/$SLUG-site',
  assetPrefix: '/$SLUG-site/',
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true }
}
module.exports = nextConfig
\`\`\`

2. CREATE public/.nojekyll (empty file — required for GitHub Pages)

3. RUN: npm install framer-motion next-themes lucide-react --legacy-peer-deps

4. CHOOSE design theme based on $CATEGORY:
- restaurant / brasserie → deep burgundy #6B1D1D + cream #FDF8F0 + gold #D4AF37
- café / salon de thé → espresso #3D1C02 + cream #FDF6E3 + warm amber #D97706
- boulangerie / pâtisserie → golden wheat #D4A017 + ivory #FFFEF0 + warm brown #8B4513
- pizzeria → terracotta #C0392B + basil green #27AE60 + cream #FDF8F0
- kebab / fast food → bold orange #E67E22 + dark charcoal #2C3E50 + white
- crêperie → sunny yellow #F4D03F + warm brown #8B4513 + cream
- default → deep navy #1A1A2E + gold #D4AF37 + white

5. OVERWRITE app/globals.css with theme CSS variables from chosen palette. Include:
- CSS custom properties for primary, secondary, accent colors
- Smooth scroll behavior
- Custom font import (Google Fonts — Playfair Display for headings, Lato for body)
- Animated gradient keyframes

6. OVERWRITE app/layout.tsx with:
- ThemeProvider from next-themes (modes: dark/light with toggle button in nav)
- <title>$NAME | [city from $ADDRESS]</title>
- Meta description in French (60-160 chars)
- Schema.org JSON-LD (Restaurant or Cafe type) with name, address, phone, rating
- Smooth scroll CSS
- Google Fonts link
- Floating theme toggle button top-right corner

7. OVERWRITE app/page.tsx with ALL these sections using Framer Motion scroll animations:

SECTION 1 — HERO (100vh height):
- Business name as H1 with animated entrance (fadeInUp, 0.8s ease)
- French tagline appropriate for $CATEGORY (e.g., 'La tradition française, revisitée')
- Two CTA buttons: 'Réserver une table' (primary) + 'Notre Carte' (secondary, outline)
- Background: gradient using theme primary + secondary with animated floating circles overlay
- Star rating display: $RATING★ ($REVIEWS avis)
- Animated scroll indicator (bouncing arrow)
- Navigation bar: business name logo + smooth-scroll links to each section

SECTION 2 — ABOUT 'Notre Histoire' (whiteSection bg):
- Large decorative quote mark
- 3 paragraphs in French, warm and personal tone, ~50 words each
- Reference the city from $ADDRESS and the type $CATEGORY
- Three feature cards below: icons + French labels (Qualité, Tradition, Convivialité or similar)
- Animated fade-in on scroll using Framer Motion useInView
- Side image: https://source.unsplash.com/600x400/?french,$CATEGORY,interior

SECTION 3 — MENU 'Notre Carte' (colored section bg):
- Section heading with decorative line
- 4-6 menu categories appropriate for $CATEGORY
- 3-4 items per category with: French name, description, EUR price
- Grid layout: responsive (1 col mobile, 2 col tablet, 3 col desktop)
- Card with hover lift effect (transform translateY + shadow)
- Realistic prices for French market
- Badge showing category icon

SECTION 4 — GALLERY 'Notre Galerie' (white bg):
- 8 images in CSS masonry/grid layout (mix of portrait + landscape)
- Images: https://source.unsplash.com/800x600/?$CATEGORY,food,french&sig=1 through &sig=8
- CSS hover zoom effect (transform scale 1.05, overflow hidden)
- Click to open CSS lightbox (checkbox hack — no JS library)
- Animated reveal on scroll

SECTION 5 — LOCATION 'Nous Trouver' (colored bg):
- Google Maps iframe: <iframe src='https://maps.google.com/maps?q=$ADDRESS&output=embed' />
- Address card with icon
- Phone number with phone icon and click-to-call link
- Opening hours table (typical for $CATEGORY, show all 7 days)
- Directions button linking to $MAPS_URL

SECTION 6 — RESERVATIONS 'Réserver une Table':
- Section intro text in French
- Form with fields: nom complet*, email*, téléphone, date*, heure*, nombre de personnes*, message
- All required fields marked with *
- Submit handler: fetch POST to \`\${process.env.NEXT_PUBLIC_API_URL}/api/reservations\`
  with body: { name, email, phone, date, time, guests, message, businessSlug: '$SLUG' }
  on success: show green confirmation 'Votre réservation a bien été envoyée! Nous vous confirmerons sous 24h.'
  on error: show amber message 'Notre système est momentanément indisponible. Appelez-nous au $PHONE'
- Phone number $PHONE displayed in large text with phone icon
- Form has smooth validation (red border + error text on required fields)

SECTION 7 — FOOTER:
- Business name in theme font
- Address, phone, email placeholder
- Opening hours quick view
- Social icons (Instagram, Facebook, TripAdvisor) as placeholder links
- Copyright © $(date +%Y) $NAME. Tous droits réservés.
- Bottom bar: 'Site créé par France Leads' in tiny muted text

8. ADD analytics to app/layout.tsx:
\`\`\`tsx
'use client'
import { useEffect } from 'react'
export function Analytics() {
  useEffect(() => {
    fetch(\`\${process.env.NEXT_PUBLIC_API_URL}/api/analytics\`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: window.location.pathname,
        referrer: document.referrer,
        userAgent: navigator.userAgent,
        businessSlug: '$SLUG'
      })
    }).catch(() => {})
  }, [])
  return null
}
\`\`\`
Import and use <Analytics /> in the layout body.

9. CREATE .env.local:
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_BUSINESS_SLUG=$SLUG
NEXT_PUBLIC_BUSINESS_NAME=$NAME

10. RUN: npm run build
    Fix ALL TypeScript and ESLint errors automatically.
    If build fails, examine the error and fix it.
    Verify out/index.html exists after successful build.
    The build MUST succeed with out/index.html present.

IMPORTANT QUALITY REQUIREMENTS:
- Every section must look professionally designed
- Typography: Playfair Display for headings, clean sans-serif for body
- Responsive on all screen sizes
- Smooth animations throughout
- French language throughout (no English text visible to users)
- All placeholder data must be realistic for French market
- Color theme must match $CATEGORY perfectly"

echo "→ Running Claude to build website..."
claude -p "$PROMPT" \
  --allowedTools "Bash,Write,Read,Edit,Glob,Grep" \
  --max-turns 40 \
  --output-format stream-json 2>&1 | tail -20

# Verify build output
if [ ! -f "out/index.html" ]; then
  echo "→ First build attempt failed. Retrying with fix prompt..."
  claude -p "The Next.js build failed. Fix ALL TypeScript and build errors.
Verify next.config.js has: output: 'export', basePath: '/$SLUG-site', assetPrefix: '/$SLUG-site/', images: { unoptimized: true }, eslint: { ignoreDuringBuilds: true }, typescript: { ignoreBuildErrors: true }.
Run npm run build until out/index.html exists.
Current directory: $(pwd)" \
    --allowedTools "Bash,Write,Read,Edit,Glob,Grep" \
    --max-turns 20 \
    --output-format stream-json 2>&1 | tail -10
fi

if [ -f "out/index.html" ]; then
  echo "✅ PUBLIC SITE SUCCESS: $NAME"
  echo "   Output: $PUBLIC_SITE_DIR/out/index.html"

  # Mirror to local storage
  echo "→ Mirroring to local storage..."
  cp -r "$PUBLIC_SITE_DIR/." "$LOCAL_MIRROR_DIR/"
  echo "✅ Mirrored to: $LOCAL_MIRROR_DIR"
else
  echo "❌ SITE BUILD FAILED for: $NAME"
  exit 1
fi
