#!/usr/bin/env python3
"""Normalize public launcher metadata. No game files are read or downloaded."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,collections,csv,hashlib,io,json,re,unicodedata,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE='http://cdn.keitaiarchive.org:9000/kwl/gamelist.xml'
CSV_SOURCE='https://keitaiarchive.org/searchable_media.csv'
PATCH=re.compile(r'^\[(ENGLISH PATCH(?:-Delocalized|-Localized)?|CHINESE PATCH)\]\s*',re.I)
TRIAL=re.compile(r'\s*(?:\[|\()(Trial|Preinstalled Trial|30 Second Trial|Demo|Trial Version|Demo Version)(?:\]|\))\s*$|\s+(Trial Version|Demo Version)\s*$',re.I)
# Only this display-name equivalence is curated; original source titles are retained.
ALIASES={'Final Fantasy VII Snowboarding':'Final Fantasy 7 Snowboarding'}

def decode(raw):
    for encoding in ('utf-8-sig','cp932'):
        try:return raw.decode(encoding),encoding
        except UnicodeDecodeError:pass
    raise ValueError('Metadata encoding was not UTF-8 or CP932; inspect before importing.')

def fingerprint(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def slug(value):
    s=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:72].rstrip('-') or 'doja'

def group_title(title):
    base=PATCH.sub('',title)
    base=TRIAL.sub('',base).strip()
    return ALIASES.get(base,base)

def ingest(xml_path,csv_path,date=None):
    raw=Path(xml_path).read_bytes();text,encoding=decode(raw);root=ET.fromstring(text)
    assert root.tag=='Gamelist','Unexpected source root'
    raw_csv=Path(csv_path).read_bytes();csv_text,csv_encoding=decode(raw_csv)
    website=list(csv.DictReader(io.StringIO(csv_text)))
    assert all({'name','carrier','media_type'}<=row.keys() for row in website)
    public_names=collections.Counter(r['name'] for r in website if r['carrier']=='NTT Docomo' and r['media_type']=='Application')
    source=[]
    for row,g in enumerate(root,1):
        record={tag:g.findtext(tag,default='').strip() for tag in ['ENTitle','JPTitle','ZIPName','Emulator','Variants']}
        record['sd_data_listed']=bool(g.findtext('SDCardDataURL',default='').strip())
        record['source_row']=row
        assert record['ENTitle'] and record['Emulator'],'Missing title or runtime in source'
        source.append(record)
    selected=[s for s in source if s['Emulator'].casefold()=='doja']
    assert selected and len({s['ZIPName'] for s in selected})==len(selected),'Inspect missing or duplicated package labels'
    grouped={};audit=[]
    for s in source:
        included=s['Emulator'].casefold()=='doja'
        if included:
            title=s['ENTitle'];base=group_title(title)
            rid=slug(base)+'--'+hashlib.sha256(base.casefold().encode()).hexdigest()[:8]
            eid='entry-'+fingerprint({k:v for k,v in s.items() if k!='source_row'})[:12]
            patch=PATCH.match(title);trial=TRIAL.search(title)
            patch_label=patch.group(1) if patch else ''
            patch_language='English' if patch_label.upper().startswith('ENGLISH') else 'Chinese' if patch else 'Not specified'
            entry={
                'id':eid,'source_row':s['source_row'],'source_title':title,'source_japanese_title':s['JPTitle'],
                'source_filename':s['ZIPName'],'source_platform':s['Emulator'],'source_variant_text':s['Variants'],
                'variant_labels':[v.strip() for v in s['Variants'].split(',') if v.strip()],
                'patch_label':patch_label,'patch_language':patch_language,'trial_label':(trial.group(1) or trial.group(2)) if trial else '',
                'sd_data_listed':s['sd_data_listed'],'website_exact_name_match':public_names[title]>0,
                'package_inspected':False,'runtime_tested':False,
            }
            group=grouped.setdefault(base.casefold(),{'id':rid,'title':base,'japanese_titles':[],'aliases':[],'entries':[]})
            if s['JPTitle'] and not PATCH.match(s['JPTitle']) and s['JPTitle'] not in group['japanese_titles']:
                group['japanese_titles'].append(s['JPTitle'])
            if title not in group['aliases']:group['aliases'].append(title)
            group['entries'].append(entry)
        audit.append({'source_row':s['source_row'],'source_title':s['ENTitle'],'source_platform':s['Emulator'],'included':included,'record_id':rid if included else '', 'entry_id':eid if included else ''})
    records=sorted(grouped.values(),key=lambda r:r['title'].casefold())
    for r in records:
        r['entries'].sort(key=lambda e:(bool(e['patch_label']),bool(e['trial_label']),e['source_title'].casefold()))
    date=date or datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
    metadata={
        'schema_version':1,'title':'DoJa / The Lost Catalog','repository':'https://github.com/Wakkatobakka/doja-archive',
        'site_url':'https://wakkatobakka.github.io/doja-archive/','snapshot_date':date,
        'sources':[
            {'id':'kwl-gamelist','name':'Keitai World Launcher public game list','url':SOURCE,'encoding':encoding,'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},
            {'id':'keitai-search','name':'Keitai Archive public search data','url':CSV_SOURCE,'encoding':csv_encoding,'size_bytes':len(raw_csv),'sha256':hashlib.sha256(raw_csv).hexdigest()},
        ],
        'counts':{
            'source_game_list_entries':len(source),'source_platform_labels':dict(sorted(collections.Counter(s['Emulator'] for s in source).items())),
            'included_doja_entries':len(selected),'grouped_catalog_records':len(records),
            'english_patch_entries':sum(bool(e['patch_label']) and e['patch_language']=='English' for r in records for e in r['entries']),
            'chinese_patch_entries':sum(e['patch_language']=='Chinese' for r in records for e in r['entries']),
            'trial_labeled_entries':sum(bool(e['trial_label']) for r in records for e in r['entries']),
            'entries_with_sd_data_reference':sum(e['sd_data_listed'] for r in records for e in r['entries']),
            'entries_with_variant_labels':sum(bool(e['variant_labels']) for r in records for e in r['entries']),
            'entries_with_exact_website_name_match':sum(e['website_exact_name_match'] for r in records for e in r['entries']),
            'website_all_media_entries':len(website),
        },
        'grouping_rules':{'strip_patch_prefixes':['ENGLISH PATCH','ENGLISH PATCH-Delocalized','ENGLISH PATCH-Localized','CHINESE PATCH'],'strip_trial_suffixes':['Trial','Preinstalled Trial','30 Second Trial','Demo','Trial Version','Demo Version'],'explicit_title_aliases':ALIASES,'note':'Catalog records group display-name variants, not verified byte-identical or interchangeable packages. Other suffixes and title differences remain distinct.'},
        'records':records,
    }
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/catalog.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'data/classification.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
    print(json.dumps(metadata['counts'],ensure_ascii=False,indent=2))
    return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gamelist',required=True,type=Path);p.add_argument('--website-csv',required=True,type=Path);p.add_argument('--date')
    a=p.parse_args();ingest(a.gamelist,a.website_csv,a.date)
