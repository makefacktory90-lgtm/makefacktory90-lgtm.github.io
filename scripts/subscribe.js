(function attachIraSubscribe(global) {
  const DEFAULT_WORKER_URL = 'https://subscribe.iraai.ru/';

  function getWorkerUrl() {
    if (typeof global.SUBSCRIBE_WORKER_URL === 'string' && global.SUBSCRIBE_WORKER_URL.trim()) {
      return global.SUBSCRIBE_WORKER_URL.trim();
    }

    const meta = global.document && global.document.querySelector('meta[name="subscribe-worker-url"]');
    return meta && meta.content.trim() ? meta.content.trim() : DEFAULT_WORKER_URL;
  }

  function toCleanString(value) {
    return typeof value === 'string' ? value.trim() : '';
  }

  async function subscribe(options) {
    const email = toCleanString(options && options.email);
    const name = toCleanString(options && options.name);
    const workerUrl = getWorkerUrl();
    const tags = Array.isArray(options && options.tags)
      ? options.tags.map(toCleanString).filter(Boolean)
      : [];
    const extraFields = options && typeof options.extraFields === 'object' && options.extraFields
      ? options.extraFields
      : {};

    if (!email || !email.includes('@')) {
      throw new Error('Invalid email');
    }

    if (!workerUrl) {
      throw new Error('Subscribe worker is not configured');
    }

    const response = await fetch(workerUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, tags, fields: extraFields }),
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok || !payload || payload.error || payload.ok === false) {
      const message = payload && payload.error ? payload.error : 'Subscribe worker failed';
      throw new Error(message);
    }

    if (!payload.result || !payload.result.person_id) {
      throw new Error('Unisender did not confirm subscription');
    }

    return payload;
  }

  global.IraSubscribe = { subscribe };
})(window);
