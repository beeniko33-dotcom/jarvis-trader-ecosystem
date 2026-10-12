const RAW = 'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main';

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
