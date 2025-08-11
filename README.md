# scrapping-linkedin

LinkedIn job scraper using ScrapingDog. Focus: Netherlands (geoId `102890719`), July 2025 filter, and per-job description via overview calls.

## Scripts
- `li_test_2_jobs_with_desc.py` – sanity test (fetch 2 jobs + descriptions).
- `li_july_2025_with_desc.py` – full run: pages until empty, fetches descriptions only for July 2025.

## Setup
```bash
pip install -r requirements.txt
