import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta

# 設定查詢日期
# 注意:股東持股資料通常每週更新一次（週五）
USE_AUTO_DATE = True  # 設為 True 自動查詢，False 使用手動日期
TARGET_DATE = datetime.now().strftime("%Y-%m-%d")  # 使用今天日期
DAYS_BACK = 30  # 往前查詢的天數（約20個交易日）
# MANUAL_START_DATE = "2025-11-14"
# MANUAL_END_DATE = "2025-11-21"

# API 設定
API_URL = "https://api.finmindtrade.com/api/v4/data"
# 優先從 token 文件讀取，如果不存在則使用環境變數
try:
    with open('token', 'r') as f:
        API_TOKEN = f.read().strip()
except FileNotFoundError:
    API_TOKEN = os.getenv('FINMIND_TOKEN', '')
API_HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# 檔案路徑（使用相對路徑）
STOCK_LIST_PATH = '(all)stock_info_list.csv'
OUTPUT_PATH = './'

def get_available_dates(target_date, days_back=60):
    """獲取目標日期往前推算期間內所有有資料的日期"""
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    start_dt = target_dt - timedelta(days=days_back)

    print(f"查詢 {start_dt.strftime('%Y-%m-%d')} 至 {target_date} 期間的可用日期...")
    # 使用台積電(2330)作為參考股票來查詢可用日期
    params = {
        "dataset": "TaiwanStockHoldingSharesPer",
        "data_id": "2330",  # 使用台積電作為參考
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": target_date,
    }
    resp = requests.get(API_URL, headers=API_HEADERS, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data and data['data']:
            df = pd.DataFrame(data['data'])
            available_dates = sorted(df['date'].unique(), reverse=True)
            print(f"找到 {len(available_dates)} 個有資料的日期")
            return available_dates
    return []

def fetch_all_holding_data(date):
    """一次性獲取某日期所有股票的持股分散資料"""
    print(f"正在獲取 {date} 的持股資料...")
    params = {
        "dataset": "TaiwanStockHoldingSharesPer",
        "start_date": date,
        "end_date": date,
    }
    resp = requests.get(API_URL, headers=API_HEADERS, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data and data['data']:
            return pd.DataFrame(data['data'])
    return None

def get_big_buyer_levels(def_big_buyer):
    """根據總股數決定大戶級距"""
    levels_map = [
        (1000000, ['more than 1,000,001']),
        (800000, ['more than 1,000,001', '800,001-1,000,000']),
        (600000, ['more than 1,000,001', '800,001-1,000,000', '600,001-800,000']),
        (0, ['more than 1,000,001', '800,001-1,000,000', '600,001-800,000', '400,001-600,000'])
    ]
    for threshold, levels in levels_map:
        if def_big_buyer >= threshold:
            return levels
    return levels_map[-1][1]

def calculate_holding_change_batch(start_df, end_df, ticker):
    """計算單一股票的大戶持股變化（從已載入的資料）"""
    try:
        start_data = start_df[start_df['stock_id'] == ticker]
        end_data = end_df[end_df['stock_id'] == ticker]

        if start_data.empty or end_data.empty:
            return None

        total_share = start_data[start_data['HoldingSharesLevel'] == 'total']
        if total_share.empty:
            return None

        def_big_buyer = total_share['unit'].iloc[0] / 1000 * 0.5
        levels = get_big_buyer_levels(def_big_buyer)

        start_big = start_data[start_data['HoldingSharesLevel'].isin(levels)]
        end_big = end_data[end_data['HoldingSharesLevel'].isin(levels)]

        if start_big.empty or end_big.empty:
            return None

        start_pct = round(start_big['percent'].astype(float).sum(), 1)
        end_pct = round(end_big['percent'].astype(float).sum(), 1)
        diff = round(end_pct - start_pct, 1)
        pct_change = round(diff / start_pct * 100, 1) if start_pct != 0 else 0.0

        return {'股票代碼': ticker, '大戶持有比例差': diff, '大戶增加比例(%)': pct_change}

    except Exception as e:
        return None

def fetch_api_data(dataset, data_id, start_date, end_date):
    """統一的 API 請求函數"""
    params = {
        "dataset": dataset,
        "data_id": data_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    resp = requests.get(API_URL, headers=API_HEADERS, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data and data['data']:
            return pd.DataFrame(data['data'])
    return None

def get_stock_data(ticker_list, start_date, end_date):
    """獲取股票價格數據並計算期間統計"""
    all_data = []

    for i, ticker in enumerate(ticker_list):
        try:
            df = fetch_api_data("TaiwanStockPrice", ticker, start_date, end_date)
            if df is None or len(df.columns) < 8:
                continue

            df = df.iloc[:, [0, 1, 4, 5, 6, 7]]
            df.columns = ['Date', 'stock_id', 'Open', 'High', 'Low', 'Close']
            df['Date'] = pd.to_datetime(df['Date'])

            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            if not df[['Open', 'High', 'Low', 'Close']].isna().all().all():
                all_data.append(df)

        except Exception as e:
            print(f"處理股票 {ticker} 時發生錯誤: {str(e)}")

        if i < len(ticker_list) - 1:
            time.sleep(0.1)

    if not all_data:
        return pd.DataFrame(columns=['stock_id', '第一天開盤價', '期間最高價', '期間最低價', '最後一天收盤價'])

    final_df = pd.concat(all_data, ignore_index=True).sort_values(['stock_id', 'Date'])

    result_data = []
    for stock in final_df['stock_id'].unique():
        stock_data = final_df[final_df['stock_id'] == stock].sort_values('Date')
        if len(stock_data) > 0:
            result_data.append({
                'stock_id': stock,
                '第一天開盤價': stock_data.iloc[0]['Open'],
                '期間最高價': stock_data['High'].max(),
                '期間最低價': stock_data['Low'].min(),
                '最後一天收盤價': stock_data.iloc[-1]['Close']
            })

    return pd.DataFrame(result_data)

# === 主程式 ===
print("=== 股東持有比例差分析（優化版）===\n")

if USE_AUTO_DATE:
    print(f"模式: 自動查詢日期")
    print(f"目標日期: {TARGET_DATE}")
    print(f"往前查詢: {DAYS_BACK} 天\n")
    # 自動找出最近的兩筆資料日期
    available_dates = get_available_dates(TARGET_DATE, days_back=DAYS_BACK)
    if len(available_dates) < 2:
        print(f"錯誤：找不到足夠的歷史資料（需要至少2筆，目前只有 {len(available_dates)} 筆）")
        print(f"請將 USE_AUTO_DATE 設為 False 並手動指定日期")
        exit()

    END_DATE = available_dates[0]
    START_DATE = available_dates[1]

    print(f"\n自動選取最近兩筆資料日期：")
else:
    print(f"模式: 手動指定日期")
    START_DATE = MANUAL_START_DATE
    END_DATE = MANUAL_END_DATE
    print(f"使用手動指定日期：")

print(f"  起始日期: {START_DATE}")
print(f"  結束日期: {END_DATE}")
print(f"  分析期間: {(datetime.strptime(END_DATE, '%Y-%m-%d') - datetime.strptime(START_DATE, '%Y-%m-%d')).days} 天\n")

# 讀取股票清單
print("讀取股票清單...")
stock_info = pd.read_csv(STOCK_LIST_PATH)
valid_tickers = stock_info.iloc[:, 0].astype(str).str.zfill(4).tolist()
print(f"共 {len(valid_tickers)} 檔股票\n")

# 一次性獲取起始日期和結束日期的所有持股資料（只需 2 次 API 請求）
start_holding_df = fetch_all_holding_data(START_DATE)
time.sleep(1)
end_holding_df = fetch_all_holding_data(END_DATE)

if start_holding_df is None or end_holding_df is None:
    print("無法獲取持股資料")
    exit()

print(f"起始日期資料: {len(start_holding_df)} 筆")
print(f"結束日期資料: {len(end_holding_df)} 筆\n")

# 只保留 valid_tickers 中的股票
start_holding_df = start_holding_df[start_holding_df['stock_id'].isin(valid_tickers)]
end_holding_df = end_holding_df[end_holding_df['stock_id'].isin(valid_tickers)]

print(f"過濾後起始日期資料: {len(start_holding_df)} 筆")
print(f"過濾後結束日期資料: {len(end_holding_df)} 筆\n")

# 計算每檔股票的持股變化
print("開始計算持股變化...")
result_list = []
processed_count = 0

for ticker in valid_tickers:
    result = calculate_holding_change_batch(start_holding_df, end_holding_df, ticker)
    if result:
        result_list.append(result)
        processed_count += 1
        if processed_count % 100 == 0:
            print(f"已處理 {processed_count} 檔股票...")

print(f"成功計算 {len(result_list)} 檔股票的持股變化\n")

if not result_list:
    print("沒有成功處理任何股票數據")
    exit()

# 整理結果並排序
df = pd.DataFrame(result_list).sort_values('大戶增加比例(%)', ascending=False).head(50)
df.insert(0, '排名', range(1, len(df) + 1))

# 獲取股票價格數據
print("開始獲取股票價格數據...")
price_df = get_stock_data(df['股票代碼'].tolist(), START_DATE, END_DATE)

# 合併價格數據
if not price_df.empty:
    result = df.merge(
        price_df[['stock_id', '第一天開盤價', '期間最高價', '期間最低價', '最後一天收盤價']],
        left_on='股票代碼',
        right_on='stock_id',
        how='left'
    ).drop('stock_id', axis=1)
else:
    result = df

# 獲取並合併公司資訊
print("開始獲取公司資訊...")
try:
    resp = requests.get(API_URL, headers=API_HEADERS, params={"dataset": "TaiwanStockInfoWithWarrant"})
    if resp.status_code == 200:
        comp_data = resp.json()
        if 'data' in comp_data and comp_data['data']:
            comp_df = pd.DataFrame(comp_data['data']).iloc[:, [0, 1, 2]]
            comp_df.columns = ['公司產業', '股票代碼', '公司名稱']
            comp_df = comp_df.drop_duplicates(subset=['股票代碼'])

            result = result.merge(comp_df, on='股票代碼', how='left')

            # 調整欄位順序
            cols = result.columns.tolist()
            for col in ['公司名稱', '公司產業']:
                if col in cols:
                    cols.remove(col)
                    cols.insert(2, col)
            result = result[cols]
except Exception as e:
    print(f"獲取公司資訊時發生錯誤: {str(e)}")

# 計算周漲幅
if '最後一天收盤價' in result.columns and '第一天開盤價' in result.columns:
    result['周漲幅'] = round((result['最後一天收盤價'] / result['第一天開盤價'] - 1) * 100, 1)

# 保存結果
filename = f"{START_DATE}_{END_DATE}大戶持有比例差"
for ext, func in [('.csv', result.to_csv)]:
    try:
        func(f"{OUTPUT_PATH}{filename}{ext}", index=False)
        print(f"{ext[1:].upper()}文件已保存: {filename}{ext}")
    except Exception as e:
        print(f"保存{ext[1:].upper()}文件時發生錯誤: {str(e)}")

print(f"\n處理完成！最終結果包含 {len(result)} 個股票的數據")
print("\n=== API 請求次數統計 ===")
print("查詢可用日期: 1 次")
print("持股資料: 2 次（起始日期 + 結束日期）")
print(f"價格資料: {len(df)} 次（前50名股票）")
print("公司資訊: 1 次")
print(f"總計: {1 + 2 + len(df) + 1} 次")
print(f"\n相比原版本減少: {len(valid_tickers) - 4} 次請求！")

result
