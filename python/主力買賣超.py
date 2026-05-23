"""
主力買賣超篩選系統
每日抓取全市場券商分點買賣資料，計算主力買超指標，執行四種篩選
執行目錄：python/
"""
import requests
import pandas as pd
import time
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# ==================== 設定 ====================

try:
    with open('token', 'r') as f:
        TOKEN = f.read()
except FileNotFoundError:
    TOKEN = os.getenv('FINMIND_TOKEN', '')
TOKEN = re.sub(r'[\s\x00-\x1f\x7f]', '', TOKEN)

API_URL = "https://api.finmindtrade.com/api/v4/data"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

import argparse
_parser = argparse.ArgumentParser()
_parser.add_argument('--date', default=None, help='指定抓取日期 YYYY-MM-DD，預設為今日')
_args, _ = _parser.parse_known_args()
TODAY = _args.date if _args.date else datetime.now().strftime('%Y-%m-%d')
HISTORY_DIR = Path('../data/history')
LATEST_DIR = Path('../data/latest')
SLEEP_SEC = 0.65  # ~92 req/min，低於上限 100/min

# ==================== 函數 ====================

def fetch_trading_report(stock_id: str, date: str):
    params = {
        "dataset": "TaiwanStockTradingDailyReport",
        "data_id": stock_id,
        "start_date": date,
        "end_date": date,
    }
    try:
        resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and data.get('status', 200) == 200 and data.get('data'):
                return pd.DataFrame(data['data'])
    except Exception:
        pass
    return None


def calc_main_force(df: pd.DataFrame) -> int:
    agg = (
        df.groupby('securities_trader_id')
        .agg(buy=('buy', 'sum'), sell=('sell', 'sum'))
        .reset_index()
    )
    top15_buy  = agg.nlargest(15, 'buy')['buy'].sum()
    top15_sell = agg.nlargest(15, 'sell')['sell'].sum()
    return int((top15_buy - top15_sell) // 1000)


def load_history_dates(n: int = 4) -> list:
    """取最近 n 個已有原始資料的歷史日期（不含今日）"""
    dates = []
    if HISTORY_DIR.exists():
        for d in sorted(HISTORY_DIR.iterdir(), reverse=True):
            if d.is_dir() and d.name < TODAY and (d / '主力買賣超_raw.csv').exists():
                dates.append(d.name)
                if len(dates) >= n:
                    break
    return dates


def load_raw(date: str):
    f = HISTORY_DIR / date / '主力買賣超_raw.csv'
    return pd.read_csv(f) if f.exists() else None


def enrich(df: pd.DataFrame, stock_map: dict) -> pd.DataFrame:
    df = df.copy()
    df['公司名稱'] = df['stock_id'].map(lambda x: stock_map.get(x, {}).get('公司名稱', ''))
    df['公司產業'] = df['stock_id'].map(lambda x: stock_map.get(x, {}).get('公司產業', ''))
    df['上市櫃']  = df['stock_id'].map(lambda x: stock_map.get(x, {}).get('上市櫃', ''))
    df.rename(columns={'stock_id': '股票代碼'}, inplace=True)
    return df


def build_result(rows: list, stock_map: dict, extra_cols: list = None) -> pd.DataFrame:
    base_cols = ['排名', '股票代碼', '公司名稱', '公司產業', '上市櫃']
    value_cols = (extra_cols or []) + ['今日主力買超(張)', '5日累積買超(張)']
    if not rows:
        return pd.DataFrame(columns=base_cols + value_cols)
    df = enrich(pd.DataFrame(rows), stock_map)
    df = df.sort_values('5日累積買超(張)', ascending=False).reset_index(drop=True)
    df.insert(0, '排名', range(1, len(df) + 1))
    return df[base_cols + value_cols]


# ==================== 主程式 ====================

print('=== 主力買賣超分析 ===\n')
print(f'目標日期: {TODAY}')

# 讀取股票清單
print('讀取股票清單...')
stock_info = pd.read_csv('(all)stock_info_list.csv')
stock_info['股票代碼'] = stock_info['股票代碼'].astype(str).str.zfill(4)
stock_list = stock_info['股票代碼'].tolist()
stock_map = stock_info.set_index('股票代碼').to_dict('index')
print(f'共 {len(stock_list)} 檔股票\n')

# ---- 抓取今日資料 ----
print(f'開始抓取 {TODAY} 券商分點資料...')
print(f'預計耗時約 {len(stock_list) * SLEEP_SEC / 60:.0f} 分鐘\n')

rows = []
success = fail = empty = 0

for i, sid in enumerate(stock_list, 1):
    if i % 200 == 0:
        print(f'  進度 {i}/{len(stock_list)} ({i/len(stock_list)*100:.0f}%)')
    df_raw = fetch_trading_report(sid, TODAY)
    if df_raw is not None and len(df_raw) > 0:
        rows.append({'stock_id': sid, 'lots': calc_main_force(df_raw)})
        success += 1
    elif df_raw is not None:
        empty += 1
    else:
        fail += 1
    time.sleep(SLEEP_SEC)

print(f'\n抓取完成：成功 {success}，空資料 {empty}，失敗 {fail}')

if not rows:
    print('今日無資料（非交易日），結束執行')
    sys.exit(0)

today_df = pd.DataFrame(rows)  # columns: stock_id, lots

# ---- 儲存今日原始資料 ----
today_hist = HISTORY_DIR / TODAY
today_hist.mkdir(parents=True, exist_ok=True)
today_df.to_csv(today_hist / '主力買賣超_raw.csv', index=False)
print(f'今日原始資料已儲存：{today_hist / "主力買賣超_raw.csv"} ({len(today_df)} 筆)\n')

# ---- 合併最近 5 交易日 ----
hist_dates = load_history_dates(n=4)
all_frames = [today_df.assign(date=TODAY)]
for d in hist_dates:
    frame = load_raw(d)
    if frame is not None:
        all_frames.append(frame.assign(date=d))

combined = pd.concat(all_frames, ignore_index=True)
all_dates = sorted(combined['date'].unique(), reverse=True)
d5 = all_dates[:5]
d3 = all_dates[:3]
d2 = all_dates[:2]
print(f'使用日期（最近5日）: {d5}')

combined = combined[combined['date'].isin(d5)]
today_lots_map = today_df.set_index('stock_id')['lots'].to_dict()


def total_5d(sid: str) -> int:
    return int(combined[combined['stock_id'] == sid]['lots'].sum())


def base_row(sid: str) -> dict:
    return {
        'stock_id': sid,
        '今日主力買超(張)': today_lots_map.get(sid, 0),
        '5日累積買超(張)': total_5d(sid),
    }


# ---- 篩選 1：連續 3 天為正 ----
s1_3d = []
for sid, grp in combined.groupby('stock_id'):
    sub = grp[grp['date'].isin(d3)]
    if len(sub) == len(d3) and (sub['lots'] > 0).all():
        s1_3d.append(base_row(sid))
df_s1_3d = build_result(s1_3d, stock_map)
print(f'篩選1 連續3天: {len(df_s1_3d)} 檔')

# ---- 篩選 2：連續 5 天為正 ----
s1_5d = []
if len(d5) >= 5:
    for sid, grp in combined.groupby('stock_id'):
        sub = grp[grp['date'].isin(d5)]
        if len(sub) == 5 and (sub['lots'] > 0).all():
            s1_5d.append(base_row(sid))
df_s1_5d = build_result(s1_5d, stock_map)
print(f'篩選2 連續5天: {len(df_s1_5d)} 檔')

# ---- 篩選 3：5天 ≥ 3天正且近2天皆正 ----
s2 = []
for sid, grp in combined.groupby('stock_id'):
    sub5 = grp[grp['date'].isin(d5)]
    sub2 = grp[grp['date'].isin(d2)]
    pos_count = int((sub5['lots'] > 0).sum())
    last2_pos = len(sub2) == len(d2) and (sub2['lots'] > 0).all()
    if pos_count >= 3 and last2_pos:
        r = base_row(sid)
        r['5天正天數'] = pos_count
        s2.append(r)
df_s2 = build_result(s2, stock_map, extra_cols=['5天正天數'])
print(f'篩選3 5天≥3天: {len(df_s2)} 檔')

# ---- 篩選 4：5天累積排名 Top 50 ----
rank_rows = []
for sid, grp in combined.groupby('stock_id'):
    rank_rows.append({
        'stock_id': sid,
        '今日主力買超(張)': today_lots_map.get(sid, 0),
        '5日累積買超(張)': int(grp[grp['date'].isin(d5)]['lots'].sum()),
    })
df_rank = build_result(rank_rows, stock_map).head(50)
# 重新編排名（head 後序號不變，重設即可）
df_rank = df_rank.reset_index(drop=True)
df_rank['排名'] = range(1, len(df_rank) + 1)
print(f'篩選4 累積排名 Top50: {len(df_rank)} 檔')

# ---- 輸出 CSV ----
LATEST_DIR.mkdir(parents=True, exist_ok=True)

df_s1_3d.to_csv(LATEST_DIR / '主力買超_連續3天.csv', index=False, encoding='utf-8-sig')
df_s1_5d.to_csv(LATEST_DIR / '主力買超_連續5天.csv', index=False, encoding='utf-8-sig')
df_s2.to_csv(LATEST_DIR / '主力買超_5天3正.csv',    index=False, encoding='utf-8-sig')
df_rank.to_csv(LATEST_DIR / '主力買超_累積排名.csv', index=False, encoding='utf-8-sig')

print(f'\n✓ 已輸出 4 個篩選結果至 {LATEST_DIR}')
print('完成！')
