#!/bin/bash
# send_telegram.sh — Send business creation notification to Telegram
# Args: $1=name $2=category $3=address $4=phone $5=rating $6=reviews $7=maps_url $8=github_url $9=slug

NAME="$1"
CATEGORY="$2"
ADDRESS="$3"
PHONE="$4"
RATING="$5"
REVIEWS="$6"
MAPS_URL="$7"
GITHUB_URL="$8"
SLUG="$9"

ENV_FILE="$HOME/france-leads-automation/.env"
if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "⚠️  Telegram not configured (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing)"
  echo "   Set them in $ENV_FILE to enable notifications"
  exit 0
fi

echo "→ Sending Telegram notification..."

MESSAGE="🏪 *Nouveau site créé\\!*

📍 *Business:* $NAME
🏷️ *Catégorie:* $CATEGORY
📫 *Adresse:* $ADDRESS
📞 *Téléphone:* $PHONE
⭐ *Note Google:* $RATING/5 \\($REVIEWS avis\\)
🗺️ [Voir sur Google Maps]($MAPS_URL)

🌐 *Site public live:*
$GITHUB_URL

🔐 *Admin panel \\(local\\):*
\`cd ~/أعمالي/$SLUG/admin && npm run dev \\-\\- \\-\\-port 3001\`
Ouvrir: http://localhost:3001/admin
Login: admin / admin123 ⚠️ À changer\\!

📡 *Accès distant:*
\`bash ~/أعمالي/$SLUG/admin/scripts/start-with-tunnel.sh\`

✅ _Prêt à envoyer au propriétaire\\!_"

RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"${TELEGRAM_CHAT_ID}\",
    \"text\": $(echo "$MESSAGE" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))"),
    \"parse_mode\": \"MarkdownV2\",
    \"disable_web_page_preview\": false
  }" 2>&1)

if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('ok') else 1)" 2>/dev/null; then
  echo "✅ Telegram notification sent!"
else
  echo "⚠️  Telegram send issue: $RESPONSE"
  # Try plain text fallback
  PLAIN_MSG="✅ Nouveau site créé: $NAME
Catégorie: $CATEGORY
Adresse: $ADDRESS
Téléphone: $PHONE
Note: $RATING/5 ($REVIEWS avis)

Site public: $GITHUB_URL

Admin local:
cd ~/أعمالي/$SLUG/admin && npm run dev -- --port 3001
URL: http://localhost:3001/admin
Login: admin / admin123"

  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=$PLAIN_MSG" > /dev/null
  echo "✅ Telegram fallback notification sent"
fi
