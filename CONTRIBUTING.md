# Contribute a record or credit correction

Use the catalog issue form or a pull request. Include:

1. The catalog record ID or URL and exact Keitai World Launcher entry title.
2. The correction: a missing preservation/translation credit, edition distinction, title, runtime detail, or source reference.
3. A supporting primary reference and its review date. Clearly separate a documented source claim from a test you performed.

Do not upload game files, SDKs, phone firmware, original screenshots, or unrelated personal information. File evidence can be described using the original filename, byte size, checksum, and the location of the source evidence.

## Metadata edits

`data/catalog.json` is canonical. Pages and `catalog.csv` / `entries.csv` are generated. Keep source rows, the `classification.csv` audit, counts, and grouping rules consistent with any structural change. Run:

```sh
python3 tools/build_site.py
python3 tools/verify.py
```

Display-name grouping does not establish that two packages are identical or interchangeable. Do not merge editions solely because a modern game shares their name. Keep original source labels and filenames intact.

Patch tags describe the source's labels. An unmarked entry does not establish its language. A separate SD-data URL establishes a reference, not a verified runtime requirement. Source variant text such as “Patched” and “Non-Working” remains a source claim.

The present index records uninspected packages and untested runtime status. Adding inspected-file or gameplay evidence requires extending the schema and updating the public status copy, counts, and verifier together. Do not promote a record based on a filename or download button alone.

Wakka reviews contributions before publishing an updated site.
