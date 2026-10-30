#!/usr/bin/env python3
"""Explicitly refresh the two public METADATA files, then rebuild the site."""
from pathlib import Path
from urllib.request import Request,urlopen
import subprocess,sys
from import_catalog import SOURCE,CSV_SOURCE,ingest
ROOT=Path(__file__).resolve().parents[1]
cache=ROOT/'.source-cache';cache.mkdir(exist_ok=True)
for name,url in [('gamelist.xml',SOURCE),('website-catalog.csv',CSV_SOURCE)]:
    request=Request(url,headers={'User-Agent':'Wakka-DoJa-Catalog/1.0'})
    with urlopen(request,timeout=45) as response:
        raw=response.read(8*1024*1024+1)
        if len(raw)>8*1024*1024:raise ValueError('Unexpectedly large metadata response; inspect source before updating.')
    (cache/name).write_bytes(raw)
ingest(cache/'gamelist.xml',cache/'website-catalog.csv')
subprocess.run([sys.executable,str(ROOT/'tools/build_site.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/verify.py')],check=True)
