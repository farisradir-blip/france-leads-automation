/**
 * Cloudflare Worker — Telegram Bot Webhook
 *
 * Listens for Telegram messages. When "إذهب" is received,
 * triggers GitHub Actions workflow and replies immediately.
 *
 * Environment variables (set in Cloudflare Dashboard → Worker Settings → Variables):
 *   TELEGRAM_BOT_TOKEN   — your bot token
 *   TELEGRAM_CHAT_ID     — your chat ID (only this chat can trigger)
 *   GITHUB_TOKEN         — classic PAT with repo + workflow permissions
 *   GITHUB_USERNAME      — farisradir-blip
 *   GITHUB_REPO          — france-leads-automation
 */

const TRIGGER_WORDS = ["إذهب", "اذهب", "go", "start", "ابدأ", "ابدا"];

async function sendTelegram(token, chat_id, text) {
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id, text, parse_mode: "HTML" }),
  });
}

async function triggerGitHubActions(token, username, repo) {
  const url = `https://api.github.com/repos/${username}/${repo}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ event_type: "telegram-trigger" }),
  });
  return res.status;
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("France Leads Bot — OK", { status: 200 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("Bad JSON", { status: 400 });
    }

    const message = update.message || update.edited_message;
    if (!message) return new Response("OK");

    const chat_id = String(message.chat.id);
    const text    = (message.text || "").trim();

    // Security: only respond to authorized chat
    if (chat_id !== String(env.TELEGRAM_CHAT_ID)) {
      return new Response("Unauthorized", { status: 403 });
    }

    const isGo = TRIGGER_WORDS.some(w => text.toLowerCase().includes(w.toLowerCase()));

    if (isGo) {
      // Trigger GitHub Actions
      const status = await triggerGitHubActions(
        env.GITHUB_TOKEN,
        env.GITHUB_USERNAME,
        env.GITHUB_REPO
      );

      if (status === 204) {
        await sendTelegram(
          env.TELEGRAM_BOT_TOKEN,
          chat_id,
          "⏳ <b>C'est parti!</b>\n\nScraping Google Maps → Génération des sites → Déploiement GitHub Pages\n\n⏱ Durée estimée: <b>10–20 minutes</b>\nTu recevras les résultats ici dès que c'est prêt."
        );
      } else {
        await sendTelegram(
          env.TELEGRAM_BOT_TOKEN,
          chat_id,
          `⚠️ Erreur GitHub Actions (HTTP ${status}). Vérifiez le token.`
        );
      }
    } else if (text.startsWith("/start") || text.startsWith("/help")) {
      await sendTelegram(
        env.TELEGRAM_BOT_TOKEN,
        chat_id,
        "🇫🇷 <b>France Leads Bot</b>\n\nEnvoie <b>إذهب</b> pour lancer l'automatisation:\n• Scraping Google Maps\n• Génération des sites web\n• Déploiement GitHub Pages gratuit\n• Notification avec les liens\n\n⚡ Fonctionne même si ton PC est éteint!"
      );
    }

    return new Response("OK");
  },
};
