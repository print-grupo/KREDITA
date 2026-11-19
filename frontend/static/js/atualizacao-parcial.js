const pagina = document.body.dataset.page;
const retorno = document.querySelector('#retorno');
const painel = () => document.querySelector('#conteudo');
const chaves = { favoritos: 'kredita-favoritos', comparar: 'kredita-comparacao', eixos: 'kredita-eixos' };
let pendente;
let mapa;
let calcularFaixas;
let ufAnterior;
let municipioAnterior;
const secaoMapa = document.querySelector('#map-section');

function ler(chave, fallback = []) {
  try {
    return JSON.parse(localStorage.getItem(chave)) ?? fallback;
  } catch {
    return fallback;
  }
}

function guardar(chave, valor) {
  try {
    localStorage.setItem(chave, JSON.stringify(valor));
  } catch {
    retorno.textContent = 'O navegador não conseguiu salvar a preferência.';
  }
}

function lista(nome) {
  const dados = ler(chaves[nome]);
  return Array.isArray(dados) ? dados.map(String).filter(codigo => /^\d{7}$/.test(codigo)) : [];
}

function preferencias(url) {
  const destino = new URL(url);
  if (!destino.searchParams.has('eixos')) destino.searchParams.set('eixos', painel().dataset.eixos);
  for (const nome of ['favoritos', 'comparar']) {
    const ids = lista(nome);
    if (ids.length) destino.searchParams.set(nome, ids.join(','));
    else if (ler(chaves[nome], null) !== null) destino.searchParams.delete(nome);
  }
  return destino;
}

function formatarFaixa(valor) {
  return Number.isFinite(valor) ? valor.toFixed(1).replace('.', ',') : '—';
}

function renderizarLegenda(faixas) {
  const legenda = document.querySelector('#map-legend');
  if (!legenda) return;
  const tituloEscala = document.querySelector('#map-scale-title');
  if (tituloEscala) {
    const eixos = (painel()?.dataset.eixos || '1,2,3,4').split(',').filter(Boolean);
    tituloEscala.textContent = eixos.length === 4 ? 'Score geral' : 'Score dos eixos selecionados';
  }
  const itens = faixas.map(({ min, max, color }, indice) => {
    const intervalo = indice
      ? 'Acima de ' + formatarFaixa(min) + ' até ' + formatarFaixa(max)
      : (min === max ? formatarFaixa(max) : formatarFaixa(min) + '–' + formatarFaixa(max));
    return `<li><span style="--swatch:${color}"></span>${intervalo}</li>`;
  });
  itens.push('<li><span style="--swatch:var(--map-unrated)"></span>Fora do recorte ou sem dados</li>');
  legenda.innerHTML = itens.join('');
}

function sincronizar() {
  const encaixe = document.querySelector('[data-map-slot]');
  if (secaoMapa && encaixe) encaixe.replaceWith(secaoMapa);
  const cabecalhoMapa = document.querySelector('#map-header-controls');
  const slotCabecalho = secaoMapa?.querySelector('[data-map-header-slot]');
  if (cabecalhoMapa && slotCabecalho) {
    cabecalhoMapa.hidden = false;
    slotCabecalho.replaceChildren(cabecalhoMapa);
  }
  const salvos = lista('favoritos');
  for (const botao of document.querySelectorAll('[data-favorite]')) {
    const salvo = salvos.includes(botao.dataset.favorite);
    botao.setAttribute('aria-pressed', String(salvo));
    const estrela = botao.querySelector('[data-estrela]');
    if (estrela) estrela.textContent = salvo ? '★' : '☆';
    const legenda = botao.querySelector('.acao-legenda');
    if (legenda) legenda.textContent = salvo ? 'Salvo' : 'Favoritar';
  }
  const info = document.querySelector('#dados-mapa');
  if (!mapa || !info) return;
  const dados = JSON.parse(info.textContent);
  const faixas = calcularFaixas(dados.map(([, score]) => score));
  renderizarLegenda(faixas);
  mapa.updateScores(dados, faixas);
  const uf = painel().dataset.uf;
  if (uf !== ufAnterior) mapa.focusArea(uf ? dados.map(([id]) => id) : []);
  const id = painel().dataset.id;
  mapa.highlight(id, Boolean(id) && id !== municipioAnterior);
  municipioAnterior = id;
  ufAnterior = uf;
}

async function atualizar(url, registrar = true) {
  pendente?.abort();
  const controle = new AbortController();
  pendente = controle;
  painel().setAttribute('aria-busy', 'true');
  retorno.textContent = 'Carregando…';
  try {
    const resposta = await fetch(preferencias(url), {
      headers: { 'X-Kredita-Parcial': '1' }, signal: controle.signal, cache: 'no-store'
    });
    if (!resposta.ok) throw new Error();
    const html = new DOMParser().parseFromString(await resposta.text(), 'text/html');
    if (controle.signal.aborted) return;
    const novo = html.querySelector('#conteudo');
    if (!novo) throw new Error();
    const campo = painel().contains(document.activeElement) ? document.activeElement : null;
    const nome = campo?.name;
    const selecao = campo?.type === 'search' ? [campo.selectionStart, campo.selectionEnd] : null;
    painel().replaceWith(novo);
    if (nome) {
      const equivalente = novo.querySelector('[name="' + CSS.escape(nome) + '"]');
      equivalente?.focus({ preventScroll: true });
      if (equivalente?.type === 'search' && selecao) equivalente.setSelectionRange(...selecao);
    }
    if (registrar && url.href !== location.href) history.pushState(null, '', url);
    if (registrar && url.searchParams.has('eixos') && url.searchParams.get('recorte') !== '1') {
      guardar(chaves.eixos, novo.dataset.eixos.split(',').map(eixo => Number(eixo) - 1));
    }
    sincronizar();
    retorno.textContent = '';
  } catch {
    if (!controle.signal.aborted) retorno.textContent = 'Falha ao atualizar. Tente novamente.';
  } finally {
    if (pendente === controle) painel().removeAttribute('aria-busy');
  }
}

function filtros(formulario) {
  const url = new URL(formulario.action, location.href);
  url.search = new URLSearchParams(new FormData(formulario));
  const eixos = url.searchParams.getAll('eixos');
  if (eixos.length) url.searchParams.set('eixos', eixos.join(','));
  else if (formulario.querySelector('[name=eixos]')) url.searchParams.set('eixos', '1,2,3,4');
  return url;
}

function municipio(id) {
  const url = new URL(location.href);
  url.searchParams.set('id', id);
  url.searchParams.delete('busca');
  url.searchParams.set('eixos', painel().dataset.eixos);
  atualizar(url);
}

document.addEventListener('submit', async evento => {
  const form = evento.target;
  if (form.matches('[data-parcial]')) {
    evento.preventDefault();
    atualizar(filtros(form));
  }
  if (form.matches('[data-sugestoes]')) {
    evento.preventDefault();
    const destino = document.querySelector('[data-sugestoes-resultado]');
    try {
      const resposta = await fetch(preferencias(filtros(form)));
      if (!resposta.ok) throw new Error();
      destino.innerHTML = await resposta.text();
      sincronizar();
    } catch {
      destino.textContent = 'Não foi possível buscar municípios.';
    }
  }
});

const menuMobile = matchMedia('(max-width: 760px)');
let menuAberto = !menuMobile.matches;
function ajustarMenu(abrir) {
  menuAberto = abrir;
  document.querySelector('.app-shell')?.classList.toggle('sidebar-collapsed', !abrir);
  document.querySelector('.hamburger')?.setAttribute('aria-expanded', String(abrir));
  const sidebar = document.querySelector('#sidebar');
  if (sidebar) sidebar.inert = !abrir;
  const sombra = document.querySelector('.menu-shade');
  if (sombra) sombra.hidden = !abrir || !menuMobile.matches;
}
ajustarMenu(menuAberto);
menuMobile.addEventListener('change', evento => ajustarMenu(!evento.matches));

document.addEventListener('click', async evento => {
  for (const aberto of document.querySelectorAll('details.axis-scope[open], details.ranking-triage[open], details.dashboard-extra-filters[open]')) {
    if (!aberto.contains(evento.target)) aberto.open = false;
  }
  const plot = evento.target.closest('#comparison-history .timeline-plot[data-plot-datas]');
  if (plot) {
    const seletor = document.querySelector('[data-diferencas]');
    if (seletor) {
      const posicoes = JSON.parse(plot.dataset.plotDatas);
      const box = plot.getBoundingClientRect();
      const alvoX = 100 * (evento.clientX - box.left) / box.width;
      const maisProximo = Object.entries(posicoes).reduce((melhor, atual) =>
        Math.abs(atual[1] - alvoX) < Math.abs(melhor[1] - alvoX) ? atual : melhor
      )[0];
      seletor.value = maisProximo;
      seletor.dispatchEvent(new Event('change', { bubbles: true }));
    }
    return;
  }
  const alvo = evento.target.closest('a, button, [data-ponto]');
  if (!alvo) return;
  const dados = alvo.dataset;
  if ('menu' in dados) {
    ajustarMenu(alvo.classList.contains('menu-shade') ? false : !menuAberto);
  }
  if ('eixosTodos' in dados) {
    const form = alvo.closest('form');
    if (form) {
      for (const box of form.querySelectorAll('input[name="eixos"]')) box.checked = true;
      form.requestSubmit();
    }
  }
  if (alvo.matches('a[data-parcial], a[data-pagina], a[data-municipio], a[data-exportar]') &&
      (evento.button || evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey)) return;
  if (alvo.matches('a[data-parcial], a[data-pagina]')) {
    evento.preventDefault();
    atualizar(new URL(alvo.href));
  }
  if (dados.municipio) {
    evento.preventDefault();
    municipio(dados.municipio);
  }
  if ('exportar' in dados) {
    evento.preventDefault();
    location.href = preferencias(alvo.href);
  }
  if ('refresh' in dados) atualizar(new URL(location.href), false);
  if ('open' in dados) document.querySelector('#comparacao-busca').showModal();
  if ('themeToggle' in dados) {
    const escuro = document.documentElement.dataset.theme !== 'dark';
    document.documentElement.dataset.theme = escuro ? 'dark' : 'light';
    try {
      localStorage.setItem('kredita-tema', escuro ? 'escuro' : 'claro');
    } catch {
      retorno.textContent = 'Preferência de tema indisponível neste navegador.';
    }
  }
  if (dados.favorite) {
    const ids = lista('favoritos');
    guardar(chaves.favoritos, ids.includes(dados.favorite) ? ids.filter(id => id !== dados.favorite) : [...ids, dados.favorite]);
    sincronizar();
    if (pagina === 'favoritos') atualizar(new URL(location.href), false);
  }
  if (dados.add || dados.remove) {
    const ids = lista('comparar');
    if (dados.add && ids.includes(dados.add)) {
      retorno.textContent = 'Município já está na comparação.';
      return;
    }
    if (dados.add && ids.length >= 3) {
      retorno.textContent = 'Remova um município antes de adicionar outro.';
      return;
    }
    guardar(chaves.comparar, dados.add ? [...ids, dados.add] : ids.filter(id => id !== dados.remove));
    sincronizar();
    retorno.textContent = dados.add ? 'Município adicionado à comparação.' : 'Município removido.';
    if (pagina === 'comparar') atualizar(new URL(location.href), false);
  }
  if ('save' in dados || 'share' in dados) {
    const url = filtros(alvo.form);
    url.searchParams.set('recorte', '1');
    if ('save' in dados) {
      const params = url.searchParams;
      guardar('kredita-recorte-ranking', {
        filters: ['busca', 'uf', 'porte', 'ordem'].map(chave => params.get(chave) || ''),
        minimums: [1, 2, 3, 4].map(i => params.get('min' + i) ? Number(params.get('min' + i)) : null),
        axes: (params.get('eixos') || '1,2,3,4').split(',').map(eixo => Number(eixo) - 1)
      });
      atualizar(url);
    } else {
      try {
        await navigator.clipboard.writeText(url.href);
        retorno.textContent = 'Link copiado.';
      } catch {
        retorno.textContent = url.href;
      }
    }
  }
  if ('restore' in dados) {
    const salvo = ler('kredita-recorte-ranking', null);
    if (!Array.isArray(salvo?.filters) || !Array.isArray(salvo?.axes) || !Array.isArray(salvo?.minimums)) {
      retorno.textContent = 'Nenhum recorte salvo.';
      return;
    }
    const url = new URL(location.pathname, location.origin);
    url.searchParams.set('recorte', '1');
    ['busca', 'uf', 'porte', 'ordem'].forEach((chave, i) => url.searchParams.set(chave, salvo.filters[i] || ''));
    salvo.minimums.forEach((valor, i) => { if (valor !== null) url.searchParams.set('min' + (i + 1), valor); });
    url.searchParams.set('eixos', salvo.axes.map(eixo => eixo + 1).join(','));
    atualizar(url);
  }
  if (dados.ponto) {
    const timeline = alvo.closest('[data-timeline]');
    timeline.querySelector('[data-leitura]').textContent = dados.ponto;
    const scoreEl = timeline.querySelector('[data-leitura-score]');
    if (scoreEl && dados.score) scoreEl.innerHTML = dados.score + ' <small>pts</small>';
    for (const btn of timeline.querySelectorAll('.timeline-point')) {
      btn.setAttribute('aria-pressed', String(btn === alvo));
    }
  }
});

document.addEventListener('change', evento => {
  if (evento.target.matches('[data-diferencas]')) {
    const mes = evento.target.value;
    for (const lista of document.querySelectorAll('[data-competencia]')) {
      lista.hidden = lista.dataset.competencia !== mes;
    }
    const plot = document.querySelector('#comparison-history .timeline-plot');
    const guide = plot?.querySelector('.comparison-month-guide');
    if (plot?.dataset.plotDatas && guide) {
      const pos = JSON.parse(plot.dataset.plotDatas)[mes];
      if (pos !== undefined) guide.style.left = pos + '%';
      for (const sel of plot.querySelectorAll('[data-sel-serie]')) {
        const pt = plot.querySelector(`.comparison-series-point[data-serie="${sel.dataset.selSerie}"][data-mes="${CSS.escape(mes)}"]`);
        sel.hidden = !pt;
        if (pt) { sel.style.left = pt.style.left; sel.style.top = pt.style.top; }
      }
    }
  }
  const formAuto = evento.target.closest('form[data-auto-submit]');
  if (formAuto && evento.target.matches('select')) {
    formAuto.requestSubmit();
  }
});

document.addEventListener('keydown', evento => {
  if (evento.key === 'Escape' && menuMobile.matches && menuAberto && !document.querySelector('#comparacao-busca')?.open) {
    ajustarMenu(false);
    document.querySelector('.hamburger')?.focus();
  }
});
window.addEventListener('popstate', () => atualizar(new URL(location.href), false));

let esperaBusca;
document.addEventListener('input', evento => {
  const campo = evento.target;
  if (pagina !== 'index' || !campo.matches('#conteudo [name=busca]')) return;
  clearTimeout(esperaBusca);
  esperaBusca = setTimeout(async () => {
    const texto = campo.value;
    const url = new URL('/site/sugestoes', location.origin);
    url.searchParams.set('busca', texto);
    url.searchParams.set('selecionar', '1');
    try {
      const resposta = await fetch(preferencias(url));
      const html = await resposta.text();
      if (resposta.ok && campo.isConnected && campo.value === texto) {
        painel().querySelector('[data-busca-resultados]').innerHTML = texto.trim() ? html : '';
        sincronizar();
      }
    } catch {
      if (campo.isConnected) retorno.textContent = 'Não foi possível buscar municípios.';
    }
  }, 250);
});

sincronizar();
const url = new URL(location.href);
const eixos = ler(chaves.eixos);
if (!url.searchParams.has('eixos') && Array.isArray(eixos) && eixos.length && eixos.length < 4) {
  url.searchParams.set('eixos', eixos.map(eixo => eixo + 1).join(','));
}
if (url.href !== location.href || (['comparar', 'favoritos'].includes(pagina) && lista(pagina).length)) {
  atualizar(url, false);
}
const elementoMapa = document.querySelector('#municipal-map');
if (elementoMapa) {
  elementoMapa.querySelector('[data-map-status]').textContent = 'Carregando mapa…';
  import('./mapa.js').then(({ createMap, scoreBands }) => {
    calcularFaixas = scoreBands;
    return createMap(elementoMapa, municipio);
  }).then(resultado => {
    mapa = resultado;
    elementoMapa.querySelector('[data-map-status]').textContent = '';
    sincronizar();
  }).catch(() => { elementoMapa.querySelector('[data-map-status]').textContent = 'Mapa indisponível.'; });
}
