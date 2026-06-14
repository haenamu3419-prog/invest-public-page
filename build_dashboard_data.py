#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공개용 대시보드 데이터 생성기 (GitHub Actions, 하루 4회)
========================================================
FRED(금리·유가·환율)만 조회해 dashboard_data.json 으로 저장한다.
공개용이라 보유종목·DART 공시는 포함하지 않는다.

환경변수(GitHub Secrets):
  FRED_API_KEY

출력: dashboard_data.json
"""

import os
import json
import datetime

import requests

KST = datetime.timezone(datetime.timedelta(hours=9))
OUT = "dashboard_data.json"

MACRO = [
    ("DGS30", "미국채 30년물", "pct"),
    ("DGS10", "미국채 10년물", "pct"),
    ("DGS2",  "미국채 2년물",  "pct"),
    ("DFF",   "연준 기준금리", "pct"),
    ("DCOILWTICO",   "WTI 유가", "usd"),
    ("DCOILBRENTEU", "브렌트유",  "usd"),
    ("DEXKOUS", "원/달러", "won"),
    ("VIXCLS",  "VIX",    "pt"),
]


def fred_latest2(series_id):
    r = requests.get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={"series_id": series_id, "api_key": os.environ["FRED_API_KEY"],
                "file_type": "json", "sort_order": "desc", "limit": 12},
        timeout=20)
    r.raise_for_status()
    out = []
    for o in r.json().get("observations", []):
        v = o.get("value", ".")
        if v not in (".", "", None):
            try: out.append(float(v))
            except ValueError: pass
        if len(out) >= 2:
            break
    return out


def build_macro():
    rows = []
    for sid, name, unit in MACRO:
        try:
            d = fred_latest2(sid)
            cur = d[0] if d else None
            prev = d[1] if len(d) >= 2 else None
            rows.append({"name": name, "unit": unit, "cur": cur, "prev": prev})
        except Exception as e:
            rows.append({"name": name, "unit": unit, "cur": None, "prev": None, "err": str(e)})
    return rows


def main():
    data = {
        "updated": datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
        "macro": build_macro(),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK {OUT} 저장: 금리 {len(data['macro'])}항목")


if __name__ == "__main__":
    main()
