(() => {
  'use strict';
  const grid = document.getElementById('game-list');
  if (!grid) return;
  const $ = id => document.getElementById(id);
  const search = $('game-search'), edition = $('edition-filter'), sd = $('sd-filter'), sort = $('sort-by');
  const reset = $('reset-filters'), previous = $('previous-page'), next = $('next-page');
  const normalize = text => String(text).normalize('NFKC').normalize('NFKD').toLocaleLowerCase().replace(/[\u0300-\u036f]/g, '');
  const records = Array.from(grid.querySelectorAll('.record')).map(node => ({
    node, name: node.dataset.name, terms: normalize(node.dataset.search), count: Number(node.dataset.count), entries: JSON.parse(node.dataset.entries)
  }));
  const pageSize = 60;
  let currentPage = 1, lastSort = '';
  const params = new URLSearchParams(location.search);
  search.value = (params.get('q') || '').slice(0, 150);
  for (const [control, key] of [[edition, 'edition'], [sd, 'sd'], [sort, 'sort']]) {
    const value = params.get(key);
    if (Array.from(control.options).some(option => option.value === value)) control.value = value;
  }
  const requested = Number(params.get('page'));
  if (Number.isSafeInteger(requested) && requested > 0) currentPage = requested;
  function entryMatches(entry) {
    const e = edition.value;
    const editionMatches = !e || (e === 'english' && entry.patch === 'English') ||
      (e === 'chinese' && entry.patch === 'Chinese') || (e === 'trial' && entry.trial) ||
      (e === 'unmarked' && !entry.patch && !entry.trial);
    return editionMatches && (!sd.value || entry.sd === (sd.value === 'yes'));
  }
  function refresh(firstPage = false) {
    if (firstPage) currentPage = 1;
    if (sort.value !== lastSort) {
      const byTitle = (a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'base' });
      records.sort(sort.value === 'reverse' ? (a, b) => byTitle(b, a) : sort.value === 'entries' ? (a, b) => b.count - a.count || byTitle(a, b) : byTitle);
      const fragment = document.createDocumentFragment();
      records.forEach(record => fragment.appendChild(record.node));
      grid.appendChild(fragment);
      lastSort = sort.value;
    }
    const tokens = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    const matches = records.filter(record => tokens.every(token => record.terms.includes(token)) && record.entries.some(entryMatches));
    const pages = Math.max(1, Math.ceil(matches.length / pageSize));
    currentPage = Math.min(currentPage, pages);
    records.forEach(record => { record.node.hidden = true; });
    const start = (currentPage - 1) * pageSize;
    matches.slice(start, start + pageSize).forEach(record => { record.node.hidden = false; });
    const comma = number => number.toLocaleString('en-US');
    $('result-count').textContent = `${comma(matches.length)} of ${comma(records.length)} records` +
      (matches.length ? ` · Showing ${comma(start + 1)}–${comma(Math.min(start + pageSize, matches.length))}` : '');
    $('no-results').hidden = matches.length !== 0;
    $('pagination').hidden = pages === 1;
    $('page-count').textContent = `Page ${currentPage} of ${pages}`;
    previous.disabled = currentPage === 1;
    next.disabled = currentPage === pages;
    reset.hidden = !search.value && !edition.value && !sd.value && sort.value === 'title' && currentPage === 1;
    const url = new URL(location.href);
    for (const [key, value] of [['q', search.value.trim()], ['edition', edition.value], ['sd', sd.value], ['sort', sort.value === 'title' ? '' : sort.value], ['page', currentPage === 1 ? '' : String(currentPage)]]) {
      if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
    }
    try { history.replaceState(null, '', url); } catch (_) { /* Some file previews restrict history updates. */ }
  }
  $('catalog-filters').hidden = false;
  search.addEventListener('input', () => refresh(true));
  [edition, sd, sort].forEach(control => control.addEventListener('change', () => refresh(true)));
  reset.addEventListener('click', () => {
    search.value = edition.value = sd.value = '';
    sort.value = 'title'; refresh(true); search.focus();
  });
  for (const [button, step] of [[previous, -1], [next, 1]]) button.addEventListener('click', () => {
    currentPage += step; refresh(); $('catalog').scrollIntoView({ behavior: 'instant', block: 'start' });
  });
  refresh();
})();
