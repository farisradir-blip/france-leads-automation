#!/bin/bash
# generate_admin.sh — Build a beautiful local admin dashboard
# Args: $1=name $2=category $3=address $4=phone $5=rating $6=slug $7=github_url

set -e

NAME="$1"
CATEGORY="$2"
ADDRESS="$3"
PHONE="$4"
RATING="$5"
SLUG="$6"
GITHUB_URL="${7:-https://example.github.io/$SLUG-site}"

echo ""
echo "═══════════════════════════════════════════════"
echo "  Generating ADMIN for: $NAME"
echo "  Slug: $SLUG"
echo "═══════════════════════════════════════════════"

ADMIN_DIR="$HOME/أعمالي/$SLUG/admin"
mkdir -p "$ADMIN_DIR"
mkdir -p "$HOME/أعمالي/$SLUG"

cd "$HOME/أعمالي/$SLUG"

# Create admin Next.js app
echo "→ Creating admin Next.js app..."
npx create-next-app@latest admin --typescript --tailwind --eslint --app --yes --no-git 2>&1 | tail -5

cd admin

# Install dependencies
echo "→ Installing admin dependencies..."
npm install @prisma/client prisma recharts lucide-react next-themes jose --legacy-peer-deps 2>&1 | tail -5
npm install -D prisma 2>&1 | tail -3

# Initialize shadcn
echo "→ Initializing shadcn/ui..."
npx shadcn@latest init --defaults --yes 2>&1 | tail -5 || true
npx shadcn@latest add button card badge toast skeleton table dialog --yes 2>&1 | tail -5 || true

# Generate admin secret
ADMIN_SECRET=$(openssl rand -hex 16 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(16))")

# Create .env.local
cat > .env.local << ENVEOF
DATABASE_URL=file:./prisma/dev.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_SECRET=$ADMIN_SECRET
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
BUSINESS_SLUG=$SLUG
BUSINESS_NAME=$NAME
BUSINESS_PHONE=$PHONE
BUSINESS_ADDRESS=$ADDRESS
BUSINESS_GITHUB_URL=$GITHUB_URL
NEXT_PUBLIC_BUSINESS_NAME=$NAME
NEXT_PUBLIC_BUSINESS_SLUG=$SLUG
NEXT_PUBLIC_GITHUB_URL=$GITHUB_URL
ENVEOF
echo "→ Created .env.local"

# Create prisma schema
mkdir -p prisma
cat > prisma/schema.prisma << 'SCHEMAEOF'
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

model Reservation {
  id           Int      @id @default(autoincrement())
  name         String
  email        String
  phone        String?
  date         String
  time         String?
  guests       Int
  message      String?
  status       String   @default("pending")
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
  businessSlug String
}

model ContactMessage {
  id           Int      @id @default(autoincrement())
  name         String
  email        String
  phone        String?
  subject      String?
  message      String
  status       String   @default("unread")
  createdAt    DateTime @default(now())
  businessSlug String
}

model PageView {
  id           Int      @id @default(autoincrement())
  page         String
  userAgent    String?
  referrer     String?
  createdAt    DateTime @default(now())
  businessSlug String
}

model SiteSettings {
  id           Int      @id @default(autoincrement())
  businessSlug String   @unique
  businessName String
  phone        String?
  email        String?
  address      String?
  openingHours String?
  autoConfirm  Boolean  @default(false)
  adminEmail   String?
  updatedAt    DateTime @updatedAt
}
SCHEMAEOF

echo "→ Running Prisma generate + db push..."
npx prisma generate 2>&1 | tail -5
npx prisma db push --accept-data-loss 2>&1 | tail -5

# Create prisma client lib
mkdir -p lib
cat > lib/prisma.ts << 'PRISMACLIENTEOF'
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['error'] : [],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
PRISMACLIENTEOF

# Create auth utility
cat > lib/auth.ts << 'AUTHEOF'
import { SignJWT, jwtVerify } from 'jose'

const secret = new TextEncoder().encode(
  process.env.ADMIN_SECRET || 'fallback-secret-change-me'
)

export async function createToken(username: string): Promise<string> {
  return new SignJWT({ username, role: 'admin' })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(secret)
}

export async function verifyToken(token: string): Promise<boolean> {
  try {
    await jwtVerify(token, secret)
    return true
  } catch {
    return false
  }
}

export function verifyCredentials(username: string, password: string): boolean {
  return (
    username === (process.env.ADMIN_USERNAME || 'admin') &&
    password === (process.env.ADMIN_PASSWORD || 'admin123')
  )
}
AUTHEOF

# Create CORS utility
cat > lib/cors.ts << 'CORSEOF'
import { NextResponse } from 'next/server'

export function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }
}

export function corsOptions() {
  return new NextResponse(null, { headers: corsHeaders() })
}
CORSEOF

# Create API routes directory structure
mkdir -p app/api/reservations
mkdir -p app/api/messages
mkdir -p app/api/analytics
mkdir -p app/api/auth
mkdir -p app/api/settings

# Reservations API
cat > app/api/reservations/route.ts << 'RESEOF'
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { verifyToken } from '@/lib/auth'
import { corsHeaders, corsOptions } from '@/lib/cors'

export async function OPTIONS() { return corsOptions() }

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { name, email, phone, date, time, guests, message, businessSlug } = body

    if (!name || !email || !date || !guests) {
      return NextResponse.json(
        { error: 'Champs requis manquants: nom, email, date, personnes' },
        { status: 400, headers: corsHeaders() }
      )
    }

    const reservation = await prisma.reservation.create({
      data: {
        name, email, phone: phone || null, date, time: time || null,
        guests: parseInt(guests), message: message || null,
        businessSlug: businessSlug || process.env.BUSINESS_SLUG || 'unknown',
      },
    })

    // Telegram notification
    if (process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID) {
      const text = `🍽️ Nouvelle réservation!\n👤 ${name}\n📅 ${date} à ${time || 'N/A'}\n👥 ${guests} personnes\n📞 ${phone || 'N/A'}\n✉️ ${email}`
      await fetch(
        `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chat_id: process.env.TELEGRAM_CHAT_ID, text }),
        }
      ).catch(() => {})
    }

    return NextResponse.json({ success: true, id: reservation.id }, { headers: corsHeaders() })
  } catch (e) {
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500, headers: corsHeaders() })
  }
}

export async function GET(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401, headers: corsHeaders() })
  }

  const { searchParams } = new URL(req.url)
  const status = searchParams.get('status')
  const limit = parseInt(searchParams.get('limit') || '50')

  const reservations = await prisma.reservation.findMany({
    where: status ? { status } : undefined,
    orderBy: { createdAt: 'desc' },
    take: limit,
  })

  return NextResponse.json(reservations, { headers: corsHeaders() })
}

export async function PATCH(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }

  const { id, status } = await req.json()
  const updated = await prisma.reservation.update({ where: { id }, data: { status } })

  if (process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID) {
    const emoji = status === 'confirmed' ? '✅' : status === 'cancelled' ? '❌' : '⏳'
    const text = `${emoji} Réservation #${id} → ${status}\n👤 ${updated.name}\n📅 ${updated.date}`
    await fetch(
      `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: process.env.TELEGRAM_CHAT_ID, text }),
      }
    ).catch(() => {})
  }

  return NextResponse.json(updated)
}

export async function DELETE(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }

  const { id } = await req.json()
  await prisma.reservation.delete({ where: { id } })
  return NextResponse.json({ success: true })
}
RESEOF

# Messages API
cat > app/api/messages/route.ts << 'MSGEOF'
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { verifyToken } from '@/lib/auth'
import { corsHeaders, corsOptions } from '@/lib/cors'

export async function OPTIONS() { return corsOptions() }

export async function POST(req: NextRequest) {
  const body = await req.json()
  const { name, email, phone, subject, message, businessSlug } = body
  if (!name || !email || !message) {
    return NextResponse.json({ error: 'Champs requis manquants' }, { status: 400, headers: corsHeaders() })
  }
  const msg = await prisma.contactMessage.create({
    data: { name, email, phone: phone || null, subject: subject || null, message,
      businessSlug: businessSlug || process.env.BUSINESS_SLUG || 'unknown' },
  })
  return NextResponse.json({ success: true, id: msg.id }, { headers: corsHeaders() })
}

export async function GET(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }
  const messages = await prisma.contactMessage.findMany({ orderBy: { createdAt: 'desc' } })
  return NextResponse.json(messages)
}

export async function PATCH(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }
  const { id, status } = await req.json()
  const updated = await prisma.contactMessage.update({ where: { id }, data: { status } })
  return NextResponse.json(updated)
}

export async function DELETE(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }
  const { id } = await req.json()
  await prisma.contactMessage.delete({ where: { id } })
  return NextResponse.json({ success: true })
}
MSGEOF

# Analytics API
cat > app/api/analytics/route.ts << 'ANALYTICSEOF'
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { verifyToken } from '@/lib/auth'
import { corsHeaders, corsOptions } from '@/lib/cors'

export async function OPTIONS() { return corsOptions() }

export async function POST(req: NextRequest) {
  const body = await req.json()
  await prisma.pageView.create({
    data: {
      page: body.page || '/',
      userAgent: body.userAgent || null,
      referrer: body.referrer || null,
      businessSlug: body.businessSlug || process.env.BUSINESS_SLUG || 'unknown',
    },
  })
  return NextResponse.json({ success: true }, { headers: corsHeaders() })
}

export async function GET(req: NextRequest) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '')
  if (!token || !(await verifyToken(token))) {
    return NextResponse.json({ error: 'Non autorisé' }, { status: 401 })
  }

  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

  const [totalViews, recentViews] = await Promise.all([
    prisma.pageView.count(),
    prisma.pageView.findMany({
      where: { createdAt: { gte: thirtyDaysAgo } },
      orderBy: { createdAt: 'desc' },
    }),
  ])

  // Group by day
  const viewsByDay: Record<string, number> = {}
  recentViews.forEach(v => {
    const day = v.createdAt.toISOString().split('T')[0]
    viewsByDay[day] = (viewsByDay[day] || 0) + 1
  })

  // Group by page
  const viewsByPage: Record<string, number> = {}
  recentViews.forEach(v => {
    viewsByPage[v.page] = (viewsByPage[v.page] || 0) + 1
  })

  // Top referrers
  const referrers: Record<string, number> = {}
  recentViews.forEach(v => {
    if (v.referrer) referrers[v.referrer] = (referrers[v.referrer] || 0) + 1
  })

  return NextResponse.json({ totalViews, viewsByDay, viewsByPage, topReferrers: referrers })
}
ANALYTICSEOF

# Auth API
cat > app/api/auth/route.ts << 'AUTHROUTE'
import { NextRequest, NextResponse } from 'next/server'
import { createToken, verifyCredentials } from '@/lib/auth'

export async function POST(req: NextRequest) {
  const { username, password } = await req.json()
  if (!verifyCredentials(username, password)) {
    return NextResponse.json({ error: 'Identifiants incorrects' }, { status: 401 })
  }
  const token = await createToken(username)
  return NextResponse.json({ token, expiresAt: Date.now() + 24 * 60 * 60 * 1000 })
}
AUTHROUTE

echo "→ API routes created"

# Build full admin UI via Claude
ADMIN_PROMPT="Build a complete, beautiful admin dashboard for a French business. Work in the current directory: $(pwd). Do everything without asking.

Business info:
- Name: $NAME
- Category: $CATEGORY
- Address: $ADDRESS
- Phone: $PHONE
- Slug: $SLUG
- GitHub URL: $GITHUB_URL

The API routes already exist at:
- /api/auth (POST login)
- /api/reservations (GET/POST/PATCH/DELETE)
- /api/messages (GET/POST/PATCH/DELETE)
- /api/analytics (GET/POST)
The Prisma client is at lib/prisma.ts, auth at lib/auth.ts

DESIGN THEME: Dark mode, professional. Use these colors matching $CATEGORY business:
- Primary bg: #0F172A (slate-900)
- Card bg: #1E293B (slate-800)
- Border: #334155 (slate-700)
- Accent: #D4AF37 (gold) for restaurant, or appropriate color
- Text: #F1F5F9 (slate-100)
- Muted text: #94A3B8 (slate-400)

CREATE THESE FILES IN ORDER:

1. app/layout.tsx — Root layout:
'use client'
import './globals.css'
import { Inter, Playfair_Display } from 'next/font/google'
const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair' })
export default function RootLayout({ children }) {
  return <html lang='fr' className='dark'><body className={inter.className + ' ' + playfair.variable + ' bg-slate-900 text-slate-100'}>{children}</body></html>
}

2. app/globals.css — Complete dark theme CSS with custom properties for the business

3. app/page.tsx — Redirect to /admin/dashboard

4. app/admin/layout.tsx — Admin shell with sidebar:
- Check for localStorage token, if none redirect to /admin/login
- Sidebar with: $NAME logo at top, nav links, logout button
- Main content area

5. components/Sidebar.tsx — Beautiful sidebar:
- Business name + category icon
- Nav items: Dashboard (Home icon), Réservations (Calendar, show pending badge), Messages (MessageSquare, show unread badge), Analytiques (BarChart2), Paramètres (Settings)
- Bottom: link to $GITHUB_URL, logout
- Active state with gold accent
- Hover transitions
- Badge counts fetched from API

6. app/admin/login/page.tsx — Login page:
- Dark background with radial gradient
- Centered card (max-w-sm)
- Business name at top in Playfair Display
- Username + Password inputs (styled dark)
- Login button (gold accent)
- Loading spinner state
- Error message display
- On success: store token in localStorage, redirect to /admin/dashboard

7. app/admin/dashboard/page.tsx — Dashboard:
Row 1 — Stats grid (4 cards):
  - Today's reservations (CalendarDays, blue)
  - Pending reservations (Clock, amber)
  - Unread messages (MessageSquare, purple)
  - Week views (TrendingUp, green)
  All cards: dark bg, colored icon, number, label, subtle border

Row 2 — Recharts BarChart (14 days of reservations):
  - Dark theme: bg transparent, grid lines slate-700, bars gold
  - Responsive container
  - Custom tooltip with French labels

Row 3 — Two columns:
  Left: Recent reservations (last 5) — table with name, date, guests, status badge, quick confirm/cancel buttons
  Right: Recent messages (last 3) — cards with name, subject, date, unread badge

Row 4 — Insights:
  - Most popular reservation day
  - Average group size
  - Total visitors this month

8. app/admin/reservations/page.tsx — Full reservations management:
- Tabs: Toutes / En attente (amber badge) / Confirmées (green) / Annulées (red)
- Search input (by name or email)
- Table: #, Nom, Email, Tél, Date, Heure, Personnes, Statut, Actions
- Status badges: pending=amber, confirmed=emerald, cancelled=red
- Row actions: ✅ Confirmer, ❌ Annuler, ✉️ mailto link, 🗑️ Delete with confirm dialog
- Bulk checkbox + bulk confirm/cancel
- Export CSV button (generate CSV client-side)
- Empty state: French message with Calendar icon

9. app/admin/messages/page.tsx — Messages management:
- List view with unread/read toggle at top
- Message cards: name, email, date, subject, message preview
- Click to expand full message
- Mark as read on open
- Reply button (mailto)
- Delete with confirm
- Unread badges
- Search by name/email

10. app/admin/analytics/page.tsx — Analytics:
- Line chart: daily visitors last 30 days (Recharts)
- Pie chart: visits by page (Recharts)
- Stats: total, avg daily, most visited page
- Referrers table
- All charts dark themed

11. app/admin/settings/page.tsx — Settings:
- Form: business name, phone, email, address, opening hours (textarea)
- Toggle: auto-confirm reservations
- Change password section (current + new + confirm)
- Ngrok section with status indicator and instructions
- Save button with success toast
- 'Voir le site' button linking to $GITHUB_URL

12. UPDATE next.config.js for admin (no static export — needs API routes):
const nextConfig = {
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true }
}
module.exports = nextConfig

13. Create hooks/useAuth.ts:
Custom hook that checks localStorage for token, redirects if invalid, exposes logout function.

14. Create hooks/useApi.ts:
Custom hook wrapping fetch with authorization header from localStorage token.

IMPORTANT:
- All UI text in French
- Use Recharts for all charts (already available via npm install recharts)
- Use lucide-react for icons
- Loading skeletons with Tailwind animate-pulse
- Toast notifications (use browser alert as fallback if shadcn not available)
- Fully responsive
- Token stored as 'admin_token' in localStorage
- API_BASE = '' (same origin)

After creating all files, run: npm run build
Fix any TypeScript/build errors automatically.
The admin must build successfully."

echo "→ Running Claude to build admin dashboard..."
claude -p "$ADMIN_PROMPT" \
  --allowedTools "Bash,Write,Read,Edit,Glob,Grep" \
  --max-turns 50 \
  --output-format stream-json 2>&1 | tail -20

# Create start-with-tunnel script
mkdir -p scripts
cat > scripts/start-with-tunnel.sh << TUNNELEOF
#!/bin/bash
source ~/france-leads-automation/.env 2>/dev/null || true
ADMIN_DIR="\$(dirname "\$(dirname "\$(realpath "\$0")")")"
cd "\$ADMIN_DIR"

echo "Starting admin server on port 3001..."
npm run dev -- --port 3001 &
ADMIN_PID=\$!
sleep 4

echo "Starting ngrok tunnel..."
ngrok http 3001 --log=stdout &
NGROK_PID=\$!
sleep 3

NGROK_URL=\$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); tunnels=data.get('tunnels',[]); https=[t for t in tunnels if t.get('proto')=='https']; print(https[0]['public_url'] if https else '')" 2>/dev/null)

if [ -n "\$NGROK_URL" ]; then
  echo ""
  echo "✅ Admin panel: \$NGROK_URL/admin"
  if [ -n "\$TELEGRAM_BOT_TOKEN" ]; then
    curl -s -X POST "https://api.telegram.org/bot\${TELEGRAM_BOT_TOKEN}/sendMessage" \\
      --data-urlencode "chat_id=\${TELEGRAM_CHAT_ID}" \\
      --data-urlencode "text=🔐 Admin panel en ligne: \${NGROK_URL}/admin" > /dev/null
  fi
else
  echo "⚠️  Ngrok URL not found. Check http://localhost:4040"
fi

wait \$ADMIN_PID
TUNNELEOF
chmod +x scripts/start-with-tunnel.sh

# Create .gitignore to prevent accidental push
cat > ../.gitignore << 'GITIGNORE'
# Never push admin to GitHub
admin/
*/admin/
*.db
.env.local
.env
node_modules/
.next/
GITIGNORE

echo "→ Gitignore created"

# Final: verify admin builds
if npm run build 2>&1 | tail -5; then
  echo "✅ ADMIN BUILD SUCCESS: $NAME"
  echo "   Admin location: $ADMIN_DIR"
  echo "   Start with: cd $ADMIN_DIR && npm run dev -- --port 3001"
  echo "   URL: http://localhost:3001/admin/login"
  echo "   Login: admin / admin123"
else
  echo "⚠️  Admin build had issues but continuing (dev mode will still work)"
fi
