const statusEl = document.querySelector('#status');
const button = document.querySelector('#generate');
const result = document.querySelector('#result');
const hint = document.querySelector('#hint');

async function health() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    statusEl.textContent = data.stable_diffusion
      ? `SD online | IA: ${data.llm_provider}`
      : `SD offline | IA: ${data.llm_provider}`;
  } catch (error) {
    statusEl.textContent = 'backend offline';
  }
}

function formPayload() {
  return {
    topic: document.querySelector('#topic').value.trim(),
    audience: document.querySelector('#audience').value.trim() || 'publico geral',
    tone: document.querySelector('#tone').value.trim() || 'direto, util e provocativo',
    brand_name: document.querySelector('#brand').value.trim(),
    style_hint: document.querySelector('#style').value.trim(),
  };
}

function renderCards(data) {
  const palette = data.palette.map(color => `<span class="swatch" style="background:${color}"></span>`).join('');
  result.innerHTML = `
    <h2>${data.title}</h2>
    <p class="hint">Job: ${data.job_id}</p>
    <div class="palette">${palette}</div>
    <div class="cards">
      ${data.cards.map(card => `
        <article class="card">
          <img src="${card.url}" alt="Card ${card.index}: ${card.headline}" loading="lazy" />
          <a href="${card.url}" target="_blank" rel="noreferrer">Abrir card ${card.index}</a>
        </article>
      `).join('')}
    </div>
  `;
}

button.addEventListener('click', async () => {
  const payload = formPayload();
  if (!payload.topic) {
    result.innerHTML = '<p class="error">Digite um tema primeiro.</p>';
    return;
  }

  button.disabled = true;
  button.textContent = 'Gerando...';
  hint.textContent = 'Gerando roteiro, fundos no Stable Diffusion e texto final. Segura o rojão.';
  result.innerHTML = '';

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Erro ao gerar carrossel');
    }

    renderCards(data);
    hint.textContent = 'Pronto. Abra cada card para salvar no celular.';
  } catch (error) {
    result.innerHTML = `<p class="error">${error.message}</p>`;
    hint.textContent = 'Deu ruim. Confira se o Stable Diffusion esta aberto com --api e se o .env esta correto.';
  } finally {
    button.disabled = false;
    button.textContent = 'Gerar 5 imagens';
  }
});

health();
setInterval(health, 15000);
