/**
 * Cloudflare Worker — прокси для Unisender Subscribe API.
 * API-ключ хранится в environment variable, НЕ в клиентском коде.
 *
 * Деплой:
 *   1. npx wrangler secret put UNISENDER_API_KEY
 *   2. npx wrangler deploy
 *   3. Wrangler создаст Worker Custom Domain subscribe.iraai.ru.
 */

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowedOrigins = new Set([
      'https://iraai.ru',
      'https://www.iraai.ru',
      'https://makefacktory90-lgtm.github.io',
      'http://localhost:8000',
      'http://127.0.0.1:8000',
    ]);
    const corsOrigin = allowedOrigins.has(origin) ? origin : 'https://iraai.ru';
    const corsHeaders = {
      'Access-Control-Allow-Origin': corsOrigin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin',
    };

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders,
      });
    }

    if (request.method !== 'POST') {
      return jsonResponse({ ok: false, error: 'Method not allowed' }, 405, corsHeaders);
    }

    if (!env.UNISENDER_API_KEY) {
      return jsonResponse({ ok: false, error: 'UNISENDER_API_KEY is not configured' }, 500, corsHeaders);
    }

    let payload;
    try {
      payload = await request.json();
    } catch (error) {
      return jsonResponse({ ok: false, error: 'Invalid JSON body' }, 400, corsHeaders);
    }

    const { email, name, tags, fields } = payload;

    if (!email || !email.includes('@')) {
      return jsonResponse({ ok: false, error: 'Invalid email' }, 400, corsHeaders);
    }

    const params = new URLSearchParams({
      format: 'json',
      api_key: env.UNISENDER_API_KEY,
      list_ids: '1',
      double_optin: '3',
      overwrite: '2',
    });

    params.set('fields[email]', email);

    if (typeof name === 'string' && name.trim()) {
      params.set('fields[Name]', name.trim());
    }

    if (Array.isArray(tags) && tags.length) {
      params.set('tags', tags.filter(Boolean).join(','));
    }

    if (fields && typeof fields === 'object') {
      Object.entries(fields).forEach(([fieldName, fieldValue]) => {
        const cleanName = typeof fieldName === 'string' ? fieldName.trim() : '';
        const cleanValue = String(fieldValue ?? '').trim();

        if (cleanName && cleanValue) {
          params.set(`fields[${cleanName}]`, cleanValue);
        }
      });
    }

    const url = 'https://api.unisender.com/ru/api/subscribe?' + params.toString();

    try {
      const res = await fetch(url);
      const data = await res.json().catch(() => null);

      if (!res.ok || !data) {
        return jsonResponse({ ok: false, error: 'Unisender request failed' }, 502, corsHeaders);
      }

      if (data.error) {
        return jsonResponse({ ok: false, error: data.error, code: data.code || null }, 502, corsHeaders);
      }

      if (!data.result || !data.result.person_id) {
        return jsonResponse({ ok: false, error: 'Unisender did not return person_id' }, 502, corsHeaders);
      }

      return jsonResponse({ ok: true, result: data.result }, 200, corsHeaders);
    } catch (error) {
      return jsonResponse({ ok: false, error: 'Unisender request failed' }, 502, corsHeaders);
    }
  },
};

function jsonResponse(payload, status, corsHeaders) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
      ...corsHeaders,
    },
  });
}
