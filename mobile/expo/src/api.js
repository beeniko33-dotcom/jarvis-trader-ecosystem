export async function fetchRepoReadme() {
  try {
    const url = 'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main/README.md';
    const res = await fetch(url);
    if (!res.ok) throw new Error('Network response not ok');
    const text = await res.text();
    return { ok: true, data: text };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}
