# Somalia (SO) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Constitutional texts and federal laws of the Federal Republic of Somalia, from the **document library of the
Federal Parliament of Somalia** (parliament.gov.so), in **Somali** (`so/`) and **English** (`en/`):

* the **Provisional Constitution of the Federal Republic of Somalia** (adopted 1 August 2012), in English and
  Somali, and, for reference, earlier constitutional texts (1949 trusteeship annex, 1960, 1979, 1990
  constitutions, 2004 Transitional Federal Charter) as published by the Parliament;
* the **laws** (*Sharciga …*, budget laws *Xeerka … Miisaaniyadda*) of the Federal Parliament that are published
  with a usable text layer.

Retrieved 2026-10-13. Status: **partial**.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `en/constitution/` | 4 |
| `en/laws/` | 2 |
| `so/constitution/` | 5 |
| `so/laws/` | 17 |
| **Total** | **28** |
<!-- /COUNTS -->

## Structure

```
en/constitution/<slug>.md      English constitutional texts
so/constitution/<slug>.md      Somali constitutional texts
so/laws/<slug>.md              laws (Somali)
en/laws/<slug>.md              laws whose published text is in English (ratification laws with an English treaty text)
```

File names are slugs of the titles in the Parliament's library. `status` is `in_force` for the 2012 Provisional
Constitution, `repealed` for earlier constitutions and `unknown` for laws.

## Sources

| Source | URL | Used for |
|---|---|---|
| Federal Parliament of Somalia — document library | https://parliament.gov.so/ (REST: `/wp-json/wp/v2/dlp_document`) | constitutions, laws |

## Not covered / known gaps

* **43 documents are scanned PDFs without a text layer** and were not converted (no Somali OCR model is
  available, and OCR was not attempted). They include many laws (e.g. the Fisheries Law, the Law on Districts and
  Regions, the laws establishing independent commissions, several budget laws). They are listed in the
  regeneration log.
* Amendments to the Provisional Constitution adopted in 2024 (revision of chapters 1–4) are not included: the
  Parliament's library publishes only the 2012 text.
* Motions, resolutions (*Qaraar*), treaties (*Heshiis*) and rules of procedure in the same library are not included.
* Laws of the Federal Member States and of Somaliland are out of scope.

## Copyright

Somali laws and constitutional texts are official public texts published by the Federal Parliament. The Markdown
conversion is provided as is, for information.

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt   # plus poppler (pdftotext)
python3 scripts/so_fetch.py        # cache in ../_raw/so
python3 scripts/so_readme.py
```
