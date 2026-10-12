const RAW = 'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main';

export const STATUS_API_BASE =
  process.env.EXPO_PUBLIC_STATUS_URL || 'http://127.0.0.1:8787';

async function fetchText(path) {
  try {
    const res = await fetch(`${RAW}/${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    return { ok: true, data: text };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

export function fetchRepoReadme() {
  return fetchText('README.md');
}

export function fetchStatusDoc() {
  return fetchText('STATUS.md');
}

export async function fetchLiveBotStatus() {
  try {
    const res = await fetch(`${STATUS_API_BASE}/status`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { ok: true, data: await res.json() };
  } catch (e) {
    return {
      ok: false,
      error: `${String(e)} — is status_server.py running at ${STATUS_API_BASE}?`,
    };
  }
}

export async function fetchSignals(limit = 15) {
  try {
    const res = await fetch(`${STATUS_API_BASE}/signals?limit=${limit}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { ok: true, data: await res.json() };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

export async function fetchTrades() {
  try {
    const res = await fetch(`${STATUS_API_BASE}/trades`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { ok: true, data: await res.json() };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}
