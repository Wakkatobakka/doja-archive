#!/usr/bin/env python3
"""Validate source accounting, exports, generated pages, links and anchors offline."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlparse
import collections,csv,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
R=D['records'];C=D['counts'];entries=[e for r in R for e in r['entries']]
assert len(R)==C['grouped_catalog_records']
assert len(entries)==C['included_doja_entries']==C['source_platform_labels']['doja']
assert len({r['id'] for r in R})==len(R)
assert len({e['id'] for e in entries})==len(entries)
assert len({e['source_row'] for e in entries})==len(entries)
assert len({e['source_filename'] for e in entries})==len(entries)
assert all(e['source_platform'].casefold()=='doja' and not e['package_inspected'] and not e['runtime_tested'] for e in entries)
assert C['entries_with_sd_data_reference']==sum(e['sd_data_listed'] for e in entries)
assert C['english_patch_entries']==sum(e['patch_language']=='English' for e in entries)
assert C['chinese_patch_entries']==sum(e['patch_language']=='Chinese' for e in entries)
assert C['trial_labeled_entries']==sum(bool(e['trial_label']) for e in entries)
assert C['entries_with_exact_website_name_match']==sum(e['website_exact_name_match'] for e in entries)

def csv_rows(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
audit=csv_rows('classification.csv')
assert len(audit)==C['source_game_list_entries']
assert dict(sorted(collections.Counter(a['source_platform'] for a in audit).items()))==C['source_platform_labels']
assert sum(a['included']=='True' for a in audit)==len(entries)
assert all((a['included']=='True')==(a['source_platform'].casefold()=='doja') for a in audit)
assert {(a['source_row'],a['entry_id']) for a in audit if a['included']=='True'}=={(str(e['source_row']),e['id']) for e in entries}
titles=csv_rows('catalog.csv');export=csv_rows('entries.csv')
assert {a['record_id'] for a in titles}=={r['id'] for r in R} and len(titles)==len(R)
assert len(export)==len(entries)
byid={e['id']:e for e in entries}
for row in export:
    e=byid[row['entry_id']]
    for key in ['source_row','source_title','source_japanese_title','source_filename','source_platform','patch_label','patch_language','trial_label','sd_data_listed','source_variant_text','website_exact_name_match','package_inspected','runtime_tested']:
        assert row[key]==str(e[key]),(key,e['id'])
    assert row['snapshot_date']==D['snapshot_date']

class Page(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.tags=[];self.ids=set();self.refs=[];self.raw=path.read_text(encoding='utf-8')
        self.feed(self.raw)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags.append((tag,a))
        if 'id' in a:
            assert a['id'] not in self.ids,('Duplicate id',a['id'])
            self.ids.add(a['id'])
        for key in ['href','src']:
            if a.get(key):self.refs.append(a[key])
paths=[ROOT/'index.html',ROOT/'about/index.html',ROOT/'404.html',*sorted((ROOT/'games').glob('*/index.html'))]
assert len(paths)==len(R)+3
pages={p.resolve():Page(p) for p in paths}
local=0
for path,p in pages.items():
    assert sum(t=='h1' for t,a in p.tags)==1,path
    assert any(t=='title' for t,a in p.tags),path
    assert 'source_platform' not in p.raw or path.name=='index.html'  # No accidental raw data dump in a record.
    for ref in p.refs:
        u=urlparse(ref)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/'index.html'
        assert target.is_relative_to(ROOT.resolve()),('Outside repository',ref,path)
        assert target.exists(),('Broken local reference',ref,path)
        if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,('Broken anchor',ref,path)
        local+=1
home=pages[(ROOT/'index.html').resolve()]
cards=[a for t,a in home.tags if t=='a' and a.get('class')=='record']
assert len(cards)==len(R)
assert {a['data-name'] for a in cards}=={r['title'] for r in R}
for a in cards:assert isinstance(json.loads(a['data-entries']),list)
for r in R:
    p=pages[(ROOT/'games'/r['id']/'index.html').resolve()]
    assert {e['id'] for e in r['entries']}<=p.ids
    for e in r['entries']:
        from html import escape
        assert escape(e['source_filename'],quote=True) in p.raw
assert {'game-search','edition-filter','sd-filter','sort-by','reset-filters','previous-page','next-page'}<=home.ids
assert len(ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'))==len(R)+2
assert (ROOT/'assets/social-preview.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
dirge=next(r for r in R if r['title']=='Final Fantasy 7 - Dirge of Cerberus - Lost Episode')
assert len(dirge['entries'])==3
assert sum(bool(e['trial_label']) for e in dirge['entries'])==1
assert sum(e['patch_language']=='English' for e in dirge['entries'])==1
assert sum(e['sd_data_listed'] for e in dirge['entries'])==2
print(f'PASS: {len(entries):,} DoJa entries; {len(R):,} records; runtime exclusions and exports reconciled; {len(paths):,} pages; {local:,} local links/anchors; Dirge editions retained.')
