# Catalog schema

`catalog.json` is canonical. `schema_version` is currently `1`.

| Top-level field | Meaning |
| --- | --- |
| `title`, `repository`, `site_url` | Site title and GitHub Pages identity |
| `snapshot_date` | Date the source metadata was reviewed; rebuilding does not change it |
| `sources` | Metadata URLs, byte sizes, encodings, and SHA-256 values |
| `counts` | Source runtime counts, included entries, grouped records, and label counts |
| `grouping_rules` | Recognized patch/trial title patterns and explicit display-name aliases |
| `records` | Grouped browsing records with their original source entries |

## Record fields

| Field | Meaning |
| --- | --- |
| `id` | ASCII title slug plus a hash of the case-folded grouping title |
| `title` | Grouping title, derived conservatively from source names |
| `japanese_titles` | Exact Japanese-title fields, excluding patch labels that merely repeat the English title |
| `aliases` | Every exact source English-title label in this group |
| `entries` | Original, trial, patch, or other retained source entries |

IDs remain stable for the same grouping title. A deliberate title correction can change the ID; maintain redirect pages if preserving already-published URLs is required.

## Source-entry fields

| Field | Meaning |
| --- | --- |
| `id` | Fingerprint of the retained entry metadata; excludes its positional source row |
| `source_row` | One-based entry position in the complete 2,818-row launcher snapshot |
| `source_title`, `source_japanese_title` | Exact source title fields |
| `source_filename` | Original ZIP label; metadata only |
| `source_platform` | Exact source runtime label; included entries must be `doja` |
| `source_variant_text`, `variant_labels` | Exact source variant field and its comma-separated labels |
| `patch_label` | A recognized explicit English/Chinese patch prefix, or blank |
| `patch_language` | `English`, `Chinese`, or `Not specified`; applies to a patch label, not a verified game-language test |
| `trial_label` | An explicit recognized trial/demo suffix, or blank |
| `sd_data_listed` | Whether the source lists a separate SD-data URL; no download or requirement test is implied |
| `website_exact_name_match` | Exact name match in the NTT Docomo/Application rows of the secondary website CSV |
| `package_inspected`, `runtime_tested` | Both `false` in this metadata-only catalog |

Original download URLs and app-icon URLs are omitted. Each page directs readers to Keitai Archive and Keitai World Launcher, with exact title labels to locate the original listing. The official website search does not provide a confirmed per-record deep link, so the site does not invent one.

## Grouping

Recognized leading labels are `[ENGLISH PATCH]`, `[CHINESE PATCH]`, and the source's English patch `-Delocalized` / `-Localized` variants. Recognized trial/demo suffixes are bracketed or parenthesized Trial, Preinstalled Trial, 30 Second Trial, Demo, Trial Version, and Demo Version, plus explicit unbracketed Trial Version / Demo Version endings. These are removed for grouping while the complete original title remains attached to the entry.

The sole explicit title alias maps `Final Fantasy VII Snowboarding` to `Final Fantasy 7 Snowboarding`. Other title differences, network/service labels, chapter names, and edition qualifiers remain distinct. Name grouping is a browsing aid and does not prove that releases are byte-identical or interchangeable.

## Exports and audit

`catalog.csv` has one row per grouped record. `entries.csv` has one row per included source entry. `classification.csv` includes every launcher source row and its include/exclude decision, so source runtime counts can be reconciled. The builder regenerates the first two CSVs. The importer generates the canonical JSON and classification audit together.

The interface substitutes ◇ for private-use carrier glyphs; the exact original code points remain in JSON and source-entry CSV. Japanese titles are not silently romanized or translated.
