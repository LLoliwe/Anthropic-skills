const el = document.querySelector<HTMLElement>('#app');
if (!el) throw new Error('Expected app root');
el.innerHTML = '<h1>Pryntor Void Pilot</h1><p id="status" role="status">Checking local API…</p>';
fetch('/api/health')
  .then((response) => {
    if (!response.ok) throw new Error('API returned ' + response.status);
    return response.json();
  })
  .then((result: { ok: boolean; service: string }) => {
    const status = document.querySelector('#status');
    if (status) status.textContent = result.ok ? result.service + ' · local OK' : 'Health check failed';
  })
  .catch(() => {
    const status = document.querySelector('#status');
    if (status) status.textContent = 'Local API unavailable';
  });
