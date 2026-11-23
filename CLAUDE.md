## Project
SUU-themed flipbook for the SUU Head Start Preschool annual report, hosted on GitHub Pages (https://nathanwiggins.github.io/headstart-annualreport/). Forked from the SPARC annual report flipbook (`../../sparc/annualreport`) with the intro animation removed: the book opens straight to the cover. Whatever single PDF is in `report/` becomes the book. Vanilla HTML/CSS/ES modules, no framework and no JS build step; the only build is PDF → images, done by `scripts/build_pages.py` (locally via `scripts/preview.sh`, in CI via `.github/workflows/deploy.yml` on push to `main`).

## Files
- `report/`: the one PDF plus `config.json` (title, year, download name, outro title, `sectionStrikes`, `sections`, `addBackCover`). The only thing that changes year to year.
- `scripts/build_pages.py`: writes `book/` (page images `pages/md|lg`, `thumbs/`, `manifest.json`, `search.json` with word boxes, `og.jpg`, `report.pdf`). With `addBackCover` it appends a plain back cover from `scripts/back_cover.py` to the book (not to `report.pdf`); `manifest.pdfPages` is the real PDF's count, and `zoom.js` only asks PDF.js for pages up to it. `--site _site` copies the shell too and rewrites the `<!-- meta:start -->…<!-- meta:end -->` block in `index.html` with real title and link-preview tags.
- `index.html`: markup shell only; every panel is filled in by its JS module.
- `css/theme.css` tokens and shared bits (icon buttons, loader, toast, lightning) · `book.css` reader, pages, outro · `nav.css` dock, scrubber, filmstrip, search panel, zoom.
- `js/main.js`: boot, deep links (`#p=N`).
- `js/book.js`: wraps StPageFlip. Book pages ≠ PDF pages (blank page padded before the back cover when the count is odd); use `bookOf()` / `pdfAt()`. Emits `change` (`cause`: `flip` | `riffle` | `layout`), `layout`, `flipstart`.
- `js/nav.js` dock + keyboard + wheel · `search.js` (uses `book/search.json`, not PDF.js) · `zoom.js` (lazy-loads PDF.js for sharp zoom; falls back to the `lg` image) · `outro.js` (end card with the Thunderbird strike; section strikes when `sectionStrikes` is on) · `lightning.js` · `sound.js` (Web Audio synth, off by default) · `icons.js` · `util.js`.
- `assets/headstart-logo.png`: top-bar lockup (red SUU from the SPARC lockup + "Head Start Preschool" in Merriweather Bold).
- `vendor/`: page-flip 2.0.7 and pdfjs-dist 4.10.38. PDF.js files are renamed `.mjs` → `.js` so `python3 -m http.server` serves them with a JavaScript MIME type.
- `book/`, `_site/`: build output, gitignored.

## Gotchas
- Sections (scrubber ticks and preview names) come from `sections` in `report/config.json` (`page` = PDF page, not the printed number); the PDF's top-level bookmarks are only a fallback.
- StPageFlip rewrites each `.page` element's inline style (`cssText`), so never put inline styles on `.page`; style or fill its children instead (see `.pg-thumb`).
- State classes on `<body>` (`booting`, `reader-in`, `reading`, `zooming`, …) must not reuse an element's class name: when it was `body.backdrop`, the `.backdrop` rules gave `<body>` a full-screen `::after` that sat over the book and swallowed every click and touch on it.
- Page drags are book.js's, not StPageFlip's (`useMouseEvents: false`): `wireDrag()` feeds pointer events to `startUserTouch`/`userMove`/`userStop`, decides the let-go itself, and overrides the flip controller's `getDirectionByPoint`. Those are StPageFlip internals, so recheck them if `vendor/page-flip` is ever upgraded.
- StPageFlip can't switch one-up ↔ two-up in place; `book.js build()` destroys and rebuilds it on the current page. Portrait is forced with a huge `minWidth`; CSS overrides the inline min sizes it writes.
- The deployed site is only `main`. Past years live on their own branches (`2025-2026`, …).

## Style
SUU branding from the SPARC flipbook: SUU red `#DB0000`, dotted paper, mono uppercase eyebrows, serif display headings, SVG lightning that jolts the Thunderbird logo on the end card. The Head Start lockup leads in the top bar.
