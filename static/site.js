'use strict';
// Keep the dated figure available while the forecast service loads.
const forecast = document.querySelector('[data-latest-forecast]');
if (forecast) {
  const latest = new Image();
  latest.addEventListener('load', () => {
    forecast.src = latest.src;
    forecast.alt = 'Latest available GeoDGP global magnetic-perturbation forecast; UTC forecast time appears on the map';
    forecast.closest('a').href = latest.src;
    document.querySelector('#forecast-status').textContent = 'Latest Available Forecast';
  });
  latest.src = forecast.dataset.latestForecast;
}

// Progressive enhancement: every publication remains readable without JavaScript.
const search = document.querySelector('#paper-search');
if (search) {
  const bibliography = document.body.classList.contains('page-bibliography');
  const items = [...document.querySelectorAll(bibliography ? '.bibliography ol > li' : '.publication-list .pub')];
  const normalize = text => text.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const labels = new Map(items.map(item => [item, normalize(item.textContent)]));
  const count = document.querySelector('#paper-count');
  const clear = document.querySelector('#clear-search');
  const empty = document.querySelector('#search-empty');
  const headings = [...document.querySelectorAll(bibliography ? '.bibliography h2,.bibliography h3' : '.publication-list > h2')];
  document.querySelector('[data-search-tools]').hidden = false;
  // Preserve citation numbers when filtering ordered bibliographies.
  document.querySelectorAll('.bibliography ol').forEach(list => {
    const rows = [...list.children].filter(row => row.tagName === 'LI');
    const reversed = list.hasAttribute('reversed');
    let value = Number(list.getAttribute('start') || (reversed ? rows.length : 1));
    rows.forEach(row => { row.value = value; value += reversed ? -1 : 1; });
  });
  function update() {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    items.forEach(item => { item.hidden = !terms.every(term => labels.get(item).includes(term)); });
    const visible = items.filter(item => !item.hidden).length;
    count.textContent = `${visible} of ${items.length} publications`;
    empty.hidden = visible !== 0;
    clear.hidden = !search.value;
    headings.forEach(heading => {
      let next = heading.nextElementSibling;
      let any = false;
      while (next && !/^H[23]$/.test(next.tagName)) {
        if (items.includes(next) && !next.hidden) any = true;
        if (items.some(item => next.contains(item) && !item.hidden)) any = true;
        next = next.nextElementSibling;
      }
      heading.hidden = !any;
    });
  }
  search.addEventListener('input', update);
  clear.addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  update();
}

const menu = document.querySelector('.mobile-menu');
if (menu) {
  menu.addEventListener('keydown', event => {
    if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); }
  });
  document.addEventListener('click', event => { if (!menu.contains(event.target)) menu.open = false; });
}
