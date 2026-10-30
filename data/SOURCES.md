# Source register

Reviewed **2026-10-30** (America/Chicago).

## Primary metadata snapshots

| Source | URL | Encoding | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Keitai World Launcher public game list | http://cdn.keitaiarchive.org:9000/kwl/gamelist.xml | cp932 | 1,140,357 | `66ff3e6cf95ea907feba4203884b79c54651e092c3c52ba732bd126c673c9289` |
| Keitai Archive public search data | https://keitaiarchive.org/searchable_media.csv | cp932 | 138,627 | `8c1f0aac76e79718e961aa3117c91771f205f033e1997c2afeb1f1d4342d84db` |

The public launcher game list is the authoritative runtime classifier for this snapshot. It has 2,818 application/media entries: 2,149 labeled `doja`, 61 `star`, 259 `softbank`, 125 `flash`, 100 `vodafone`, 58 `jsky`, 36 `ezplus`, and 30 `airedge`. Only `doja` entries enter this catalog.

The website CSV contains 3,125 rows across applications and other media. Of the included DoJa entries, 2,117 match a website name exactly. The other 32 have exact-string differences; these are not treated as absent or unpreserved games. The launcher titles are retained.

## How the metadata endpoint was identified

- [Official Keitai Archive launcher download page](https://keitaiarchive.org/downloads.html).
- [Official launcher ZIP](https://keitaiarchive.org/KeitaiWorldLauncher.zip), `configs/appconfig.xml`, whose `GamelistURL` points to the XML endpoint above. Configuration bytes were read from the ZIP with HTTP range requests; no executables were extracted or run. The ZIP was 336,540,548 bytes at inspection and its server Last-Modified header was October 28, 2026. That header is an observation, not a game release date.
- [Keitai World Launcher source](https://github.com/Yuvi-App/Keitai-World-Launcher), including the public Game model and XML-list manager. The inspected source-tree commit was `7d0cd74a44345ec04e3019368cefd3a81c0a6d9f`. Repository sample configs are placeholders; the published launcher config supplied the live metadata address.
- [Keitai Archive search interface](https://keitaiarchive.org/search.html), whose source loads `searchable_media.csv`. The live data decodes strictly as CP932; the new site exports UTF-8.

## Context and preservation credits

- [Keitai Archive](https://keitaiarchive.org/) — the source community and its preservation project.
- [Keitai World Launcher](https://keitaiarchive.org/downloads.html) — access to the source software catalog and its emulator setup.
- [Keitai Wiki](https://keitaiwiki.com/) — broader documentation.
- [Keitai Archive resources](https://keitaiarchive.org/resources.html) — distinguishes DoJa from STAR and links other preservation tools.
- [Yuvi: The Story to Save a Couple of Lost Keitai Games](https://medium.com/@yuviapp/the-story-to-save-a-couple-of-lost-keitai-games-1be4ede27c75), August 3, 2026 — firsthand account of restoring the full Dirge of Cerberus: Lost Episode release; credits Naoya Shinota and other contributors.
- [Dirge Bridge](https://github.com/Wakkatobakka/Dirge-Bridge) — Wakka's separate downstream Android bridge, linked from the featured record.

Original preservation, translation, and emulator credits stay with the source projects and their contributors. The metadata does not give full per-entry contributor attribution; missing names are not invented.

## Evidence boundaries

- Catalog titles are applications as classified by the source, including games, utilities, and other software. These are not counts of distinct retail games or every historical DoJa release.
- A `doja` source label is recorded as source evidence. No binary API inspection was performed.
- Original package and SD-data URLs were not followed. No game packages, SDKs, source artwork, or source screenshots are hosted here.
- Source filenames and variant labels identify entries. They do not establish package integrity, exact SDK requirements, language of unmarked entries, completeness, or compatibility.
- An SD-data URL records a separate source reference. It is not a tested requirement; a blank field does not establish that extra data is unnecessary.
- Grouping recognizes documented patch/trial title patterns and one display-name alias. It does not establish that files are interchangeable.
- No publisher, release-year, translator, runtime-test, or package-integrity facts are inferred where the metadata does not supply evidence.
- Metadata hashes identify the two source snapshots, not game files.
- Source websites may change or remove material; this catalog does not override their current availability policies.
