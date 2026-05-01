"""
可轉債篩選工具
資料來源：
  - CB 資料：cbas16889.pscnet.com.tw API（無需 auth）
  - 股票現價：FinMind API（需 FINMIND_TOKEN 環境變數）
篩選條件：個股現價在轉換價格 ±5% 內
"""

import warnings
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

CBAS_BASE = "https://cbas16889.pscnet.com.tw/api/CbasQuote"
FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"
THRESHOLD = 0.05  # ±5%

CBAS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://cbas16889.pscnet.com.tw/",
}


def fetch_cbas(endpoint: str) -> list[dict]:
    r = requests.get(f"{CBAS_BASE}/{endpoint}", headers=CBAS_HEADERS, verify=False, timeout=20)
    r.raise_for_status()
    return r.json()["result"]


def fetch_stock_prices(token: str) -> tuple[str, dict[str, float]]:
    d = datetime.today()
    for _ in range(10):
        if d.weekday() < 5:
            date_str = d.strftime("%Y-%m-%d")
            r = requests.get(
                FINMIND_URL,
                params={"dataset": "TaiwanStockPrice", "start_date": date_str, "token": token},
                timeout=60,
            )
            r.raise_for_status()
            records = r.json().get("data", [])
            if records:
                price_map = {rec["stock_id"]: float(rec["close"]) for rec in records if rec.get("close") is not None}
                return date_str, price_map
        d -= timedelta(days=1)
    raise RuntimeError("找不到近期有效交易日資料")


def filter_convertible_bonds():
    token = os.getenv("FINMIND_TOKEN")
    if not token:
        token_file = Path(__file__).parent / "token"
        if token_file.exists():
            token = token_file.read_text().strip().split()[-1]
    if not token:
        raise ValueError("請設定環境變數 FINMIND_TOKEN 或在 python/token 放置 token 檔案")

    # ── 抓取資料 ──
    print("抓取 CBAS 資料...")
    issued_raw = fetch_cbas("GetIssuedCBSchedule")
    listed_raw = fetch_cbas("GetRecentlyListed")
    print(f"  已發行CB {len(issued_raw)} 筆 / 近期上市 {len(listed_raw)} 筆")

    print("抓取股票現價...")
    price_date, price_map = fetch_stock_prices(token)
    print(f"  股價日期：{price_date}，共 {len(price_map)} 支")

    # ── 整理資料 ──
    rows = []

    for r in issued_raw:
        cp = r.get("conversion_price")
        sc = r.get("convert_target_code")
        if not cp or not sc:
            continue
        try:
            cp = float(cp)
        except (ValueError, TypeError):
            continue
        price = price_map.get(sc)
        if price is None:
            continue
        gap = (price - cp) / cp * 100
        if abs(gap) > THRESHOLD * 100:
            continue
        rows.append({
            "CB代號": r.get("bond_code", ""),
            "CB名稱": r.get("underlying_bond", ""),
            "個股現價": price,
            "轉換價格": cp,
            "餘額比例(%)": r.get("balance_ratio", ""),
            "距轉換價差距(%)": round(gap, 2),
            "已發行/近期上市": "已發行CB",
        })

    for r in listed_raw:
        cp = r.get("conversion_price")
        sc = r.get("code")
        if not cp or not sc:
            continue
        try:
            cp = float(cp)
        except (ValueError, TypeError):
            continue
        price = price_map.get(sc)
        if price is None:
            continue
        gap = (price - cp) / cp * 100
        if abs(gap) > THRESHOLD * 100:
            continue
        rows.append({
            "CB代號": r.get("cb_code", ""),
            "CB名稱": r.get("cb_name", ""),
            "個股現價": price,
            "轉換價格": cp,
            "餘額比例(%)": 100,
            "距轉換價差距(%)": round(gap, 2),
            "已發行/近期上市": "近期上市",
        })

    # ── 輸出 ──
    df = pd.DataFrame(rows, columns=[
        "CB代號", "CB名稱", "個股現價", "轉換價格",
        "餘額比例(%)", "距轉換價差距(%)", "已發行/近期上市",
    ])
    df = df.sort_values("距轉換價差距(%)", key=abs).reset_index(drop=True)

    print(f"\n篩選結果（±{int(THRESHOLD*100)}%，股價日期 {price_date}）：{len(df)} 筆")

    # 匯出到 latest
    latest_dir = Path("../public/data/latest") if Path("../public/data/latest").exists() else Path("public/data/latest")
    latest_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(latest_dir / "convertible-bonds.csv", index=False, encoding="utf-8-sig")
    print(f"已儲存：{latest_dir / 'convertible-bonds.csv'}")

    # 匯出到 history
    history_date = price_date.replace("-", "")
    history_dir = Path(f"../public/data/history/{history_date}") if Path("../public/data").exists() else Path(f"public/data/history/{history_date}")
    history_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(history_dir / "convertible-bonds.csv", index=False, encoding="utf-8-sig")
    print(f"已儲存：{history_dir / 'convertible-bonds.csv'}")

    return df


if __name__ == "__main__":
    filter_convertible_bonds()
