'use strict';
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
  const headings = [...document.querySelectorAll(bibliography ? '.bibliography h2,.bibliography h3' : '.publication-theme > h2')];
  const groups = [...document.querySelectorAll('.publication-theme')];
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
    groups.forEach(group => {
      group.hidden = !items.some(item => group.contains(item) && !item.hidden);
    });
  }
  search.addEventListener('input', update);
  clear.addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  update();
}

const menu = document.querySelector('.mobile-menu');
const disclosures = [...document.querySelectorAll('.nav-disclosure')];
const closeDisclosures = except => disclosures.forEach(item => {
  if (item !== except) item.open = false;
});

// Native disclosures support touch, keyboard, and navigation without JavaScript.
disclosures.forEach(item => {
  item.addEventListener('toggle', () => {
    if (item.open) closeDisclosures(item);
  });
});

document.addEventListener('click', event => {
  disclosures.forEach(item => {
    if (!item.closest('.nav-group').contains(event.target)) item.open = false;
  });
  if (menu && !menu.contains(event.target)) menu.open = false;
});

document.addEventListener('focusin', event => {
  disclosures.forEach(item => {
    if (!item.closest('.nav-group').contains(event.target)) item.open = false;
  });
  if (menu && !menu.contains(event.target)) menu.open = false;
});

document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const openDisclosure = disclosures.find(item => item.open);
  if (openDisclosure) {
    openDisclosure.open = false;
    openDisclosure.querySelector('summary').focus();
    event.preventDefault();
  } else if (menu && menu.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
    event.preventDefault();
  }
});

if (menu) {
  menu.addEventListener('toggle', () => {
    if (!menu.open) closeDisclosures();
  });
}

window.matchMedia('(max-width: 1120px)').addEventListener('change', () => {
  closeDisclosures();
  if (menu) menu.open = false;
});
