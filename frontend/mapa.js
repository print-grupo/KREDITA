const NS = 'http://www.w3.org/2000/svg';
const country = { x: -75, y: -6, w: 42, h: 41 };
const svgElement = name => document.createElementNS(NS, name);
const scoreColors = Array.from({ length: 5 }, (_, index) => `var(--map-band-${index + 1})`);
const displayedScore = score => Number(score.toFixed(1));

export function scoreBands(values) {
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

async function mapFeatures(file) {
  const response = await fetch(file);
  if (!response.ok) throw new Error('Malha indisponível: ' + file);
  return (await response.json()).features;
}

function outline(geometry) {
  if (!geometry || !['Polygon', 'MultiPolygon'].includes(geometry.type)) return '';
  const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
  return polygons.flatMap(polygon => polygon.map(ring =>
    'M' + ring.map(([x, y]) => x.toFixed(4) + ',' + (-y).toFixed(4)).join('L') + 'Z'
  )).join('');
}

export async function createMap(container, select) {
  const [features, states] = await Promise.all([
    mapFeatures('municipios.geojson'),
    mapFeatures('estados.geojson').catch(() => [])
  ]);
  const svg = svgElement('svg');
  svg.setAttribute('aria-label', 'Mapa do Brasil com limites estaduais e municipais');
  const paths = new Map();
  const fragment = document.createDocumentFragment();
  let view = { ...country };
  let drag = null;
  let moved = false;
  let selected;
  let colored = new Set();

  function setView(next) {
    view = next;
    svg.setAttribute('viewBox', [view.x, view.y, view.w, view.h].join(' '));
    svg.classList.toggle('map-detail', view.w < 12);
  }

  function fitBounds(bounds, padding) {
    const width = Math.max(0.5, (bounds.right - bounds.left) * padding,
      (bounds.bottom - bounds.top) * padding * country.w / country.h);
    const height = width * country.h / country.w;
    setView({ x: (bounds.left + bounds.right - width) / 2,
      y: (bounds.top + bounds.bottom - height) / 2, w: width, h: height });
  }

  function areaBounds(ids) {
    const bounds = { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity };
    for (const id of ids) {
      const path = paths.get(id);
      if (!path) continue;
      const { x, y, width, height } = path.getBBox();
      bounds.left = Math.min(bounds.left, x);
      bounds.top = Math.min(bounds.top, y);
      bounds.right = Math.max(bounds.right, x + width);
      bounds.bottom = Math.max(bounds.bottom, y + height);
    }
    return bounds;
  }

  for (const feature of features) {
    const shape = outline(feature.geometry);
    if (!shape) continue;
    const path = svgElement('path');
    path.dataset.id = String(feature.properties.codarea);
    path.setAttribute('d', shape);
    path.setAttribute('fill-rule', 'evenodd');
    fragment.append(path);
    paths.set(path.dataset.id, path);
  }
  svg.append(fragment);
  if (states.length) {
    const borders = svgElement('path');
    borders.setAttribute('class', 'state-borders');
    borders.setAttribute('d', states.map(state => outline(state.geometry)).join(''));
    borders.setAttribute('aria-hidden', 'true');
    svg.append(borders);
  }
  container.prepend(svg);
  setView(country);

  function point(event) {
    return new DOMPoint(event.clientX, event.clientY).matrixTransform(svg.getScreenCTM().inverse());
  }

  function zoom(factor, x = view.x + view.w / 2, y = view.y + view.h / 2) {
    const width = Math.min(country.w, Math.max(0.18, view.w * factor));
    const ratio = width / view.w;
    setView({ x: x + (view.x - x) * ratio, y: y + (view.y - y) * ratio,
      w: width, h: view.h * ratio });
  }

  svg.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !event.isPrimary) return;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY, view,
      matrix: svg.getScreenCTM().inverse() };
    moved = false;
  });
  svg.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (Math.hypot(dx, dy) < 4 && !moved) return;
    moved = true;
    svg.setPointerCapture(event.pointerId);
    setView({ ...drag.view, x: drag.view.x - dx * drag.matrix.a,
      y: drag.view.y - dy * drag.matrix.d });
  });
  for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) {
    svg.addEventListener(event, () => { drag = null; });
  }
  svg.addEventListener('click', event => {
    const target = event.target.closest('[data-id]');
    if (!moved && target) select(target.dataset.id);
    moved = false;
  });
  svg.addEventListener('wheel', event => {
    if (!event.ctrlKey) return;
    event.preventDefault();
    const anchor = point(event);
    zoom(event.deltaY < 0 ? 0.75 : 1.33, anchor.x, anchor.y);
  }, { passive: false });
  container.querySelector('[data-zoom-in]').onclick = () => zoom(0.65);
  container.querySelector('[data-zoom-out]').onclick = () => zoom(1.54);
  container.querySelector('[data-map-reset]').onclick = () => setView(country);

  return {
    focusArea(ids) {
      const bounds = areaBounds(ids);
      if (Number.isFinite(bounds.left)) fitBounds(bounds, 1.18);
      else setView(country);
    },
    updateScores(municipalities, bands) {
      for (const id of colored) paths.get(id).style.removeProperty('--municipal-fill');
      colored = new Set();
      for (const [id, score] of municipalities) {
        const path = paths.get(id);
        if (!path || !Number.isFinite(score)) continue;
        const band = bands.find(item => displayedScore(score) <= item.max);
        if (!band) continue;
        path.style.setProperty('--municipal-fill', band.color);
        colored.add(id);
      }
    },
    highlight(id, focus = false) {
      selected?.classList.remove('selected');
      selected = paths.get(id);
      selected?.classList.add('selected');
      if (!selected || !focus) return;
      fitBounds(areaBounds([id]), 2.6);
    }
  };
}

