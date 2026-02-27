/**
 * Cloudflare Worker — прокси для Unisender Subscribe API.
 * API-ключ хранится в environment variable, НЕ в клиентском коде.
 *
 * Деплой:
 *   1. Зайди на dash.cloudflare.com → Workers & Pages → Create Worker
 *   2. Вставь этот код
 *   3. Settings → Variables → добавь: UNISENDER_API_KEY = твой ключ
 *   4. Задай route: subscribe.iraai.ru/* (или используй workers.dev URL)
 *   5. В index.html замени SUBSCRIBE_WORKER_URL на реальный URL воркера
 */

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': 'https://iraai.ru',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const { email } = await request.json();

    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: 'Invalid email' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const url = 'https://api.unisender.com/ru/api/subscribe?format=json'
      + '&api_key=' + env.UNISENDER_API_KEY
      + '&list_ids=1'
      + '&fields[email]=' + encodeURIComponent(email)
      + '&double_optin=3'
      + '&overwrite=2';

    const res = await fetch(url);
    const data = await res.json();

    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://iraai.ru',
      },
    });
  },
};
