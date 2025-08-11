#!/usr/bin/env python3
"""
LinkedIn Jobs via ScrapingDog — JULY 2025 only, no page/job limit.
- Pages until an empty page is returned.
- Fetches description (overview) ONLY for jobs dated in July 2025.
- Saves JSON + CSV.

Env vars (PowerShell examples below):
  SCRAPINGDOG_API_KEY  (required)
  FIELD                (default: "data engineer")
  GEOID                (default: "102890719" -> Netherlands)
  LOCATION             (optional; e.g., "Amsterdam")
  SORT_BY              (optional: "", "day", "week", "month")
  JOB_TYPE             (optional: temporary|contract|volunteer|full_time|part_time)
  EXP_LEVEL            (optional: internship|entry_level|associate|mid_senior_level|director)
  WORK_TYPE            (optional: at_work|remote|hybrid)
  FILTER_BY_COMPANY    (optional: LinkedIn company ID)
  BASE_DELAY           (default: 1.0 seconds between pages)
  OV_DELAY             (default: 0.6 seconds between overview calls)
"""

from __future__ import annotations
import csv, json, os, random, time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, timezone
import requests
from dateutil import parser as dtparser

API_KEY = os.getenv("SCRAPINGDOG_API_KEY", "")
ENDPOINT = "https://api.scrapingdog.com/linkedinjobs"

# Search scope
GEOID_NL  = os.getenv("GEOID", "102890719")         # Netherlands
FIELD     = os.getenv("FIELD", "data engineer")
LOCATION  = os.getenv("LOCATION", "")
SORT_BY   = os.getenv("SORT_BY", "")
JOB_TYPE  = os.getenv("JOB_TYPE", "")
EXP_LEVEL = os.getenv("EXP_LEVEL", "")
WORK_TYPE = os.getenv("WORK_TYPE", "")
FILTER_BY_COMPANY = os.getenv("FILTER_BY_COMPANY", "")

# Timing
TIMEOUT     = 30
BASE_DELAY  = float(os.getenv("BASE_DELAY", "1.0"))
OV_DELAY    = float(os.getenv("OV_DELAY", "0.6"))

# July 2025 window (inclusive)
WIN_START = date(2025, 7, 1)
WIN_END   = date(2025, 7, 31)

# Outputs
JULY_JSON = "li_jobs_2025-07_with_desc.json"
JULY_CSV  = "li_jobs_2025-07_with_desc.csv"

def _backoff_sleep(attempts: int, retry_after: Optional[str]) -> None:
    if retry_after:
        try:
            time.sleep(float(retry_after)); return
        except ValueError:
            pass
    time.sleep(min(60.0, (2 ** (attempts - 1))) + random.uniform(0.2, 0.9))

def fetch_list(page: int) -> List[Dict[str, Any]]:
    params = {
        "api_key": API_KEY,
        "field": FIELD,
        "geoid": GEOID_NL,
        "location": LOCATION,
        "page": str(page),
    }
    if SORT_BY: params["sort_by"] = SORT_BY
    if JOB_TYPE: params["job_type"] = JOB_TYPE
    if EXP_LEVEL: params["exp_level"] = EXP_LEVEL
    if WORK_TYPE: params["work_type"] = WORK_TYPE
    if FILTER_BY_COMPANY: params["filter_by_company"] = FILTER_BY_COMPANY

    attempts = 0
    while True:
        attempts += 1
        r = requests.get(ENDPOINT, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            try:
                data = r.json()
            except ValueError:
                data = []
            return data if isinstance(data, list) else []
        if r.status_code in (429, 500, 502, 503, 504):
            _backoff_sleep(attempts, r.headers.get("Retry-After"))
            continue
        # Non-retryable: return empty page to stop
        return []

def fetch_overview(job_id: str) -> Union[Dict[str, Any], List[Any]]:
    if not job_id:
        return {}
    params = {"api_key": API_KEY, "job_id": job_id}
    attempts = 0
    while True:
        attempts += 1
        r = requests.get(ENDPOINT, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            try:
                return r.json() or {}
            except ValueError:
                return {}
        if r.status_code in (429, 500, 502, 503, 504):
            _backoff_sleep(attempts, r.headers.get("Retry-After"))
            continue
        return {}

def _extract_description(overview: Union[Dict[str, Any], List[Any]]) -> str:
    # Accept dict or list-of-dicts; look for description-like fields
    ov: Dict[str, Any] = {}
    if isinstance(overview, list):
        for el in overview:
            if isinstance(el, dict):
                ov = el; break
    elif isinstance(overview, dict):
        ov = overview

    for key in ("description", "job_description", "full_description"):
        val = ov.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    for v in ov.values():
        if isinstance(v, str) and len(v.strip()) > 40:
            return v.strip()

    for v in ov.values():
        if isinstance(v, dict):
            for key in ("description", "job_description", "full_description"):
                val = v.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

    return ""

def in_july_2025(dstr: Optional[str]) -> bool:
    if not dstr: return False
    try:
        d = dtparser.parse(dstr).date()
    except Exception:
        return False
    return WIN_START <= d <= WIN_END

def main():
    if not API_KEY or len(API_KEY) < 10:
        raise SystemExit("Missing SCRAPINGDOG_API_KEY")

    july_rows: List[Dict[str, Any]] = []
    page = 1
    total_seen = 0
    total_july = 0
    total_overviews = 0

    while True:
        rows = fetch_list(page)
        if not rows:
            break

        for j in rows:
            total_seen += 1
            job_id = j.get("job_id", "")
            job_date = j.get("job_posting_date")

            if in_july_2025(job_date):
                ov = fetch_overview(job_id)
                desc = _extract_description(ov)
                total_overviews += 1 if ov else 0

                july_rows.append({
                    "job_id": job_id,
                    "job_position": j.get("job_position"),
                    "company_name": j.get("company_name"),
                    "company_profile": j.get("company_profile"),
                    "job_location": j.get("job_location"),
                    "job_link": j.get("job_link"),
                    "job_posting_date": job_date,
                    "description": desc,
                })
                total_july += 1

                time.sleep(OV_DELAY + random.uniform(0.1, 0.5))

        page += 1
        time.sleep(BASE_DELAY + random.uniform(0.2, 0.8))

    # Save JSON (July only)
    with open(JULY_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "geoid": GEOID_NL,
                "field": FIELD,
                "location": LOCATION or None,
                "sort_by": SORT_BY or None,
                "records_total_seen": total_seen,
                "records_in_july": total_july,
                "overviews_fetched": total_overviews,
                "window_start": WIN_START.isoformat(),
                "window_end": WIN_END.isoformat(),
            },
            "data": july_rows,
        }, f, ensure_ascii=False, indent=2)

    # Save CSV (July only)
    fieldnames = [
        "job_posting_date","job_position","company_name",
        "job_location","job_id","job_link","description"
    ]
    with open(JULY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in july_rows:
            w.writerow(r)

    print(f"Seen total listings: {total_seen}")
    print(f"July matches: {total_july} (overviews fetched: {total_overviews})")
    print(f"Saved JSON => {JULY_JSON}")
    print(f"Saved CSV  => {JULY_CSV}")

if __name__ == "__main__":
    main()
