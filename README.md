# SUU Head Start Annual Report flipbook

An SUU-themed flipbook for the SUU Head Start Preschool annual report. Drop a PDF into `report/`, push to `main`, and GitHub Pages serves it at **https://nathanwiggins.github.io/headstart-annualreport/**. The book opens straight to the cover, pages turn like paper, and a bolt strikes the SUU logo on the end card.

Built from the [SPARC annual report flipbook](https://github.com/nathanwiggins/annualreport) without its intro animation.

## Swap in a new report

1. Replace the PDF in `report/` (keep exactly one PDF there).
2. Update `report/config.json` (title, year, download file name, sections).
3. Push to `main`. The GitHub Action renders the pages and publishes the site in a couple of minutes.

The PDF's **first page is the front cover** and its **last page is the back cover**, unless `addBackCover` is on: then the last page stays an inside page and the flipbook adds a plain SUU back cover after it (Download still gives the original PDF). If the page count is odd, a blank page is added before the back cover so spreads line up. Each **section** gets a tick on the scrubber and its name in the scrubber preview. Sections come from `sections` in `report/config.json`. Without that list, the PDF's top-level bookmarks are used instead.

### `report/config.json`

| Field | Used for |
|---|---|
| `title`, `year` | Browser tab, top bar, end card, link previews |
| `shortName`, `organization`, `university` | Eyebrow labels, end card |
| `description` | Link-preview text |
| `downloadName` | File name when someone downloads the PDF |
| `outroTitle` | Heading on the end card |
| `sectionStrikes` | `true` adds a small lightning strike and a name chip when a reader reaches a section (off here) |
| `addBackCover` | `true` when the PDF has no back cover: adds one (`scripts/back_cover.py`) after the last page |
| `sections` | `[{ "title": "Enrollment", "page": 5 }, …]`. `page` is the PDF page as a PDF viewer counts it (cover = 1), not the number printed on the page. |

## Preview locally

```sh
pip install pymupdf pillow
scripts/preview.sh          # then open http://localhost:8000
```

## QR code

`assets/qr-code.svg` (vector, for print) and `assets/qr-code.png` (1568 px) link to the site, in the same style as the SPARC report's code: ink dots, SUU-red corners, and the Thunderbird in the middle. To rebuild them, for example for a new URL:

```sh
pip install segno pymupdf pillow
python3 scripts/make_qr.py                    # or: --url https://…  --title "…"
```

## One-time GitHub setup

Settings → Pages → Build and deployment → Source: **GitHub Actions**.

## Past years

Each year is kept on its own branch. At year end, freeze the current report, then swap the PDF on `main`:

```sh
git branch 2025-2026 && git push origin 2025-2026
```

Only `main` is published. To look at an older year, check out its branch and run `scripts/preview.sh`.

## For readers

- **Turn pages:** click or drag a page corner, swipe, use ← →, or scroll over the book.
- **Bottom bar:** drag the scrubber (it previews pages as you go), open thumbnails (T), search (/), zoom (Z), copy a link to the current page, toggle sound, go fullscreen (F), download the PDF. Click the page counter to type a page number.
- **Links:** `…/headstart-annualreport/#p=5` opens straight to page 5.
