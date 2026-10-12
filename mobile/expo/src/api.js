const RAW = 'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main';

// Point this at your status_server (phone must reach the host).
// Android emulator -> host machine: http://10.0.2.2:8787
// iOS simulator -> http://127.0.0.1:8787
// Physical device -> http://<your-lan-ip>:8787
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
    const res = await fetch(`${STATUS_API_BASE}/status`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { ok: true, data };
  } catch (e) {
    return {
      ok: false,
      error: `${String(e)} — is status_server.py running at ${STATUS_API_BASE}?`,
    };
  }
}
