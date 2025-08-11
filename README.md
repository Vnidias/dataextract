# scrapping-linkedin 🔎💼

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Requests](https://img.shields.io/badge/requests-%E2%9C%93-lightgrey)
![dateutil](https://img.shields.io/badge/python--dateutil-%E2%9C%93-lightgrey)
![OS](https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-OK-success)

Scrape **LinkedIn Jobs** through **ScrapingDog** for the Netherlands and export results to **JSON** and **CSV**. Includes a **description fetch** step (via job overview) and a **July 2025 filter**.

> **Zero BS goal:** new users should be able to run this in minutes without leaking secrets.

---

## ✨ What you get

* 🇳🇱 Focus on the **Netherlands** (`geoId = 102890719`).
* 🔁 Auto-pagination until the API returns an empty page.
* 📝 Job **descriptions** pulled via the **overview** endpoint (per `job_id`).
* 📅 **July 2025** filter (01–31 inclusive) baked-in (one script) and a **tiny 2‑job test** script.
* 🧯 Rate‑limit safe (exponential backoff + jitter; honors `Retry-After`).
* 🧰 Clean outputs:

  * `li_jobs_2025-07_with_desc.json`
  * `li_jobs_2025-07_with_desc.csv`
  * (test) `li_jobs_sample_with_desc.json` / `.csv`

---

## 🗂️ Repo contents

```
.
├─ li_july_2025_with_desc.py       # Full July-only run, no artificial cap
├─ li_test_2_jobs_with_desc.py     # Minimal sanity test (2 jobs) with descriptions
├─ requirements.txt                # requests + python-dateutil
├─ .gitignore                      # ignores __pycache__, outputs, .env, etc.
├─ .env.example                    # template for your key (not auto-loaded)
└─ README.md                       # this file
```

---

## ✅ Prerequisites

* **Python 3.10+** installed and on PATH (`python --version`).
* A **ScrapingDog API key** with the LinkedIn Jobs feature enabled.
* Basic terminal usage (PowerShell on Windows / bash on macOS/Linux).

> We **do not** auto-read `.env`. Set environment variables in your shell (examples below). `.env.example` is just a template you can copy from.

---

## 🚀 Quick start

### Windows (PowerShell)

```powershell
# 1) Get deps
python -m pip install -r requirements.txt

# 2) Set env vars for this session
$env:SCRAPINGDOG_API_KEY = "YOUR_KEY"
$env:FIELD = "data engineer"        # keywords
# Optional filters to narrow results (all are optional):
# $env:LOCATION = "Amsterdam"
# $env:SORT_BY  = "month"            # "day" | "week" | "month" | "" (empty)
# $env:JOB_TYPE = "full_time"        # temporary|contract|volunteer|full_time|part_time
# $env:EXP_LEVEL = "associate"       # internship|entry_level|associate|mid_senior_level|director
# $env:WORK_TYPE = "hybrid"          # at_work|remote|hybrid
# $env:FILTER_BY_COMPANY = "123456"  # LinkedIn company ID

# 3) Sanity test (fetch 2 jobs + descriptions)
python .\li_test_2_jobs_with_desc.py

# 4) Full July run (fetch descriptions only for July 2025)
python .\li_july_2025_with_desc.py
```

### macOS / Linux (bash/zsh)

```bash
# 1) Get deps
python3 -m pip install -r requirements.txt

# 2) Set env vars for this shell session
export SCRAPINGDOG_API_KEY="YOUR_KEY"
export FIELD="data engineer"
# Optional filters:
# export LOCATION="Amsterdam"
# export SORT_BY="month"
# export JOB_TYPE="full_time"
# export EXP_LEVEL="associate"
# export WORK_TYPE="hybrid"
# export FILTER_BY_COMPANY="123456"

# 3) Sanity test
python3 li_test_2_jobs_with_desc.py

# 4) Full July run
python3 li_july_2025_with_desc.py
```

> **Pro tip (Windows):** to persist the key across new shells, use `setx` once: `setx SCRAPINGDOG_API_KEY "YOUR_KEY"` (applies to *new* PowerShell windows).

---

## ⚙️ Configuration (env vars)

| Variable              | Required | Example                  | What it does                                                  |              |           |                    |              |
| --------------------- | -------- | ------------------------ | ------------------------------------------------------------- | ------------ | --------- | ------------------ | ------------ |
| `SCRAPINGDOG_API_KEY` | ✅        | `sk_live_...`            | Auth token for ScrapingDog.                                   |              |           |                    |              |
| `FIELD`               | ✅        | `data engineer`          | Keywords / title to search for.                               |              |           |                    |              |
| `GEOID`               | ❌        | `102890719`              | LinkedIn **geoId** for country/region. Default = Netherlands. |              |           |                    |              |
| `LOCATION`            | ❌        | `Amsterdam`              | Free-text location (pairs with geoId).                        |              |           |                    |              |
| `SORT_BY`             | ❌        | `day` / `week` / `month` | Relative time window (LinkedIn’s sort filter).                |              |           |                    |              |
| `JOB_TYPE`            | ❌        | `full_time`              | \`temporary                                                   | contract     | volunteer | full\_time         | part\_time\` |
| `EXP_LEVEL`           | ❌        | `associate`              | \`internship                                                  | entry\_level | associate | mid\_senior\_level | director\`   |
| `WORK_TYPE`           | ❌        | `remote`                 | \`at\_work                                                    | remote       | hybrid\`  |                    |              |
| `FILTER_BY_COMPANY`   | ❌        | `123456`                 | LinkedIn company ID to include only that company’s jobs.      |              |           |                    |              |
| `BASE_DELAY`          | ❌        | `1.0`                    | Seconds between list pages (to avoid 429).                    |              |           |                    |              |
| `OV_DELAY`            | ❌        | `0.6`                    | Seconds between overview (description) calls.                 |              |           |                    |              |

> If you don’t know your `geoId` for a city, leaving `GEOID` at NL and setting `LOCATION="CityName"` works well.

---

## 🧠 How it works

1. **List phase** → Calls `https://api.scrapingdog.com/linkedinjobs` with your query and paging (`page=1,2,3...`).
2. **Filter phase** → Checks `job_posting_date` for **July 2025**.
3. **Overview phase** → For July hits only, calls the **same endpoint** with `job_id` to retrieve the **full description**.
4. **Export** → Writes July-only **JSON** and **CSV**.

This two‑pass approach keeps API usage efficient: **no overview calls** for non‑July items.

---

## 📤 Outputs

* `li_jobs_2025-07_with_desc.json` → structured objects with `job_id`, `job_position`, `company_name`, `job_location`, `job_link`, `job_posting_date`, `description`.
* `li_jobs_2025-07_with_desc.csv` → same data as CSV.
* (Test) `li_jobs_sample_with_desc.json` / `.csv` → 2‑job sample with descriptions.

> Files are **git‑ignored** by default so you don’t accidentally commit data dumps.

---

## 🧪 Troubleshooting

**429 Too Many Requests**

* You’re rate‑limited. Increase `BASE_DELAY` and `OV_DELAY`. The scripts already honor `Retry-After`, but being gentler helps.

**Empty results**

* Try different `FIELD` (e.g., `python developer`, `software engineer`). Add `LOCATION` like `Amsterdam`.
* Set `SORT_BY="month"` to bias toward recent postings.

**Descriptions are empty**

* Some overview payloads vary. We extract from `description`/`job_description` and fall back to long string heuristics. If you find an odd case, open an issue with a redacted snippet and we’ll extend the parser.

**CSV error: “fields not in fieldnames”**

* We set `extrasaction="ignore"` in CSV writers to prevent this. If you build your own, keep fieldnames in sync.

**Windows: `export` not recognized**

* Use PowerShell syntax: `$env:NAME = "value"`. `export` is for bash.

---

## 🔒 Secrets & safety

* **Never** hardcode your API key in scripts or commit it to git. Use env vars.
* `.env.example` is a template; if you create a real `.env`, keep it **out of git** (already in `.gitignore`).
* Respect LinkedIn’s and ScrapingDog’s terms. Don’t go wild with parallelism.

---

## 🧾 Data schema (July exports)

```jsonc
{
  "job_id": "string",
  "job_position": "string",
  "company_name": "string",
  "job_location": "string",
  "job_link": "url",
  "job_posting_date": "YYYY-MM-DD",
  "description": "string (may be long)"
}
```

---

## 🛠️ Common recipes

**Amsterdam only**

```powershell
$env:LOCATION = "Amsterdam"
python .\li_july_2025_with_desc.py
```

**Hybrid roles only, last 30 days**

```powershell
$env:WORK_TYPE = "hybrid"
$env:SORT_BY = "month"
python .\li_july_2025_with_desc.py
```

**Company‑specific crawl**

```powershell
$env:FILTER_BY_COMPANY = "123456"
python .\li_july_2025_with_desc.py
```

---

## 🤖 Optional: GitHub Actions (manual run)

> Store your key as a **GitHub Secret** named `SCRAPINGDOG_API_KEY`.

```yaml
name: linkedin-july-scrape
on:
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - env:
          SCRAPINGDOG_API_KEY: ${{ secrets.SCRAPINGDOG_API_KEY }}
          FIELD: data engineer
          LOCATION: Amsterdam
        run: |
          python li_july_2025_with_desc.py
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: linkedin-july-outputs
          path: |
            li_jobs_2025-07_with_desc.json
            li_jobs_2025-07_with_desc.csv
```

---

## 🤝 Contributing

* Fork → branch → PR. Keep scripts **idempotent**, add **docstrings**, and avoid breaking env‑var defaults.
* If you change output fields, update this README and add a short schema note.

---

## 📜 License

Choose a license (MIT/Apache‑2.0). Add a `LICENSE` file. If you’re unsure, MIT is a good default for scripts.

---

## 📣 Credits

* [ScrapingDog – LinkedIn Jobs](https://docs.scrapingdog.com/linkedin-jobs-scraper/scrape-linkedin-jobs)
* [ScrapingDog – Job Overview](https://docs.scrapingdog.com/linkedin-jobs-scraper/scrape-linkedin-job-overview)

---

## 🧭 Roadmap

* [ ] Multi‑keyword batch runner (merge + dedupe by `job_id`).
* [ ] Optional export to PostgreSQL / S3.
* [ ] Unit tests for overview parsers (schema drift).
* [ ] Simple dashboard (Streamlit) to browse results.
