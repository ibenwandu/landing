# ibenwandu.com

Personal landing page — static site on GitHub Pages.

- `index.html` — the page (editorial layout: hero, credentials, index of work, method,
  contact). No build step; styles are inline, fonts from Google Fonts.
- `scripts/update_tsa_pane.py` + `.github/workflows/tsa-refresh.yml` — **dormant.** They
  refreshed a live TradeSignal Africa pane between `TSA:START` / `TSA:END` markers. The
  2026-10 redesign removed that pane and its markers, so the script raises if run. The
  workflow is disabled on GitHub; do not re-enable it without restoring the markers.
- `assets/` — headshot, chat QR, cockpit graphic (not used by the current page).

## Local dev
Open `index.html` in a browser, or `python -m http.server 8765` and visit
`http://localhost:8765/`.
