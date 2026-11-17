const scoreColors = ['#d9f0ec', '#a4d8cb', '#65b6a4', '#258779', '#07574c'];
const displayedScore = score => Number(score.toFixed(1));

function scoreBands(values) {
  const sorted = values.filter(Number.isFinite).map(displayedScore).sort((a, b) => a - b);
  if (!sorted.length) return [];
  const upperBounds = [...new Set(scoreColors.map((_, index) =>
    sorted[Math.ceil(sorted.length * (index + 1) / scoreColors.length) - 1]))];
  return upperBounds.map((max, index) => ({
    min: index ? upperBounds[index - 1] : sorted[0],
    max,
    color: scoreColors[upperBounds.length === 1 ? 2 :
      Math.round(index * (scoreColors.length - 1) / (upperBounds.length - 1))]
  }));
}

(() => {
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  const key = 'kredita-tema';
  let selected;
  try {
    selected = localStorage.getItem(key);
  } catch {}
  function applyTheme() {
    const dark = selected === 'escuro' || (selected !== 'claro' && system.matches);
    root.dataset.theme = dark ? 'dark' : 'light';
    document.querySelector('#theme-toggle')?.setAttribute('aria-pressed', String(dark));
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#111922' : '#f5f7fb');
  }
  applyTheme();
  system.addEventListener('change', applyTheme);
  document.addEventListener('click', event => {
    if (!event.target.closest('#theme-toggle')) return;
    selected = root.dataset.theme === 'dark' ? 'claro' : 'escuro';
    try {
      localStorage.setItem(key, selected);
    } catch {}
    applyTheme();
  });
})();

const number = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const count = new Intl.NumberFormat('pt-BR');
const html = value => String(value).replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const formatValue = value => value == null ? '—' : number.format(value);
const deltaNumber = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 2, maximumFractionDigits: 2, signDisplay: 'exceptZero'
});
const signedPoints = value => deltaNumber.format(value) + ' pts';
const monthLabel = value => value.slice(5) + '/' + value.slice(0, 4);
const monthIndex = value => Number(value.slice(0, 4)) * 12 + Number(value.slice(5));

function monthlyHistoryPoints(history) {
  return Object.entries(history ?? {}).sort(([a], [b]) => a.localeCompare(b))
    .map(([date, score]) => ({ date, score }));
}

function historyScale(points) {
  const scores = points.map(point => point.score).filter(Number.isFinite);
  if (!scores.length) return [0, 100];
  const low = Math.min(...scores);
  const high = Math.max(...scores);
  const step = [5, 10, 20, 25].find(size => (high - low) / size <= 4);
  return [Math.max(0, Math.floor((low - step / 2) / step) * step),
    Math.min(100, Math.ceil((high + step / 2) / step) * step)];
}

function timelinePath(vertices, y, monthly) {
  return vertices.map(({ date, score, x }, index) => {
    if (!Number.isFinite(score)) return '';
    const prev = vertices[index - 1];
    const connected = Number.isFinite(prev?.score) &&
      (!monthly || monthIndex(prev.date) + 1 === monthIndex(date));
    return `${connected ? 'L' : 'M'}${x} ${y(score)}`;
  }).join(' ');
}

function timelineFrame(min, max, graphic, controls = '') {
  const ticks = [max, (min + max) / 2, min];
  return `<div class="timeline-frame">
    <div class="timeline-scale" aria-hidden="true">${ticks.map(tick => `<span>${tick.toLocaleString('pt-BR')}</span>`).join('')}</div>
    <div class="timeline-plot">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <path class="chart-gridline" d="M0 0H100 M0 50H100 M0 100H100" />
        ${graphic}
      </svg>
      ${controls}
    </div>
  </div>`;
}

function timelineDates(dates) {
  return `<div class="timeline-dates" aria-hidden="true">${dates.map(({ date, x }) =>
    `<span style="--x:${x}%">${html(monthLabel(date))}</span>`).join('')}</div>`;
}

function historyChart(points, { monthly = false, scale, empty = 'Histórico indisponível para este município.' } = {}) {
  const latest = points.findLast(point => Number.isFinite(point.score));
  if (!latest) return `<p class="empty-result">${empty}</p>`;
  const describe = point => monthLabel(point.date) + (point.editionLabel ? ' · ' + point.editionLabel : '');
  const reading = `<div class="timeline-reading" aria-live="polite">
    <span data-timeline-date>${html(describe(latest))}</span>
    <strong data-timeline-score>${formatValue(latest.score)} <small>pts</small></strong>
  </div>`;
  if (points.length === 1) return `<div class="score-timeline">${reading}
    ${latest.version ? `<p class="subtitle timeline-version">${html(latest.version)}</p>` : ''}</div>`;
  const [min, max] = scale ?? historyScale(points);
  const y = score => 100 * (max - score) / (max - min);
  const first = monthly ? monthIndex(points[0].date) : 0;
  const lastIndex = points.length - 1;
  const span = monthly ? monthIndex(points[lastIndex].date) - first : lastIndex;
  const vertices = points.map((point, index) => ({
    ...point,
    x: span ? 100 * (monthly ? monthIndex(point.date) - first : index) / span : 50
  }));
  const path = timelinePath(vertices, y, monthly);
  const middle = vertices.find(point => point.x >= 40 && point.x <= 60 &&
    point.date !== points[0].date && point.date !== points[lastIndex].date);
  const dates = points[0].date === points[lastIndex].date ? [{ date: points[0].date, x: 50 }] :
    [vertices[0], ...(middle ? [middle] : []), vertices[lastIndex]];

  return `<div class="score-timeline">${reading}
    ${timelineFrame(min, max, `<path class="timeline-line" d="${path}" />`,
      vertices.map((point, index) => !Number.isFinite(point.score) ? '' : `
          <button class="timeline-point" type="button" style="--x:${point.x}%;--y:${y(point.score)}%"
            data-timeline-point data-date="${html(describe(point))}" data-score="${formatValue(point.score)}"
            aria-pressed="${points[index] === latest}"
            aria-label="${html(describe(point))}: ${formatValue(point.score)} pontos"></button>`).join(''))}
    ${timelineDates(dates)}
    <details class="timeline-table"><summary>Ver valores <span>(${count.format(points.length)})</span></summary>
      <div class="ranking-table-wrap" tabindex="0" aria-label="Valores do histórico"><table class="ranking-table">
        <thead><tr><th scope="col">Competência</th><th scope="col">Score</th></tr></thead>
        <tbody>${points.map(point => `<tr><th scope="row">${html(monthLabel(point.date))}
          ${point.editionLabel ? `<small>${html(point.editionLabel + ' · ' + point.version)}</small>` : ''}</th>
          <td>${Number.isFinite(point.score) ? formatValue(point.score) : 'Sem score'}</td></tr>`).join('')}</tbody>
      </table></div>
    </details>
  </div>`;
}

let comparisonHistorySource = 'scr';
const comparisonMonths = {};

function renderComparisonHistory(panel, entries, demonstration) {
  if (entries.some(entry => entry.loading)) {
    panel.insertAdjacentHTML('beforeend', '<p class="empty-result">Carregando históricos…</p>');
    return;
  }
  const datasets = {
    scr: entries.map(entry => entry.simulated),
    publicado: entries.map(entry => entry.published)
  };
  for (const [kind, series] of Object.entries(datasets)) {
    datasets[kind] = series.map(points => new Map(points.map(point => [point.date, point.score])));
  }
  const available = Object.fromEntries(Object.entries(datasets).map(([source, series]) => [
    source, series.some(points => [...points.values()].some(Number.isFinite))
  ]));
  if (!Object.values(available).some(Boolean)) {
    panel.insertAdjacentHTML('beforeend', '<p class="empty-result">Histórico indisponível para os municípios selecionados.</p>');
    return;
  }
  if (!available[comparisonHistorySource]) comparisonHistorySource = available.scr ? 'scr' : 'publicado';
  panel.insertAdjacentHTML('beforeend', `<div class="comparison-history-filters">
      <label class="input-label">Série<select id="comparison-history-source">
        <option value="scr"${available.scr ? '' : ' disabled'}>${demonstration ? 'Histórico de demonstração' : 'Simulação SCR'}</option>
        <option value="publicado"${available.publicado ? '' : ' disabled'}>Edições publicadas</option>
      </select></label>
      <label class="input-label">Competência<select id="comparison-history-month"></select></label>
    </div>
    <p class="subtitle comparison-history-note"></p>
    <div class="score-timeline comparison-timeline"></div>
    <div class="comparison-history-reading" aria-live="polite"></div>`);
  const source = panel.querySelector('#comparison-history-source');
  const month = panel.querySelector('#comparison-history-month');
  const plot = panel.querySelector('.comparison-timeline');
  const reading = panel.querySelector('.comparison-history-reading');
  source.value = comparisonHistorySource;

  function renderSeries() {
    const kind = source.value;
    comparisonHistorySource = kind;
    panel.querySelector('.comparison-history-note').textContent = kind === 'publicado'
      ? 'Última edição publicada de cada competência.'
      : demonstration ? '' : 'Série simulada com variação do SCR.';
    const series = datasets[kind];
    const dates = [...new Set(series.flatMap(values => [...values.keys()]))].sort();
    const latest = dates.findLast(date => series.some(values => Number.isFinite(values.get(date))));
    const start = monthIndex(dates[0]);
    const span = monthIndex(dates.at(-1)) - start;
    const x = date => span ? (monthIndex(date) - start) / span * 100 : 50;
    const [min, max] = historyScale(series.flatMap(values => [...values.values()].map(score => ({ score }))));
    const y = value => (max - value) / (max - min) * 100;
    const middleDate = dates.find(date => x(date) >= 40 && x(date) <= 60);
    const ticks = span ? [dates[0], ...(middleDate ? [middleDate] : []), dates.at(-1)] : dates;
    month.replaceChildren(...dates.map(date => new Option(monthLabel(date), date)));
    month.value = dates.includes(comparisonMonths[kind]) ? comparisonMonths[kind] : latest;
    const lines = series.map((values, index) => {
      const vertices = dates.map(date => ({ date, x: x(date), score: values.get(date) }));
      return `<path class="timeline-line comparison-series-${index}" d="${timelinePath(vertices, y, kind === 'scr')}" />`;
    }).join('');
    const markers = series.map((values, index) => [...values].map(([date, score]) => Number.isFinite(score)
      ? `<span class="comparison-series-point comparison-series-${index}" style="left:${x(date)}%;top:${y(score)}%"></span>`
      : '').join('')).join('');
    plot.innerHTML = timelineFrame(min, max, lines,
      `<span class="comparison-month-guide" aria-hidden="true"></span><div aria-hidden="true">${markers}</div>
      <div class="comparison-month-points" aria-hidden="true"></div>`) +
      timelineDates(ticks.map(date => ({ date, x: x(date) })));

    function renderMonth() {
      const date = month.value;
      comparisonMonths[kind] = date;
      const values = series.map(values => values.get(date));
      plot.querySelector('.comparison-month-guide').style.left = `${x(date)}%`;
      plot.querySelector('.comparison-month-points').innerHTML = values.map((score, index) =>
        Number.isFinite(score) ? `<span class="comparison-selected-point comparison-series-${index}"
          style="left:${x(date)}%;top:${y(score)}%"></span>` : '').join('');
      const differences = values.flatMap((score, i) => values.slice(i + 1).flatMap((other, offset) => {
        if (!Number.isFinite(score) || !Number.isFinite(other)) return [];
        return `<li>${html(entries[i].name)} − ${html(entries[i + offset + 1].name)} <strong>${signedPoints(score - other)}</strong></li>`;
      }));
      reading.innerHTML = `<ul class="comparison-history-values">${values.map((score, index) => `<li>
        <span class="comparison-series-${index}"><i aria-hidden="true"></i> ${html(entries[index].name)}</span>
        <strong>${Number.isFinite(score) ? formatValue(score) + ' pts' : 'Sem score'}</strong>
      </li>`).join('')}</ul>
      <h3>Diferença no mês</h3>
      ${differences.length ? `<ul class="comparison-history-differences">${differences.join('')}</ul>` :
        '<p class="empty-result">São necessários dois scores na competência para calcular a diferença.</p>'}`;
    }

    month.onchange = renderMonth;
    plot.querySelector('.timeline-plot').onclick = event => {
      const box = event.currentTarget.getBoundingClientRect();
      const position = 100 * (event.clientX - box.left) / box.width;
      month.value = dates.reduce((closest, date) => Math.abs(x(date) - position) < Math.abs(x(closest) - position) ? date : closest);
      renderMonth();
    };
    renderMonth();
  }

  source.onchange = renderSeries;
  renderSeries();
}

const page = document.body.dataset.page;
const titles = {
  index: 'Visão geral', ranking: 'Ranking municipal', municipio: 'Município',
  favoritos: 'Favoritos', comparar: 'Comparar municípios', guia: 'Guia do site', metodologia: 'Metodologia e fontes',
  apostas: 'Apostas'
};
const axisLabels = ['Risco', 'Capacidade', 'Inclusão', 'Demografia'];
const allAxes = axisLabels.map((_, index) => index);
const axisStorageKey = 'kredita-eixos';
let activeAxes = readActiveAxes();
const metricLabels = ['Score geral', ...axisLabels];
const normalize = value => value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
const $ = selector => document.querySelector(selector);
const identity = item => html(item.nome + ' · ' + item.uf);
const defaultId = new URLSearchParams(location.search).get('id');
let selectedId = page === 'index' ? defaultId : null;
let municipalities = new Map();
let catalog = new Map();
let scores = [];
let edition;
let rankingPage = 1;
const historyCache = new Map();
let comparison = readSaved('kredita-comparacao').slice(0, 3);
let favorites = readSaved('kredita-favoritos');
let map;
let focusMapOnLoad = false;
let latestNotice = 0;

function readSaved(key) {
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    return Array.isArray(saved) ? [...new Set(saved.filter(id => typeof id === 'string' && /^\d{7}$/.test(id)))] : [];
  } catch {
    return [];
  }
}

function readActiveAxes() {
  try {
    const saved = JSON.parse(localStorage.getItem(axisStorageKey));
    const selected = allAxes.filter(index => Array.isArray(saved) && saved.includes(index));
    if (selected.length) return selected;
  } catch {}
  return [...allAxes];
}

function scopedScore(score, axes) {
  if (activeAxes.length === allAxes.length) return score ?? null;
  if (score == null || !activeAxes.every(index => Number.isFinite(axes?.[index]))) return null;
  return activeAxes.reduce((sum, index) => sum + axes[index], 0) / activeAxes.length;
}

function updateScoreScope() {
  const partial = activeAxes.length !== allAxes.length;
  metricLabels[0] = partial ? 'Score dos eixos selecionados' : 'Score geral';
  scores = [];
  for (const item of catalog.values()) {
    const score = scopedScore(item.score, item.eixos);
    if (score !== null) scores.push({ ...item, score });
  }
  scores.sort((a, b) => (partial ? b.score - a.score : 0) || a.position - b.position || a.id.localeCompare(b.id));
  if (partial) scores.forEach((item, index) => { item.position = index + 1; });
  municipalities = new Map(scores.map(item => [item.id, item]));
}

function setScoreAxes(selection) {
  activeAxes = selection;
  try {
    localStorage.setItem(axisStorageKey, JSON.stringify(activeAxes));
  } catch {
    notify('O navegador impediu salvar a seleção de eixos entre páginas.');
  }
  updateScoreScope();
  updateAxisControls();
}

function nav(key, icon) {
  const current = page === key ? ' active' : '';
  return `<a class="nav-link${current}" href="${key}.html"${current ? ' aria-current="page"' : ''}>
    <span class="nav-icon" aria-hidden="true">${icon}</span>${titles[key]}</a>`;
}

$('#app').innerHTML = `
  <div class="app-shell">
    <aside class="sidebar" id="sidebar" aria-label="Menu principal">
      <a class="brand" href="index.html">
        <span class="brand-mark"><img src="logo.png" alt=""></span>
        <span class="brand-name">KREDITA<small>INTELIGÊNCIA TERRITORIAL</small></span>
      </a>
      <nav class="side-nav" aria-label="Painel">
        ${nav('index', '⌂')}${nav('ranking', '≡')}${nav('favoritos', '☆')}${nav('comparar', '⇄')}
      </nav>
      <div class="menu-caption second-caption">EXPLORAR</div>
      <nav class="side-nav" aria-label="Explorar">
        ${nav('guia', '?')}${nav('metodologia', '▤')}${nav('apostas', '◉')}
      </nav>
      <div class="sidebar-bottom"><span class="status-dot"></span>
        <div><strong>Ambiente de análise</strong><small>Dados municipais</small></div>
      </div>
    </aside>
    <button class="menu-shade" type="button" aria-label="Fechar menu" tabindex="-1" hidden></button>
    <div class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <button class="hamburger" type="button" aria-label="Menu principal" aria-controls="sidebar" aria-expanded="false"><span></span><span></span><span></span></button>
          <div class="breadcrumb"><strong>${titles[page]}</strong></div>
        </div>
        <div class="topbar-actions">
          <button id="theme-toggle" class="button button-outline" type="button" aria-label="Modo escuro" aria-pressed="false" title="Alternar tema">
            <span class="theme-moon" aria-hidden="true">☾</span><span class="theme-sun" aria-hidden="true">☀</span>
          </button>
          ${['index', 'ranking', 'municipio', 'favoritos', 'comparar'].includes(page) ? `
          <details class="axis-scope">
            <summary class="button button-outline">Eixos do score <span id="axis-active"></span></summary>
            <form id="axis-form" class="filter-popover">
              <fieldset><legend>Incluir no score e no ranking</legend>
                ${axisLabels.map((label, index) => `<label><input type="checkbox" name="axis" value="${index}"${activeAxes.includes(index) ? ' checked' : ''}> ${label}</label>`).join('')}
              </fieldset>
              <div class="actions"><button class="button button-primary" type="submit">Aplicar eixos</button>
                <button class="button button-quiet" type="button" id="axis-reset">Usar todos</button></div>
              <p id="axis-feedback" role="status"></p>
            </form>
          </details>` : ''}
          <button class="button button-outline" type="button" id="refresh"><span aria-hidden="true">↻</span> Atualizar dados</button>
          <button class="button button-primary" type="button" id="compare-open" aria-label="Adicionar município à comparação"><span aria-hidden="true">＋</span><span id="compare-count">0</span></button>
        </div>
      </header>
      <p class="preview-banner" id="preview-banner" hidden>Modo demonstração · Scores e históricos fictícios</p>
      <main class="content" id="main"></main>
      <footer class="page-footer"><span>© KREDITA · Score territorial</span><span>Metodologia KREDITA</span></footer>
    </div>
  </div>
  <dialog id="compare-dialog" aria-labelledby="dialog-title">
    <div class="dialog-heading"><h2 id="dialog-title">Adicionar à comparação</h2>
      <form method="dialog"><button class="icon-btn" aria-label="Fechar">×</button></form></div>
    <div id="dialog-picker"></div>
    <p id="dialog-status" class="dialog-status" aria-live="polite"></p>
    <a class="button button-outline" href="comparar.html">Abrir comparação →</a>
  </dialog>
  <div class="toast" role="status" aria-live="polite"></div>`;
$('#theme-toggle')?.setAttribute('aria-pressed', String(document.documentElement.dataset.theme === 'dark'));

if ($('#axis-form')) {
  const control = $('.axis-scope');
  const close = () => {
    control.open = false;
    control.querySelector('summary').focus();
  };
  control.addEventListener('keydown', event => {
    if (event.key === 'Escape' && control.open) close();
  });
  document.addEventListener('click', event => {
    if (control.open && !control.contains(event.target)) control.open = false;
  });
  control.addEventListener('toggle', () => {
    if (!control.open) updateAxisControls();
  });
  const applyAxes = async selection => {
    setScoreAxes(selection);
    close();
    rankingPage = 1;
    if (page === 'index') {
      updateSelection();
      renderDashboard();
    }
    if (page === 'ranking') renderRanking();
    if (page === 'favoritos') renderFavorites();
    if (page === 'comparar') renderComparison();
    if (page === 'municipio' && edition) {
      try { await renderDetails(); }
      catch { notify('Não foi possível atualizar os detalhes do município.'); }
    }
    dialogPicker.render();
  };
  $('#axis-form').onsubmit = event => {
    event.preventDefault();
    const selection = allAxes.filter(index => $('#axis-form input[value="' + index + '"]').checked);
    if (!selection.length) {
      $('#axis-feedback').textContent = 'Selecione pelo menos um eixo.';
      return;
    }
    applyAxes(selection);
  };
  $('#axis-reset').onclick = () => applyAxes([...allAxes]);
  updateAxisControls();
}

function updateAxisControls() {
  if ($('#axis-form')) {
    const summary = $('#axis-active');
    summary.textContent = activeAxes.length === allAxes.length ? 'Todos' : `${activeAxes.length}/${allAxes.length}`;
    summary.title = activeAxes.map(index => axisLabels[index]).join(' · ');
    $('#axis-feedback').textContent = '';
    for (const input of $('#axis-form').elements.namedItem('axis')) input.checked = activeAxes.includes(Number(input.value));
  }
  const metric = $('#dashboard-metric');
  if (metric) {
    for (const option of metric.options) option.disabled = Number(option.value) > 0 &&
      !activeAxes.includes(Number(option.value) - 1);
    if (metric.selectedOptions[0]?.disabled) metric.value = '0';
    metric.options[0].text = metricLabels[0];
  }
}

const mobileMenu = matchMedia('(max-width: 760px)');
let menuOpen = !mobileMenu.matches;
function setMenu(open) {
  menuOpen = open;
  $('.app-shell').classList.toggle('sidebar-collapsed', !open);
  $('.hamburger').setAttribute('aria-expanded', open);
  $('#sidebar').inert = !open;
  $('.menu-shade').hidden = !open || !mobileMenu.matches;
}
setMenu(menuOpen);
mobileMenu.addEventListener('change', event => setMenu(!event.matches));
$('.hamburger').onclick = () => setMenu(!menuOpen);
$('.menu-shade').onclick = () => setMenu(false);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobileMenu.matches && menuOpen && !$('#compare-dialog').open) {
    setMenu(false);
    $('.hamburger').focus();
  }
});

function notify(message) {
  const toast = $('.toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(latestNotice);
  latestNotice = setTimeout(() => toast.classList.remove('show'), 3800);
}

function details(item, withLabel = false) {
  return `<a class="${withLabel ? 'button button-primary' : 'row-action'}" href="municipio.html?id=${encodeURIComponent(item.id)}"
    aria-label="Ver detalhes de ${html(item.nome)}" title="Ver detalhes">${withLabel ? 'Ver detalhes' : '→'}</a>`;
}

function plus(item, withLabel = false) {
  return `<button class="${withLabel ? 'button button-outline' : 'row-action'}" data-add="${html(item.id)}" type="button"
    aria-label="Adicionar ${html(item.nome)} à comparação" title="Adicionar à comparação">${withLabel ? 'Comparar' : '+'}</button>`;
}

function favoriteButton(item, withLabel = false) {
  return `<button class="${withLabel ? 'button button-outline' : 'row-action'}" type="button"
    data-favorite="${html(item.id)}" data-name="${html(item.nome)}"${withLabel ? ' data-label' : ''}>
    ${favoriteButtonText(item.id, withLabel)}</button>`;
}

function favoriteButtonText(id, withLabel) {
  const saved = favorites.includes(id);
  return withLabel ? (saved ? 'Remover dos favoritos' : 'Salvar nos favoritos') : (saved ? '★' : '☆');
}

function syncFavoriteButtons() {
  for (const button of document.querySelectorAll('[data-favorite]')) {
    const saved = favorites.includes(button.dataset.favorite);
    button.textContent = favoriteButtonText(button.dataset.favorite, button.hasAttribute('data-label'));
    button.setAttribute('aria-pressed', saved);
    button.setAttribute('aria-label', 'Favoritar ' + button.dataset.name);
    button.title = (saved ? 'Remover dos favoritos' : 'Salvar nos favoritos');
  }
}

function toggleFavorite(id) {
  const saved = favorites.includes(id);
  const next = saved ? favorites.filter(code => code !== id) : [...favorites, id];
  try {
    localStorage.setItem('kredita-favoritos', JSON.stringify(next));
  } catch {
    notify('O navegador impediu salvar os favoritos.');
    return;
  }
  favorites = next;
  if (page === 'favoritos') {
    renderFavorites();
    ($('#main [data-favorite]') || $('#favorites-ranking')).focus();
  } else syncFavoriteButtons();
  notify(saved ? 'Município removido dos favoritos.' : 'Município salvo nos favoritos.');
}

function setComparison(next, message) {
  comparison = next;
  try {
    localStorage.setItem('kredita-comparacao', JSON.stringify(comparison));
  } catch {
    message += ' O navegador impede salvar a seleção após recarregar.';
  }
  $('#compare-count').textContent = comparison.length;
  if (page === 'comparar') renderComparison();
  compareNotice(message);
}

function compareNotice(message) {
  if ($('#compare-dialog').open) $('#dialog-status').textContent = message;
  else notify(message);
}

document.addEventListener('click', event => {
  const favorite = event.target.closest('[data-favorite]');
  if (favorite) toggleFavorite(favorite.dataset.favorite);
  const add = event.target.closest('[data-add]');
  const remove = event.target.closest('[data-remove]');
  if (remove) {
    setComparison(comparison.filter(id => id !== remove.dataset.remove), 'Município removido.');
    ($('#main [data-remove]') || $('#page-compare-open')).focus();
  }
  if (!add) return;
  const item = municipalities.get(add.dataset.add);
  if (!item) return;
  if (comparison.includes(item.id)) return compareNotice('Este município já está na comparação.');
  if (comparison.length === 3) return compareNotice('Remova um município para adicionar outro.');
  setComparison([...comparison, item.id], item.nome + ' entrou na comparação.');
});

function matches(item, query) {
  return normalize(item.nome + ' ' + item.uf).includes(query) || item.id === query;
}

function picker(container, scope, accept) {
  container.innerHTML = `<label class="input-label">Buscar município
      <input type="search" placeholder="Digite o nome ou código IBGE" autocomplete="off"></label>
    <ul class="suggestions" aria-label="Sugestões de municípios"></ul>
    <p class="search-count sr-only" role="status"></p>`;
  const input = container.querySelector('input');
  const list = container.querySelector('ul');

  function render() {
    const query = normalize(input.value);
    const options = query ? [...scope()].filter(item => matches(item, query)).sort((a, b) => {
      const priority = item => item.id === query || normalize(item.nome) === query ? 0 :
        normalize(item.nome).startsWith(query) ? 1 : 2;
      return priority(a) - priority(b) || a.nome.localeCompare(b.nome, 'pt-BR');
    }).slice(0, 8) : [];
    list.innerHTML = options.map(item => `<li>
      ${accept ? `<button type="button" class="suggestion-name" data-pick="${html(item.id)}">${identity(item)}</button>`
        : `<span class="suggestion-name">${identity(item)}</span>`}
      ${details(item)}${municipalities.has(item.id) ? plus(item) : ''}</li>`).join('');
    if (query && !options.length) list.innerHTML = '<li class="empty-result">Nenhum município encontrado.</li>';
    container.querySelector('.search-count').textContent = query ? options.length + ' sugestões.' : '';
  }

  function choose(id) {
    accept(id);
    input.value = '';
    render();
    input.focus();
  }
  input.addEventListener('input', render);
  input.addEventListener('keydown', event => {
    const option = list.querySelector('[data-pick]');
    if (event.key === 'Enter' && option) choose(option.dataset.pick);
  });
  list.addEventListener('click', event => {
    const option = event.target.closest('[data-pick]');
    if (option) choose(option.dataset.pick);
  });
  return { input, render };
}

const dialogPicker = picker($('#dialog-picker'), () => scores);
function openCompare() {
  dialogPicker.input.value = '';
  dialogPicker.render();
  $('#dialog-status').textContent = '';
  $('#compare-dialog').showModal();
  dialogPicker.input.focus();
}
$('#compare-open').onclick = openCompare;
$('#compare-count').textContent = comparison.length;

function heading(title, subtitle) {
  return `<div class="welcome-row"><div><h1>${title}<span class="accent-dot">.</span></h1>
    <p class="subtitle">${subtitle}</p></div></div>`;
}

function dashboardMetric(label, id, symbol, foot, primary = false) {
  return `<article class="metric-card dashboard-metric${primary ? ' primary-metric' : ''}">
    <div class="metric-top"><span id="${id}-label">${label}</span><span class="metric-icon" aria-hidden="true">${symbol}</span></div>
    <div class="metric-value" id="${id}">—</div><div class="metric-note">${foot}</div></article>`;
}

function dashboardScope() {
  const uf = $('#dashboard-uf').value;
  const size = $('#dashboard-size').value;
  const metric = Number($('#dashboard-metric').value);
  const value = item => metric === 0 ? item.score : item.eixos[metric - 1];
  const items = scores.filter(item => {
    return (!uf || item.uf === uf) && (!size || size === populationGroup(item));
  }).sort((a, b) => value(b) - value(a) || a.position - b.position);
  return { items, value, metric };
}

function populationGroup(item) {
  if (item.populacao == null) return '';
  if (item.populacao <= 20000) return 'small';
  return item.populacao <= 100000 ? 'medium' : 'large';
}

function renderDashboard() {
  const { items, value, metric } = dashboardScope();
  const label = metricLabels[metric];
  const size = $('#dashboard-size');
  const state = $('#dashboard-uf').value;
  renderBetsCard(state);
  $('#active-filters').textContent = [state, size.value ? size.selectedOptions[0].text : '', metric ? label : '']
    .filter(Boolean).join(' · ');
  const mean = items.reduce((sum, item) => sum + value(item), 0) / items.length;
  $('#dashboard-mean-label').textContent = metric ? 'Média no eixo ' + label :
    activeAxes.length === allAxes.length ? 'Score médio do recorte' : 'Score médio dos eixos selecionados';
  $('#dashboard-mean').innerHTML = items.length ? number.format(mean) + ' <small>/ 100</small>' : '—';
  $('#dashboard-count').textContent = count.format(items.length);
  $('#dashboard-export').disabled = items.length === 0;
  $('#preview-metric').textContent = label;
  $('#preview-body').innerHTML = items.length ? items.slice(0, 5).map(item => `<tr>
    <th scope="row">${identity(item)}</th><td>${number.format(value(item))}</td>
    <td><div class="actions">${details(item)}${plus(item)}${favoriteButton(item)}</div></td></tr>`).join('') :
    '<tr><td colspan="3">Nenhum município corresponde aos filtros.</td></tr>';
  const bands = scoreBands(scores.map(value));
  $('#map-legend').innerHTML = bands.map(({min, max, color}, index) => {
    const range = index ? 'Acima de ' + number.format(min) + ' até ' + number.format(max) :
      min === max ? number.format(max) : number.format(min) + '–' + number.format(max);
    return `<li><span style="--swatch:${color}"></span>${range}</li>`;
  }).join('') + '<li><span style="--swatch:var(--map-unrated)"></span>Fora do recorte ou sem dados</li>';
  $('#map-scale-title').textContent = label;
  map?.updateScores(new Map(items.map(item => [item.id, value(item)])), bands);
  renderDashboardCharts(items);
  syncFavoriteButtons();
}

function renderDashboardCharts(items) {
  const panel = $('#dashboard-charts');
  const municipality = municipalities.get(selectedId);
  const place = catalog.get(selectedId);
  if (selectedId) {
    panel.innerHTML = municipality
      ? charts(municipality, identity(municipality))
      : `<section class="panel chart-panel"><h2>Gráficos de ${place ? identity(place) : 'município selecionado'}</h2>
        <p class="empty-result">Score indisponível.</p></section>`;
    return;
  }
  if (!items.length) {
    panel.innerHTML = '<section class="panel chart-panel"><h2>Gráficos do recorte</h2><p class="empty-result">Nenhum município corresponde aos filtros.</p></section>';
    return;
  }
  const monthly = new Map();
  for (const item of items) {
    for (const [date, score] of Object.entries(scopedHistory(item))) {
      if (score === null) continue;
      const month = monthly.get(date) || { sum: 0, count: 0 };
      month.sum += score;
      month.count++;
      monthly.set(date, month);
    }
  }
  const average = {
    eixos: axisLabels.map((_, index) => items.reduce((sum, item) => sum + item.eixos[index], 0) / items.length),
    historico: Object.fromEntries([...monthly].map(([date, month]) => [date, month.sum / month.count]))
  };
  panel.innerHTML = `
    <section class="panel chart-panel"><h2>Média por eixo</h2><p class="subtitle chart-context">Municípios do recorte</p>${axisChart(average)}</section>
    <section class="panel chart-panel"><h2>${edition?.demonstracao ? 'Histórico do score médio' : 'Simulação SCR do score médio'}</h2>
      <p class="subtitle chart-context">Média dos municípios do recorte com dados nos eixos ativos em cada mês.</p>
      ${historyChart(monthlyHistoryPoints(average.historico), { monthly: true, empty: 'Histórico indisponível no recorte.' })}</section>`;
}

function municipalitiesInState() {
  const state = $('#dashboard-uf').value;
  return state ? [...catalog.values()].filter(item => item.uf === state) : [];
}

function renderMapLocator() {
  const locator = $('#map-locator');
  const places = municipalitiesInState().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  locator.replaceChildren(new Option(places.length ? 'Escolha um município' : 'Escolha a UF nos filtros', ''),
    ...places.map(item => new Option(item.nome, item.id)));
  locator.disabled = !places.length;
}

function focusMapState() {
  map?.focusArea(municipalitiesInState().map(item => item.id));
}

function exportDashboard() {
  const { items, value, metric } = dashboardScope();
  const fields = ['Código IBGE', 'Município', 'UF', 'População', 'Posição nacional', metricLabels[metric], 'Eixos do score'];
  const axes = activeAxes.map(index => axisLabels[index]).join(' / ');
  const rows = items.map(item => [item.id, item.nome, item.uf, item.populacao, item.position, number.format(value(item)), axes]);
  downloadCsv('kredita-ranking.csv', fields, rows);
}

function downloadCsv(filename, fields, rows) {
  const csv = [fields, ...rows].map(row => row.map(field => '"' + String(field ?? '').replaceAll('"', '""') + '"').join(';')).join('\r\n');
  const url = URL.createObjectURL(new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' }));
  const link = Object.assign(document.createElement('a'), { href: url, download: filename });
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function exportMunicipalities(ids, filename) {
  const fields = ['Código IBGE', 'Município', 'UF', 'População', 'Posição', metricLabels[0], ...activeAxes.map(index => axisLabels[index])];
  const decimal = value => value == null ? '' : number.format(value);
  const rows = ids.map(id => {
    const item = catalog.get(id);
    const ranked = municipalities.get(id);
    return [id, item?.nome, item?.uf, item?.populacao, ranked?.position, decimal(ranked?.score),
      ...activeAxes.map(index => decimal(item?.eixos?.[index]))];
  });
  downloadCsv(filename, fields, rows);
}

function updateSelection() {
  const item = municipalities.get(selectedId);
  const place = catalog.get(selectedId);
  $('.current-selection').hidden = !selectedId;
  $('#current-municipality').textContent = place ? place.nome + ' · ' + place.uf :
    selectedId ? 'Município ' + selectedId : 'Nenhum município selecionado';
  $('#current-score').innerHTML = item ? number.format(item.score) + ' <small>/ 100</small>' :
    selectedId ? 'Score indisponível' : '—';
  const locator = $('#map-locator');
  locator.value = [...locator.options].some(option => option.value === selectedId) ? selectedId : '';
  $('#selection').innerHTML = selectedId ? `<div>
    <strong>${place ? identity(place) : 'Município ' + html(selectedId)}</strong>
    <p>${item ? 'Score ' + number.format(item.score) + ' / 100 · ' + item.position + 'º no ranking nacional' : 'Score indisponível'}</p></div>
    <div class="actions">${details(place || { id: selectedId, nome: selectedId }, true)}
    ${item ? plus(item, true) : ''}${place ? favoriteButton(place, true) : ''}
    <button class="button button-quiet" type="button" id="clear-selection">Limpar seleção</button></div>` :
    '<p>Escolha um município na lista ou clique no mapa.</p>';
  if ($('#clear-selection')) $('#clear-selection').onclick = () => {
    selectMunicipality(null);
    focusMapState();
    ($('#map-locator').disabled ? $('#dashboard-uf') : $('#map-locator')).focus();
  };
  renderDashboardCharts(dashboardScope().items);
  syncFavoriteButtons();
}

function selectMunicipality(id, focus = false) {
  const state = catalog.get(id)?.uf;
  const stateFilter = $('#dashboard-uf');
  const stateChanged = state && state !== stateFilter.value;
  if (stateChanged) {
    stateFilter.value = state;
    renderMapLocator();
  }
  selectedId = id;
  const url = new URL(location.href);
  if (id) url.searchParams.set('id', id);
  else url.searchParams.delete('id');
  history.replaceState(null, '', url);
  if (!map) focusMapOnLoad = focus;
  map?.highlight(id, focus || Boolean(stateChanged));
  updateSelection();
  if (stateChanged) renderDashboard();
}

function applyStateFilter() {
  renderMapLocator();
  selectMunicipality(null);
  focusMapState();
  renderDashboard();
}

let overviewPicker;
if (page === 'index') {
  $('#main').innerHTML = heading('Panorama territorial', 'Explore os municípios por estado, porte populacional e eixo de análise.') + `
    <section class="panel dashboard-filters" aria-label="Busca e filtros do dashboard">
      <div id="overview-picker"></div>
      <label class="input-label">Estado (UF)<select id="dashboard-uf"><option value="">Todos os estados</option></select></label>
      <div id="axis-slot"></div>
      <details class="dashboard-extra-filters">
        <summary class="button button-outline">Mais filtros</summary>
        <div class="dashboard-extra-fields filter-popover">
          <label class="input-label">População<select id="dashboard-size"><option value="">Todos os portes</option>
            <option value="small">Até 20 mil</option><option value="medium">Mais de 20 mil até 100 mil</option>
            <option value="large">Acima de 100 mil</option></select></label>
          <label class="input-label">Visualizar por<select id="dashboard-metric">
            ${metricLabels.map((label, i) => `<option value="${i}">${label}</option>`).join('')}</select></label>
        </div>
      </details>
      <button type="button" id="dashboard-clear" class="button button-quiet">Limpar filtros</button>
      <p id="active-filters" class="subtitle" aria-live="polite"></p>
    </section>
    <section class="panel current-selection" aria-label="Município e score selecionados" aria-live="polite" hidden>
      <div><span class="metric-top">Município selecionado</span><strong id="current-municipality"></strong></div>
      <div><span class="metric-top">Score do município</span><strong id="current-score"></strong></div>
    </section>
    <section class="metric-grid selection-metrics" aria-label="Resumo do recorte" aria-live="polite">
      ${dashboardMetric('Score médio do recorte', 'dashboard-mean', '↗', 'Pontuação média', true)}
      ${dashboardMetric('Municípios no recorte', 'dashboard-count', '⌖', 'Municípios com score')}
      <article class="metric-card dashboard-metric bets-card" id="bets-card" hidden></article>
    </section>
    <div class="dashboard-grid">
    <section class="panel map-panel" aria-labelledby="map-title">
      <div class="panel-heading"><div><h2 id="map-title">Mapa municipal</h2>
      <p>O filtro de UF aproxima o mapa e define a lista de municípios.</p></div></div>
      <div class="map-locator">
        <label class="input-label">Município no mapa<select id="map-locator" disabled>
          <option value="">Escolha a UF nos filtros</option></select></label>
      </div>
      <div id="selection" class="map-selection" aria-live="polite"></div>
      <div id="municipal-map" class="municipal-map">
        <p id="map-load" role="status">Carregando mapa…</p>
        <div class="map-controls">
          <button class="row-action" type="button" data-zoom-in aria-label="Ampliar mapa" disabled>+</button>
          <button class="row-action" type="button" data-zoom-out aria-label="Reduzir mapa" disabled>−</button>
          <button class="row-action" type="button" data-map-reset aria-label="Mostrar todo o Brasil" disabled>⌂</button>
        </div>
        <div class="map-key"><strong id="map-scale-title">Score geral</strong>
          <ul id="map-legend" aria-label="Faixas da escala"></ul></div>
      </div>
      <p class="map-credit">Faixas por quintis nacionais da métrica selecionada. Limites do IBGE.</p>
    </section>
    <div class="bottom-grid dashboard-charts" id="dashboard-charts" aria-label="Gráficos do dashboard"></div>
    <section class="panel dashboard-preview" aria-labelledby="preview-title">
      <div class="panel-heading"><div><h2 id="preview-title">Prévia do ranking</h2><p>Até cinco municípios do recorte.</p></div></div>
      <div class="ranking-table-wrap" tabindex="0" aria-label="Prévia do ranking">
        <table class="ranking-table"><thead><tr><th>Município</th><th id="preview-metric">Score geral</th><th>Ações</th></tr></thead>
        <tbody id="preview-body"></tbody></table>
      </div>
      <div class="preview-actions"><a class="button button-primary" href="ranking.html">Ver ranking completo →</a>
        <button type="button" class="button button-outline" id="dashboard-export" disabled>Exportar CSV</button></div>
    </section></div>`;
  $('#axis-slot').replaceWith($('.axis-scope'));
  overviewPicker = picker($('#overview-picker'), () => catalog.values(), id => {
    selectMunicipality(id, true);
    requestAnimationFrame(() => $('#map-title').scrollIntoView({ block: 'start' }));
  });
  $('#map-locator').onchange = event => {
    const id = event.target.value;
    selectMunicipality(id || null, Boolean(id));
    if (!id) focusMapState();
  };
  $('.dashboard-filters').onchange = event => {
    if (event.target.name === 'axis') return;
    if (event.target.id === 'dashboard-uf') applyStateFilter();
    else renderDashboard();
  };
  $('#dashboard-clear').onclick = () => {
    $('#dashboard-uf').value = '';
    $('#dashboard-size').value = '';
    $('#dashboard-metric').value = '0';
    applyStateFilter();
  };
  $('#dashboard-export').onclick = exportDashboard;
  updateSelection();
  import('./mapa.js').then(({ createMap }) => createMap($('#municipal-map'), selectMunicipality)).then(controller => {
    map = controller;
    $('#map-load').remove();
    document.querySelectorAll('.map-controls button').forEach(button => { button.disabled = false; });
    renderDashboard();
    if (!selectedId && $('#dashboard-uf').value) focusMapState();
    map.highlight(selectedId, focusMapOnLoad || Boolean(defaultId && selectedId === defaultId));
  }).catch(() => { $('#map-load').textContent = 'Mapa indisponível. Você ainda pode usar a busca.'; });
}

const rankingFilterIds = ['ranking-search', 'uf', 'ranking-size', 'ranking-order'];
const rankingParams = ['busca', 'uf', 'porte', 'ordem'];
const rankingPresetKey = 'kredita-recorte-ranking';
let rankingMinimums = allAxes.map(() => null);
let sharedRankingUF = null;

function readRankingLink() {
  const params = new URLSearchParams(location.search);
  if (params.get('recorte') !== '1') return null;
  const axes = params.get('eixos')?.split(',') ?? [];
  return {
    filters: rankingParams.map(key => params.get(key) ?? ''),
    axes: allAxes.filter(index => axes.includes(String(index + 1))),
    minimums: allAxes.map(index => {
      const value = params.get(`min${index + 1}`);
      const minimum = value?.trim() ? Number(value) : NaN;
      return Number.isFinite(minimum) && minimum >= 0 && minimum <= 100 ? minimum : null;
    })
  };
}

function readRankingPreset() {
  try {
    const preset = JSON.parse(localStorage.getItem(rankingPresetKey));
    if (Array.isArray(preset?.filters) && preset.filters.length === rankingFilterIds.length &&
      preset.filters.every(value => typeof value === 'string') &&
      Array.isArray(preset.minimums) && preset.minimums.length === allAxes.length &&
      preset.minimums.every(value => value === null || (Number.isFinite(value) && value >= 0 && value <= 100)) &&
      Array.isArray(preset.axes) && allAxes.some(index => preset.axes.includes(index))) return preset;
  } catch {}
  return null;
}

function renderRanking() {
  const state = $('#uf').value;
  const size = $('#ranking-size').value;
  const query = normalize($('#ranking-search').value);
  const order = $('#ranking-order').value;
  const results = scores.filter(item => (!state || state === item.uf) &&
    (!size || size === populationGroup(item)) && matches(item, query) &&
    rankingMinimums.every((minimum, index) => minimum === null ||
      (Number.isFinite(item.eixos?.[index]) && item.eixos[index] >= minimum)));
  if (order === 'name') results.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR') || a.position - b.position);
  if (order === 'population') results.sort((a, b) => (b.populacao ?? -1) - (a.populacao ?? -1) || a.position - b.position);
  if (order === 'score-asc') results.sort((a, b) => a.score - b.score || a.position - b.position);
  const limit = 50;
  const pages = Math.max(1, Math.ceil(results.length / limit));
  rankingPage = Math.min(rankingPage, pages);
  const current = results.slice((rankingPage - 1) * limit, rankingPage * limit);
  $('#ranking-count').textContent = count.format(results.length) + (results.length === 1 ? ' município' : ' municípios');
  $('#ranking-page').textContent = `${rankingPage} / ${pages}`;
  $('#ranking-score-label').textContent = metricLabels[0];
  $('#ranking-prev').disabled = rankingPage === 1;
  $('#ranking-next').disabled = rankingPage === pages;
  $('#ranking-body').innerHTML = current.length ? current.map(item => `<tr>
    <td>${item.position}º</td><th scope="row">${identity(item)}</th>
    <td>${item.populacao == null ? '—' : count.format(item.populacao)}</td>
    <td>${number.format(item.score)}</td><td><div class="actions">${details(item)}${plus(item)}${favoriteButton(item)}</div></td>
  </tr>`).join('') : '<tr><td colspan="5">Nenhum município encontrado neste recorte.</td></tr>';
  syncFavoriteButtons();
}

if (page === 'ranking') {
  $('#main').innerHTML = heading(titles.ranking, 'Encontre municípios e ajuste a ordem dos resultados.') + `
    <section class="panel ranking-panel" aria-label="Ranking municipal">
      <div class="rank-filters"><label class="input-label">Buscar município
      <input type="search" id="ranking-search" placeholder="Digite o nome ou código IBGE"></label>
      <label class="input-label">UF<select id="uf"><option value="">Todas as UFs</option></select></label>
      <label class="input-label">População<select id="ranking-size"><option value="">Todos os portes</option>
        <option value="small">Até 20 mil</option><option value="medium">Mais de 20 mil até 100 mil</option>
        <option value="large">Acima de 100 mil</option></select></label>
      <label class="input-label">Ordenar por<select id="ranking-order">
        <option value="">Maior score</option><option value="score-asc">Menor score</option>
        <option value="name">Nome (A–Z)</option><option value="population">Maior população</option></select></label>
      <div id="axis-slot"></div>
      <details class="ranking-triage">
        <summary class="button button-outline">Mínimos por eixo <span id="ranking-minimum-count" hidden></span></summary>
        <form id="ranking-triage-form" class="filter-popover">
          <fieldset><legend>Nota mínima por eixo</legend>
            <p>Preencha de 0 a 100. Os mínimos filtram os resultados e preservam a posição nacional.</p>
            <div class="ranking-minimums">${axisLabels.map((label, index) => `
              <label class="input-label">${label}
                <input name="minimum" id="ranking-minimum-${index}" type="number" min="0" max="100" step="any" placeholder="Sem mínimo">
              </label>`).join('')}</div>
          </fieldset>
          <div class="actions">
            <button class="button button-primary" type="submit">Aplicar</button>
            <button class="button button-outline" type="submit" id="ranking-save">Salvar recorte</button>
            <button class="button button-quiet" type="button" id="ranking-restore" disabled>Carregar salvo</button>
          </div>
        </form>
      </details>
      <button type="button" class="button button-quiet" id="ranking-clear">Limpar filtros</button></div>
      <div class="ranking-toolbar"><p id="ranking-count" aria-live="polite"></p>
        <button class="button button-outline" type="button" id="ranking-share">Compartilhar recorte</button>
      </div>
      <div class="ranking-table-wrap" tabindex="0" aria-label="Tabela do ranking">
        <table class="ranking-table"><thead><tr><th>Posição</th><th>Município</th><th>População</th><th id="ranking-score-label">Score geral</th><th>Ações</th></tr></thead>
        <tbody id="ranking-body"></tbody></table>
      </div>
      <div class="detail-actions">
        <button class="button button-outline" id="ranking-prev" type="button">Anterior</button>
        <span id="ranking-page" aria-live="polite"></span>
        <button class="button button-outline" id="ranking-next" type="button">Próxima</button>
      </div>
    </section>
    <dialog id="ranking-share-dialog" aria-labelledby="ranking-share-title">
      <div class="dialog-heading"><h2 id="ranking-share-title">Compartilhar recorte</h2>
        <form method="dialog"><button class="icon-btn" aria-label="Fechar">×</button></form></div>
      <label class="input-label">Link do ranking<input id="ranking-share-url" type="url" readonly></label>
      <div class="detail-actions"><button class="button button-primary" id="ranking-copy" type="button">Copiar link</button></div>
      <p class="dialog-status" id="ranking-share-status" role="status"></p>
    </dialog>`;
  $('#axis-slot').replaceWith($('.axis-scope'));
  const triage = $('.ranking-triage');
  const minimumFields = allAxes.map(index => $(`#ranking-minimum-${index}`));
  const filterFields = rankingFilterIds.map(id => $(`#${id}`));
  const badge = $('#ranking-minimum-count');
  const restore = $('#ranking-restore');
  const setFilters = filters => filterFields.forEach((field, index) => {
    field.value = filters[index];
    if (field.selectedIndex === -1) field.value = '';
  });
  const refreshMinimums = () => {
    minimumFields.forEach((field, index) => { field.value = rankingMinimums[index] ?? ''; });
    const total = rankingMinimums.filter(value => value !== null).length;
    badge.hidden = !total;
    badge.textContent = total;
  };
  const closeTriage = () => {
    triage.open = false;
    triage.querySelector('summary').focus();
  };
  const resetPage = () => { rankingPage = 1; renderRanking(); };
  const shared = readRankingLink();
  if (shared) {
    setFilters(shared.filters);
    sharedRankingUF = shared.filters[1].toUpperCase();
    rankingMinimums = shared.minimums;
    activeAxes = shared.axes.length ? shared.axes : [...allAxes];
    updateAxisControls();
    refreshMinimums();
  }
  const shareDialog = $('#ranking-share-dialog');
  const shareUrl = $('#ranking-share-url');
  const shareStatus = $('#ranking-share-status');
  $('#ranking-share').onclick = () => {
    const link = new URL(location.pathname, location.origin);
    link.searchParams.set('recorte', '1');
    filterFields.forEach((field, index) => {
      if (field.value) link.searchParams.set(rankingParams[index], field.value);
    });
    link.searchParams.set('eixos', activeAxes.map(index => index + 1).join(','));
    rankingMinimums.forEach((minimum, index) => {
      if (minimum !== null) link.searchParams.set(`min${index + 1}`, minimum);
    });
    shareUrl.value = link.href;
    shareStatus.textContent = '';
    shareDialog.showModal();
    shareUrl.focus();
    shareUrl.select();
  };
  $('#ranking-copy').onclick = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl.value);
      shareStatus.textContent = 'Link copiado.';
    } catch {
      shareUrl.focus();
      shareUrl.select();
      shareStatus.textContent = 'Link selecionado. Use a opção de copiar do navegador.';
    }
  };
  restore.disabled = !readRankingPreset();
  triage.addEventListener('toggle', () => { if (!triage.open) refreshMinimums(); });
  triage.addEventListener('keydown', event => { if (event.key === 'Escape' && triage.open) closeTriage(); });
  document.addEventListener('click', event => {
    if (triage.open && !triage.contains(event.target)) triage.open = false;
  });
  $('#ranking-triage-form').onsubmit = event => {
    event.preventDefault();
    rankingMinimums = minimumFields.map(field => field.value === '' ? null : field.valueAsNumber);
    refreshMinimums();
    resetPage();
    if (event.submitter?.id === 'ranking-save') {
      try {
        localStorage.setItem(rankingPresetKey, JSON.stringify({
          filters: filterFields.map(field => field.value), minimums: rankingMinimums, axes: activeAxes
        }));
        restore.disabled = false;
        notify('Recorte salvo neste navegador.');
      } catch {
        notify('Não foi possível salvar o recorte neste navegador.');
      }
    }
    closeTriage();
  };
  restore.onclick = () => {
    const preset = readRankingPreset();
    if (!preset || !edition) {
      notify('O recorte salvo e os dados do ranking precisam estar disponíveis.');
      return;
    }
    setFilters(preset.filters);
    rankingMinimums = preset.minimums;
    setScoreAxes(allAxes.filter(index => preset.axes.includes(index)));
    refreshMinimums();
    resetPage();
    closeTriage();
    notify('Recorte salvo carregado.');
  };
  $('#ranking-search').oninput = resetPage;
  $('.rank-filters').onchange = event => {
    if (filterFields.includes(event.target)) resetPage();
  };
  $('#ranking-clear').onclick = () => {
    for (const field of filterFields) field.value = '';
    rankingMinimums = allAxes.map(() => null);
    refreshMinimums();
    resetPage();
  };
  $('#ranking-prev').onclick = () => { rankingPage -= 1; renderRanking(); };
  $('#ranking-next').onclick = () => { rankingPage += 1; renderRanking(); };
}

function axisChart(item) {
  return `<div class="axis-bars">${activeAxes.map(i => {
    const value = item.eixos[i];
    return `<div><span>${axisLabels[i]}</span>${value == null ? '' :
      `<meter min="0" max="100" value="${value}" aria-label="${axisLabels[i]}"></meter>`}
      <strong>${formatValue(value)}</strong></div>`;
  }).join('')}</div>`;
}

function scopedHistory(item) {
  return Object.fromEntries(Object.entries(item.historico ?? {}).map(([date, score]) =>
    [date, scopedScore(score, item.historico_eixos?.[date])]).filter(([, score]) => score != null));
}

function publicationPoints(history) {
  return (history?.publicado ?? []).map(point => ({
    date: point.competencia,
    score: scopedScore(point.score, point.eixos),
    editionLabel: `Edição ${point.edicao_id}`,
    version: point.versao
  }));
}

function simulationPoints(item, history) {
  if (!history) return monthlyHistoryPoints(scopedHistory(item));
  return history.simulacao_scr.map(point => ({
    date: point.competencia,
    score: scopedScore(point.score, point.eixos)
  }));
}

$('#main').addEventListener('click', event => {
  const point = event.target.closest('[data-timeline-point]');
  if (!point) return;
  const timeline = point.closest('.score-timeline');
  timeline.querySelector('[aria-pressed="true"]')?.setAttribute('aria-pressed', 'false');
  point.setAttribute('aria-pressed', 'true');
  timeline.querySelector('[data-timeline-date]').textContent = point.dataset.date;
  timeline.querySelector('[data-timeline-score]').firstChild.textContent = point.dataset.score + ' ';
});

function charts(item, context = '', history = null, scale = null) {
  const caption = context ? `<p class="subtitle chart-context">${context}</p>` : '';
  const publications = publicationPoints(history);
  const editions = publications.length ? `<div class="history-series"><h3>Edições publicadas</h3>
    ${historyChart(publications, { scale, empty: 'Nenhuma edição publicada tem score para este município.' })}</div>` : '';
  return `<section class="panel chart-panel"><h2>Perfil por eixo</h2>${caption}${axisChart(item)}</section>
    <section class="panel chart-panel"><h2>Histórico do score</h2>${caption}${editions}<div class="history-series">
    ${edition?.demonstracao ? '' : `<h3>Simulação histórica com variação do SCR</h3>
      <p class="subtitle">Variam I01, I03 e I11. As demais fontes mantêm a referência da edição.</p>`}
    ${history !== null || item.historico ? historyChart(simulationPoints(item, history), { monthly: true, scale }) : '<p>Carregando histórico…</p>'}
    </div>
    </section>`;
}

function municipalityHistory(id) {
  return readJson(`/api/municipios/${encodeURIComponent(id)}/historico`);
}

let editionPair;

function editionChanges(from, to) {
  const first = from.municipio;
  const last = to.municipio;
  const a = scopedScore(first.score, first.eixos);
  const b = scopedScore(last.score, last.eixos);
  const contributions = activeAxes.map(index => {
    const before = first.eixos?.[index];
    const after = last.eixos?.[index];
    return Number.isFinite(before) && Number.isFinite(after)
      ? (after - before) / activeAxes.length : null;
  });
  const residual = a !== null && b !== null && contributions.every(value => value !== null)
    ? b - a - contributions.reduce((sum, value) => sum + value, 0) : 0;
  const rows = new Map(from.indicadores.map(ind => [ind.indicador, { before: ind }]));
  for (const ind of to.indicadores) {
    rows.set(ind.indicador, { before: rows.get(ind.indicador)?.before, after: ind });
  }
  const comparedFields = ['nota', 'valor_usado', 'valor_bruto', 'fonte', 'referencia',
    'situacao', 'situacao_original', 'unidade', 'uf', 'peso'];
  const changed = [...rows].sort(([a], [b]) => a.localeCompare(b)).map(([, pair]) => pair)
    .filter(({ before, after }) => comparedFields.some(key => before?.[key] !== after?.[key]));
  const observation = ind => ind ? `<strong>Nota ${formatValue(ind.nota)}</strong>
    <br>Valor usado ${formatValue(ind.valor_usado)} ${ind.valor_usado == null ? '' : html(ind.unidade)}
    ${ind.valor_bruto != null && ind.valor_bruto !== ind.valor_usado ? `<br>Valor de origem ${formatValue(ind.valor_bruto)}` : ''}
    <br>${html(ind.fonte)} · ${html(ind.referencia)}${ind.uf ? ' · ' + html(ind.uf) : ''}
    <br>${ind.situacao === 'reaproveitado' ? '<strong>Reaproveitado</strong>' : html(ind.situacao)}` : '—';
  return `
    ${from.edicao.versao !== to.edicao.versao ? '<p>As edições usam versões metodológicas diferentes. A variação pode incluir mudanças de método.</p>' : ''}
    ${a !== null && b !== null ? `<p><strong>${formatValue(a)} → ${formatValue(b)}</strong> · ${signedPoints(b - a)}</p>` :
      '<p>A variação total está indisponível porque uma das edições ficou sem score.</p>'}
    <p class="subtitle">A contribuição é a diferença na nota do eixo dividida pela quantidade de eixos ativos.</p>
    <ul class="history-values">${activeAxes.map((index, i) => `<li>
      ${axisLabels[index]} · ${formatValue(first.eixos?.[index])} → ${formatValue(last.eixos?.[index])}
      <strong>${contributions[i] === null ? '—' : signedPoints(contributions[i])}</strong></li>`).join('')}
      ${Math.abs(residual) >= 0.005 ? `<li>Diferença em relação ao score publicado <strong>${signedPoints(residual)}</strong></li>` : ''}
    </ul>
    <h3>Indicadores que mudaram</h3>
    ${changed.length ? `<div class="ranking-table-wrap" tabindex="0" aria-label="Indicadores que mudaram">
      <table class="ranking-table"><thead><tr><th>Indicador</th><th>Edição de referência</th><th>Edição comparada</th></tr></thead>
      <tbody>${changed.map(({ before, after }) => {
        const ind = after ?? before;
        return `<tr><th scope="row">${html(ind.indicador.toUpperCase() + ' · ' + ind.nome)}</th>
          <td>${observation(before)}</td><td>${observation(after)}</td></tr>`;
      }).join('')}</tbody></table></div>` : '<p>Nenhuma mudança nos indicadores auditados dessas edições.</p>'}`;
}

function setupEditionComparison(detail, history) {
  if (!history || history.publicado.length < 2) return;
  const editions = history.publicado;
  const options = editions.map(point => `<option value="${html(point.edicao_id)}">
    ${html(monthLabel(point.competencia))} · ${html(point.versao)} · edição ${html(point.edicao_id)}</option>`).join('');
  const panel = $('#edition-comparison');
  panel.hidden = false;
  panel.innerHTML = `<h2>Variação entre edições publicadas</h2>
    <div class="edition-filters">
      <label class="input-label">Edição de referência<select id="edition-from">${options}</select></label>
      <label class="input-label">Edição comparada<select id="edition-to">${options}</select></label>
    </div><div class="edition-results" aria-live="polite"></div>`;
  const from = $('#edition-from');
  const to = $('#edition-to');
  from.value = editionPair?.[0] ?? editions.at(-2).edicao_id;
  to.value = editionPair?.[1] ?? editions.at(-1).edicao_id;
  if (!from.value) from.value = editions.at(-2).edicao_id;
  if (!to.value) to.value = editions.at(-1).edicao_id;
  const output = panel.querySelector('.edition-results');
  const cache = new Map([[String(detail.edicao.id), Promise.resolve(detail)]]);
  const load = id => {
    if (!cache.has(id)) {
      const url = `/api/municipios/${encodeURIComponent(detail.municipio.id)}?edicao=${encodeURIComponent(id)}`;
      cache.set(id, readJson(url).catch(error => { cache.delete(id); throw error; }));
    }
    return cache.get(id);
  };
  let version = 0;
  const render = async () => {
    const request = ++version;
    editionPair = [from.value, to.value];
    if (from.value === to.value) {
      output.textContent = 'Escolha duas edições diferentes.';
      return;
    }
    output.textContent = 'Carregando a comparação…';
    try {
      const [first, last] = await Promise.all(editionPair.map(load));
      if (request === version && panel.isConnected) output.innerHTML = editionChanges(first, last);
    } catch {
      if (request === version && panel.isConnected) output.textContent = 'Não foi possível carregar as edições selecionadas.';
    }
  };
  from.onchange = to.onchange = render;
  render();
}

async function renderDetails() {
  const place = catalog.get(defaultId);
  if (!place) {
    $('#main').innerHTML = heading(titles.municipio, 'Consulte um município pela busca ou pelo ranking.') +
      '<p class="panel copy-panel">Município não encontrado.</p>';
    return;
  }
  const [detail, history] = await Promise.all([
    readJson(`/api/municipios/${encodeURIComponent(place.id)}`),
    municipalityHistory(place.id).catch(() => false)
  ]);
  const ranked = municipalities.get(place.id);
  const item = { ...detail.municipio, score: ranked?.score ?? null, position: ranked?.position ?? null };
  $('#main').innerHTML = heading(identity(place),
    `Código IBGE ${html(place.id)} · Competência ${html(monthLabel(detail.edicao.competencia))}`) +
    `<div class="detail-actions"><a href="ranking.html">← Ranking</a>
      ${item.score === null ? '' :
        `<button class="button button-outline" type="button" data-add="${item.id}">+ Adicionar à comparação</button>`}
      ${favoriteButton(place, true)}</div>
      <div class="metric-grid selection-metrics">
      <article class="metric-card primary-metric"><div class="metric-top">${metricLabels[0]}</div>
      <div class="metric-value">${item.score === null ? 'Indisponível' : `${formatValue(item.score)} <small>/ 100</small>`}</div></article>
      <article class="metric-card"><div class="metric-top">Posição nacional</div>
      <div class="metric-value">${item.position === null ? '—' : `${item.position}º`}</div></article></div>
      ${item.motivo_sem_score ? `<p>${html(item.motivo_sem_score)}</p>` : ''}
      <div class="bottom-grid detail-charts">${charts(item, '', history)}</div>
      <section id="edition-comparison" class="panel ranking-panel" hidden></section>
      <section class="panel ranking-panel"><h2>Indicadores e fontes</h2><div class="ranking-table-wrap">
      <table class="ranking-table"><thead><tr><th>Indicador</th><th>Valor usado</th><th>Nota</th>
      <th>Fonte e referência</th><th>Situação do dado de origem</th></tr></thead>
      <tbody>${detail.edicao.demonstracao ? '<tr><td colspan="5">Indicadores detalhados indisponíveis na demonstração.</td></tr>' :
        detail.indicadores.map(ind => `<tr>
        <th scope="row">${html(ind.indicador.toUpperCase() + ' · ' + ind.nome)}</th>
        <td>${formatValue(ind.valor_usado)} ${ind.valor_usado === null ? '' : html(ind.unidade)}</td>
        <td>${formatValue(ind.nota)}</td>
        <td>${html(ind.fonte)} · ${html(ind.referencia)}${ind.uf ? ' · ' + html(ind.uf) : ''}</td>
        <td>${html(ind.situacao)}</td></tr>`).join('')}</tbody></table></div></section>`;
  setupEditionComparison(detail, history);
  syncFavoriteButtons();
}

function renderFavorites() {
  $('#main').innerHTML = heading(titles.favoritos, 'Municípios salvos neste navegador.') + `
    <div class="detail-actions"><a class="button button-outline" id="favorites-ranking" href="ranking.html">Abrir ranking</a>
      <button class="button button-primary" id="favorites-export" type="button"${favorites.length ? '' : ' disabled'}>Exportar CSV</button></div>
    ${favorites.length ? `<section class="panel ranking-panel" aria-label="Municípios favoritos">
      <div class="ranking-table-wrap" tabindex="0" aria-label="Tabela de favoritos">
      <table class="ranking-table"><thead><tr><th>Município</th><th>Posição</th><th>${metricLabels[0]}</th><th>Ações</th></tr></thead>
      <tbody>${favorites.map(id => {
        const place = catalog.get(id);
        const item = municipalities.get(id);
        return `<tr><th scope="row">${place ? identity(place) : html(id)}</th>
          <td>${item?.position != null ? item.position + 'º' : '—'}</td><td>${formatValue(item?.score)}</td>
          <td><div class="actions">${place ? details(place) : ''}${item ? plus(item) : ''}
          ${favoriteButton(place || { id, nome: id }, true)}</div></td></tr>`;
      }).join('')}</tbody></table></div></section>`
      : '<p class="panel copy-panel">Salve municípios pela estrela no ranking ou pelo botão na página do município.</p>'}`;
  $('#favorites-export').onclick = () => exportMunicipalities(favorites, 'kredita-favoritos.csv');
  syncFavoriteButtons();
}

let comparisonReference = 'uf';
const populationLabels = { small: 'até 20 mil', medium: 'mais de 20 mil até 100 mil', large: 'acima de 100 mil' };

function comparisonBenchmark(item) {
  const byState = comparisonReference === 'uf';
  const group = byState ? item.uf : populationGroup(item);
  if (!group) return '<p class="comparison-benchmark">Mediana indisponível para este porte.</p>';
  const values = scores.filter(candidate => (byState ? candidate.uf : populationGroup(candidate)) === group)
    .map(candidate => candidate.score).sort((a, b) => a - b);
  if (!values.length) return '<p class="comparison-benchmark">Mediana indisponível para este grupo.</p>';
  const middle = Math.floor(values.length / 2);
  const median = values.length % 2 ? values[middle] : (values[middle - 1] + values[middle]) / 2;
  const label = byState ? `Mediana de ${html(group)}` : `Mediana nacional · ${populationLabels[group]} habitantes`;
  return `<div class="comparison-benchmark"><span>${label}</span>
    <strong>${formatValue(median)} <small>/ 100</small></strong>
    <small>${signedPoints(item.score - median)} em relação à mediana · ${count.format(values.length)} ${values.length === 1 ? 'município' : 'municípios'}</small></div>`;
}

function renderComparison() {
  for (const id of comparison) {
    if (municipalities.has(id) && !historyCache.has(id)) {
      historyCache.set(id, null);
      const requestedEdition = edition.id;
      municipalityHistory(id).catch(() => false).then(history => {
        if (edition.id !== requestedEdition) return;
        historyCache.set(id, history);
        renderComparison();
      });
    }
  }
  const comparisonHistory = comparison.flatMap(id => {
    const item = municipalities.get(id);
    if (!item) return [];
    const history = historyCache.get(id);
    return [...publicationPoints(history), ...simulationPoints(item, history)];
  });
  const comparisonScale = historyScale(comparisonHistory);
  $('#main').innerHTML = heading(titles.comparar, 'Compare score, posição, eixos e histórico de até três municípios.') +
    `<div class="detail-actions"><button class="button button-primary" type="button" id="page-compare-open">+ Adicionar município</button>
      <button class="button button-outline" id="comparison-export" type="button"${comparison.length ? '' : ' disabled'}>Exportar CSV</button></div>
      ${comparison.length ? `<section class="panel comparison-reference">
        <label class="input-label">Referência do score<select id="comparison-reference">
          <option value="uf"${comparisonReference === 'uf' ? ' selected' : ''}>Mediana estadual</option>
          <option value="porte"${comparisonReference === 'porte' ? ' selected' : ''}>Mediana do mesmo porte</option>
        </select></label>
        <p class="subtitle">A mediana usa o score dos eixos ativos e inclui todos os municípios com score no grupo.</p>
      </section>` : ''}
      ${comparison.length ? `<section class="compare-grid" aria-label="Municípios selecionados">${comparison.map(id => {
        const item = municipalities.get(id);
        const place = catalog.get(id);
        const title = place ? identity(place) : 'Município ' + html(id);
        return `<article class="compare-card">
          <div class="panel compare-heading"><h2>${title}</h2>
          ${item ? `<div class="compare-score"><strong>${number.format(item.score)}</strong><span>/ 100 · ${item.position}º no Brasil</span></div>`
            : '<p>Score indisponível</p>'}
          ${item ? comparisonBenchmark(item) : ''}
          <div class="actions">${place ? details(place) + favoriteButton(place) : ''}
          <button class="button button-quiet" type="button" data-remove="${html(id)}"
            aria-label="Remover ${place ? html(place.nome) : html(id)} da comparação">Remover</button></div></div>
          ${item ? charts(item, '', historyCache.get(id), comparisonScale) : ''}</article>`;
      }).join('')}</section>` : '<p class="panel copy-panel">Adicione municípios pela busca acima ou pelo botão + no ranking.</p>'}
      ${comparison.length >= 2 ? '<section class="panel ranking-panel" id="comparison-history"><h2>Histórico lado a lado</h2></section>' : ''}`;
  $('#page-compare-open').onclick = openCompare;
  $('#comparison-export').onclick = () => exportMunicipalities(comparison, 'kredita-comparacao.csv');
  const reference = $('#comparison-reference');
  if (reference) reference.onchange = () => {
    comparisonReference = reference.value;
    renderComparison();
    $('#comparison-reference').focus();
  };
  const historyPanel = $('#comparison-history');
  if (historyPanel) {
    const entries = comparison.map(id => {
      const item = municipalities.get(id);
      const history = historyCache.get(id);
      const place = catalog.get(id);
      return {
        name: place ? place.nome + ' · ' + place.uf : id,
        loading: Boolean(item && history === null),
        simulated: item ? simulationPoints(item, history) : [],
        published: publicationPoints(history)
      };
    });
    renderComparisonHistory(historyPanel, entries, edition.demonstracao);
  }
  syncFavoriteButtons();
}

if (page === 'guia') {
  $('#main').innerHTML = heading(titles.guia, 'Como consultar e comparar municípios no KREDITA.') + `
    <section class="panel copy-panel"><h2>Busca e mapa</h2><p>Digite o nome do município e escolha a sugestão com a UF correta.
    Use o filtro de UF para aproximar o mapa e preencher a lista de municípios. Você também pode clicar diretamente em uma área do mapa.</p>
    <h2>Ranking e detalhe</h2><p>Filtre o ranking e use Compartilhar recorte para copiar um link com os filtros aplicados.
    Use a seta para abrir o perfil e o histórico do município. Com duas edições publicadas, o detalhe explica a variação do score.</p>
    <h2>Comparação</h2><p>Use o botão + junto de um município ou no cabeçalho. Abra Comparar municípios para ver até três perfis lado a lado e escolha a mediana estadual ou a de municípios do mesmo porte como referência.</p>
    <h2>Atualização</h2><p>O botão Atualizar dados consulta a edição publicada.</p></section>`;
}

if (page === 'metodologia') {
  $('#main').innerHTML = heading(titles.metodologia, 'Escala, cobertura e origem dos dados exibidos.') + `
    <section class="panel copy-panel"><h2>Como o score é calculado</h2>
    <h3>1. Converter os dados em notas</h3>
    <p>Cada indicador tem uma fórmula para seu valor bruto e outra para a nota de 0 a 100. No I06, um saldo de −3 empregos formais por mil habitantes resulta em 50 + 50 × (−3 ÷ 15) = <strong>40 pontos</strong>. Um saldo confirmado de zero vale 50 pontos.</p>
    <h3>2. Calcular o índice municipal e o cofator</h3>
    <p><strong>M = soma das notas sem ajuste × seus pesos no índice.</strong> I02 vale 30%. I04, I05, I06, I07, I09 e I16 valem 10% cada. I13 e I14 valem 5% cada.</p>
    <p><strong>φ = 0,2 × (M ÷ 50 − 1)</strong>, limitado entre −0,2 e +0,2. Com M igual a 50, o cofator é zero. A fórmula multiplica os valores estaduais de I01, I03 e I11 por (1 − φ) e o de I08 por (1 + φ), antes de recalcular suas notas.</p>
    <h3>3. Combinar os eixos</h3>
    <p>A nota do eixo é a soma de cada nota multiplicada por seu peso dentro do eixo, dividida pela soma desses pesos.</p>
    <p><strong>Score geral = (Risco + Capacidade + Inclusão + Demografia) ÷ 4.</strong> Cada eixo responde por 25%. Para obter o score sem cofator, use a mesma média com as notas anteriores ao ajuste estadual.</p>
    <p>O seletor <strong>Eixos do score</strong> permite consultar a média e a posição nacional usando apenas os eixos marcados. A edição publicada usa os quatro eixos.</p>
    <p>A população absoluta (I15) tem peso zero. Ela é exibida no painel e serve de denominador em indicadores por habitante.</p>
    <h2>Exemplo auditado · Curitiba · dezembro de 2025</h2>
    <p>Com M = 71,24, o cofator foi 0,08495. Os quatro eixos tiveram notas 68,31, 67,43, 24,31 e 63,73. A média, calculada antes do arredondamento, foi <strong>55,95</strong>. O score sem cofator foi <strong>52,17</strong>.</p>
    <h2>Referências e lacunas</h2>
    <p>A competência identifica a edição do score. A referência indica a data do dado de origem e pode ser diferente para cada indicador.</p>
    <ul><li><strong>Observado</strong> · valor coletado na fonte.</li><li><strong>Estimado</strong> · valor obtido por uma regra da metodologia, como a média da UF para salário sem admissões válidas.</li>
    <li><strong>Reaproveitado</strong> · valor de uma referência anterior usado em uma nova edição, com a referência original visível.</li>
    <li><strong>Ausente</strong> · valor indisponível. Sem um indicador obrigatório, o município fica sem score.</li></ul>
    <h2>Edições e simulação SCR</h2><p>As edições publicadas guardam os resultados e fontes usados em cada publicação. A simulação mensal varia I01, I03 e I11 do SCR e mantém os demais indicadores na referência da edição.</p>
    <p><a href="apostas.html">Consultar a metodologia e as fontes dos dados de apostas</a></p></section>
    <section class="panel copy-panel bets-context"><h2>Indicadores e fontes</h2>
      <div class="ranking-table-wrap" tabindex="0" aria-label="Indicadores do score"><table class="ranking-table">
      <thead><tr><th>Indicador</th><th>Fonte</th><th>Unidade</th><th>Peso no score</th><th>Periodicidade</th></tr></thead>
      <tbody id="method-indicators"></tbody></table></div>
      <p><a href="https://www.ibge.gov.br/geociencias/todos-os-produtos-geociencias/15774-malhas.html">Malha Municipal do IBGE</a></p></section>
    <section class="panel copy-panel bets-context"><h2>Fórmula de cada indicador</h2>
      <p>Nas fórmulas, <strong>x</strong> é o valor usado. <strong>t</strong> é esse valor limitado à faixa indicada e <strong>ln</strong> é o logaritmo natural. Para os quatro indicadores estaduais ajustados, x já inclui o cofator.</p>
      <div id="method-formulas" class="method-formulas"></div></section>`;
}

function normalizationFormula(ind, precision) {
  const [a, b, c] = ind.params.map(value => precision.format(value));
  const lower = ind.params[0] < 0 ? `(${a})` : a;
  const bounds = end => `t limitado entre ${a} e ${end}.`;
  const single = expression => [[null, expression, bounds(b)]];
  const formulas = {
    linear: single(`100 × (t − ${lower}) ÷ (${b} − ${lower})`),
    inverse: single(`100 × (${b} − t) ÷ (${b} − ${lower})`),
    log: single(`100 × ln(t ÷ ${a}) ÷ ln(${b} ÷ ${a})`),
    loginverse: single(`100 × ln(${b} ÷ t) ÷ ln(${b} ÷ ${a})`),
    centerlog: [
      [`Quando t ≤ ${b}`, `50 × ln(t ÷ ${a}) ÷ ln(${b} ÷ ${a})`],
      [`Quando t > ${b}`, `50 + 50 × ln(t ÷ ${b}) ÷ ln(${c} ÷ ${b})`, bounds(c)]
    ],
    signed: [[null, `50 + 50 × x ÷ ${a}`, 'Nota limitada entre 0 e 100.']],
    informality: [
      [`Quando x ≤ ${b}`, `30 + 20 × (x − ${a}) ÷ (${b} − ${a})`, 'Nota limitada entre 30 e 50.'],
      [`Quando x > ${b}`, `50 + 50 × (x − ${b}) ÷ (${c} − ${b})`, 'Nota limitada entre 50 e 100.']
    ]
  };
  return formulas[ind.kind] ?? [];
}

async function loadMethodology() {
  const { indicadores } = await readJson('/api/metodologia');
  const weights = [10, 6.25, 8.75, 25 / 6, 25 / 6, 25 / 6, 25 / 6, 25 / 6, 25 / 6, 10, 10, 5, 5, 10, 0, 10];
  const frequencies = ['Mensal', 'Censitária', 'Mensal', 'Censitária', 'Mensal', 'Mensal', 'Censitária',
    'Mensal', 'Mensal', 'Mensal', 'Mensal', 'Censitária', 'Anual', 'Censitária', 'Anual', 'Conforme publicação'];
  const precision = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });
  $('#method-indicators').innerHTML = indicadores.map(ind => {
    const index = Number(ind.id.slice(1)) - 1;
    return `<tr><th scope="row">${html(ind.id.toUpperCase() + ' · ' + ind.nome)}</th>
      <td>${html(ind.fonte)}</td><td>${html(ind.unidade)}</td><td>${precision.format(weights[index])}%</td>
      <td>${frequencies[index]}</td></tr>`;
  }).join('');
  $('#method-formulas').innerHTML = indicadores.map(ind => `<details>
    <summary>${html(ind.id.toUpperCase() + ' · ' + ind.nome)}</summary>
    <div class="formula-block"><h3>Valor bruto</h3><div class="formula-expression">${html(ind.rawFormula)}</div></div>
    <div class="formula-block"><h3>Nota</h3>
      ${ind.kind === 'none' ? '<p>A população é exibida em habitantes e tem peso zero no score.</p>' :
        normalizationFormula(ind, precision).map(([condition, expression, limit]) => `<div class="formula-case">
          ${condition ? `<div class="formula-condition">${html(condition)}</div>` : ''}
          <div class="formula-expression">Nota = ${html(expression)}</div>
          ${limit ? `<p class="formula-limit">${html(limit)}</p>` : ''}
        </div>`).join('')}
    </div>
    <ul>${ind.steps.map(step => `<li>${html(step)}</li>`).join('')}</ul>
    <p>${html(ind.caveat)}</p></details>`).join('');
}

let bets;
const betsPercent = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });

function betsValue(row) {
  return betsPercent.format(row.valor) + '%';
}

function betsMargin(row) {
  return row.margem_pp == null ? 'Margem não publicada' : '± ' + betsPercent.format(row.margem_pp) + ' p.p.';
}

function renderBetsCard(state) {
  const row = bets?.territorios.find(item => item.uf === (state || 'BR'));
  const card = $('#bets-card');
  card.hidden = !row;
  if (!row) return;
  card.innerHTML = `<div class="metric-top">Apostas esportivas online</div>
    <div class="metric-value">${betsValue(row)} <small>${betsMargin(row)}</small></div>
    <div class="metric-note">${state ? 'Contexto estadual · ' + html(state) : 'Brasil'} · DataSenado · ${html(bets.inicio.slice(0, 4))}</div>
    <a href="apostas.html${state ? '?uf=' + encodeURIComponent(state) : ''}">Explorar dados de apostas →</a>`;
}

function renderBetsPage() {
  const selector = $('#bets-uf');
  const national = bets.territorios.find(row => row.uf === 'BR');
  const states = bets.territorios.filter(row => row.uf !== 'BR').sort((a, b) => a.uf.localeCompare(b.uf));
  const requested = selector.value || new URLSearchParams(location.search).get('uf');
  selector.replaceChildren(new Option('Escolha uma UF', ''), ...states.map(row => new Option(row.uf, row.uf)));
  if (states.some(row => row.uf === requested)) selector.value = requested;
  const date = iso => iso.split('-').reverse().join('/');
  $('#bets-source').textContent = bets.estudo + ' · Coleta de ' + date(bets.inicio) + ' a ' + date(bets.fim);
  $('#bets-source').href = bets.fonte;
  $('#bets-definition').textContent = bets.metrica + '.';
  $('#bets-table').innerHTML = states.map(row => `<tr><th scope="row">${html(row.uf)}</th>
    <td>${betsValue(row)}</td><td>${betsMargin(row)}</td>
    <td>${count.format(row.populacao_estimada)}</td></tr>`).join('');
  selector.onchange = () => {
    const state = states.find(row => row.uf === selector.value);
    $('#bets-chart').innerHTML = (state ? [national, state] : [national]).map(row => {
      const margin = row.margem_pp ?? 0;
      const low = Math.max(0, row.valor - margin);
      const high = Math.min(100, row.valor + margin);
      return `<div class="bets-line">
        <strong>${row.uf === 'BR' ? 'Brasil' : html(row.uf)}</strong>
        <div class="bets-track" aria-hidden="true" style="--estimate:${row.valor}%;--low:${low}%;--width:${high - low}%">
          <span></span><i></i></div><span>${betsValue(row)} · ${betsMargin(row)}</span>
        </div>`;
    }).join('');
  };
  selector.onchange();
}

async function loadBets() {
  bets = await readJson('/api/apostas');
  if (page === 'index') renderBetsCard($('#dashboard-uf').value);
  if (page === 'apostas') renderBetsPage();
}

if (page === 'apostas') {
  $('#main').innerHTML = heading(titles.apostas, 'Levantamentos sobre apostas e comportamento financeiro.') + `
    <section class="panel copy-panel"><h2>Apostas esportivas por UF</h2>
      <p id="bets-definition"></p><label class="input-label">UF para comparar com o Brasil<select id="bets-uf"></select></label>
      <div id="bets-chart" aria-live="polite"></div><p class="subtitle">Escala de 0 a 100%. O traço indica a margem de erro.</p>
      <p><a id="bets-source">Fonte da pesquisa</a></p>
      <div class="ranking-table-wrap" tabindex="0" aria-label="Estimativas por UF">
        <table class="ranking-table"><thead><tr><th>UF</th><th>Estimativa</th><th>Margem de erro</th><th>Pessoas estimadas</th></tr></thead>
        <tbody id="bets-table"></tbody></table></div>
    </section>
    <section class="panel copy-panel bets-context"><h2>Outros levantamentos nacionais</h2>
      <h3>Ministério da Fazenda · Mercado regulado em 2025</h3>
      <p>Os operadores autorizados reportaram 25,2 milhões de participantes de apostas de quota fixa em 2025.
        <a href="https://www.gov.br/fazenda/pt-br/acesso-a-informacao/auditorias/arquivos/rgi_mf_2025_vf.pdf">Relatório de gestão da SPA</a></p>
      <h3>ANBIMA e Datafolha · Participação e perfil em 2025</h3>
      <p>Na pesquisa com pessoas a partir de 16 anos, 17% declararam ter feito apostas online em 2025. Entre os apostadores, 66% eram homens e a idade média era de 35 anos.
        <a href="https://www.anbima.com.br/data/files/BE/05/B0/55/1EABD91008E6DAD9F82BA2A8/Raio-X-do-Investidor-9-edicao.pdf">Raio X do Investidor Brasileiro, 9ª edição</a></p>
      <h3>NielsenIQ · Hábitos de consumo dos lares</h3>
      <p>A análise publicada em 2026 examina o orçamento de lares apostadores e inclui modalidades como loterias, jogos online e bets.
        <a href="https://nielseniq.com/global/pt/insights/analysis/2026/bets-entram-no-orcamento-familiar-e-pressionam-o-consumo-o-novo-retrato-do-shopper-brasileiro/">Estudo sobre apostas e consumo</a></p>
    </section>`;
}

async function readJson(path) {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) throw new Error('Falha ao ler ' + path);
  return response.json();
}

const catalogCacheKey = 'kredita-catalogo-sessao';

async function loadCatalog(manual) {
  const needsSim = page === 'index';
  if (!manual) {
    try {
      const cached = JSON.parse(sessionStorage.getItem(catalogCacheKey));
      if (cached?.edicao && Array.isArray(cached.municipios) && (!needsSim || cached.simulacao)) {
        return cached;
      }
    } catch {}
  }
  const data = await readJson('/api/municipios' + (needsSim ? '?simulacao=1' : ''));
  try {
    sessionStorage.setItem(catalogCacheKey, JSON.stringify({ ...data, simulacao: needsSim }));
  } catch {}
  return data;
}

async function reload(manual = false) {
  const data = await loadCatalog(manual);
  edition = data.edicao;
  $('#preview-banner').hidden = !edition.demonstracao;
  catalog = new Map(data.municipios.map(item => [item.id, item]));
  updateScoreScope();
  updateAxisControls();
  historyCache.clear();
  if (page === 'index') {
    loadBets().catch(() => {});
    const uf = catalog.get(selectedId)?.uf || $('#dashboard-uf').value;
    const states = [...new Set([...catalog.values()].map(item => item.uf))].sort();
    $('#dashboard-uf').replaceChildren(new Option('Todos os estados', ''),
      ...states.map(state => new Option(state, state)));
    if (states.includes(uf)) $('#dashboard-uf').value = uf;
    renderMapLocator();
    overviewPicker.render();
    updateSelection();
    renderDashboard();
  }
  if (page === 'ranking') {
    const uf = sharedRankingUF ?? $('#uf').value;
    sharedRankingUF = null;
    $('#uf').replaceChildren(new Option('Todas as UFs', ''), ...[...new Set([...catalog.values()].map(item => item.uf))]
      .sort().map(state => new Option(state, state)));
    if ([...$('#uf').options].some(option => option.value === uf)) $('#uf').value = uf;
    renderRanking();
  }
  if (page === 'municipio') await renderDetails();
  if (page === 'comparar') renderComparison();
  if (page === 'favoritos') renderFavorites();
  dialogPicker.render();
}

async function refresh(manual) {
  $('#refresh').disabled = true;
  $('#main').setAttribute('aria-busy', 'true');
  try {
    if (page === 'apostas') await loadBets();
    else if (page === 'metodologia') await loadMethodology();
    else await reload(manual);
    $('#load-error')?.remove();
    if (manual) notify('Dados municipais atualizados.');
  } catch {
    if ((!scores.length || page === 'municipio') && !$('#load-error')) {
      const error = document.createElement('p');
      error.id = 'load-error';
      error.className = 'panel copy-panel';
      error.setAttribute('role', 'alert');
      error.textContent = page === 'apostas' ? 'Não foi possível carregar as estimativas de apostas.' :
        page === 'metodologia' ? 'Não foi possível carregar a tabela de indicadores.' :
        'Não foi possível carregar os dados municipais. Tente atualizar os dados.';
      $('#main').prepend(error);
    }
    notify('Falha ao atualizar os dados municipais.');
  } finally {
    $('#refresh').disabled = false;
    $('#main').removeAttribute('aria-busy');
  }
}

$('#refresh').onclick = () => refresh(true);
refresh(false);
