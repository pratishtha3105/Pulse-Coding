Review Scraper

Small CLI tool to scrape product reviews from review sites (Capterra, G2).

**Requirements:** Python 3.10+ (venv recommended)

**Install**

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

**Usage**

Run the CLI with required flags:

```powershell
python scrape_reviews.py --company <company_id_or_slug> --source capterra|g2 --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```

Examples:

```powershell
python scrape_reviews.py --company 17415 --source capterra --start_date 2023-01-01 --end_date 2025-01-01
python scrape_reviews.py --company HubSpot --source capterra --start_date 2023-01-01 --end_date 2025-01-01
```

Output: JSON file named `reviews_<company>_<source>.json` in the working directory.

**Notes / Troubleshooting**
- The Capterra pages are heavily client-side (Next.js). The Capterra scraper uses Selenium and webdriver-manager.
- If the scraper cannot find reviews it saves a debug HTML snapshot: `debug_capterra_<company>.html`.
- If your `--company` value contains `/`, filenames are sanitized (slashes become underscores).
- To reduce detection, the scraper runs Chrome in headless mode with a browser-like user-agent. You may remove headless flags for debugging.
- If you get `ModuleNotFoundError: No module named 'selenium'`, ensure you installed `requirements.txt` into the active venv.

**What I changed (local branch)**
- Improved `scrapers/capterra.py` to poll multiple selectors, add scrolling, save debug HTML when pages fail to load, and sanitize filenames.
- Sanitized output filename handling in `scrape_reviews.py`.

**Pushing to GitHub**
- Changes have been pushed to branch `update/capterra-fix` on https://github.com/pratishtha3105/Pulse-Coding.

**Next steps**
- Provide exact Capterra product slug if scraping a specific product fails (e.g., `HubSpot-Marketing-Hub`).
- Add retry/backoff, per-site rate limiting, and optional headful mode for debugging.

---
Created/updated by automation in workspace.

