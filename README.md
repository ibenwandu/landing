# ibenwandu.com

Personal landing page — static site on GitHub Pages.

- `index.html` — the page (hero + project grid). No build step.
- `scripts/update_tsa_pane.py` — refreshes the TradeSignal Africa pane from the
  public Telegram channel. Run by `.github/workflows/tsa-refresh.yml` (cron) and committed.
- `assets/` — headshot, chat QR, cockpit graphic.

## Local dev
Open `index.html` in a browser. To refresh the TSA pane locally:
`TSA_CHANNEL=<channel> python scripts/update_tsa_pane.py`
