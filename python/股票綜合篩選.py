"""
台股綜合篩選系統 - 整合版
自動偵測今天日期，執行四種篩選策略：
1. 外資大量買超
2. 投信連續買超
3. 強勢股篩選
4. 盤整突破

特點：
- 自動使用今天日期（或最近交易日）
- 批次API請求優化
- 輸出整合報告
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys

# ==================== 全域設定 ====================

# 讀取 API Token (優先從 token 文件讀取，如果不存在則使用環境變數)
try:
    with open('token', 'r') as f:
        TOKEN = f.read().strip()
except FileNotFoundError:
    TOKEN = os.getenv('FINMIND_TOKEN', '')

API_URL = "https://api.finmindtrade.com/api/v4/data"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 自動使用今天日期（台灣時區）
TODAY = datetime.now().strftime('%Y-%m-%d')

# API 請求次數統計
API_REQUEST_COUNT = 0

# ==================== 共用函數 ====================

def get_date_range(end_date_str, days=100):
    """計算日期範圍"""
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    start_date = end_date - timedelta(days=days)
    return start_date.strftime('%Y-%m-%d'), end_date_str


def get_valid_stock_list():
    """讀取有效股票清單"""
    df = pd.read_csv('(all)stock_info_list.csv')
    return set(df['股票代碼'].astype(str).tolist())


def get_stock_info():
    """讀取股票資訊（代碼、名稱）"""
    df = pd.read_csv('(all)stock_info_list.csv')
    df['股票代碼'] = df['股票代碼'].astype(str)
    return df[['股票代碼', '公司名稱']].set_index('股票代碼').to_dict()['公司名稱']


def get_stock_category():
    """讀取股票族群分類（支援一對多）"""
    df = pd.read_csv('stock_category.csv')
    df['股票代碼'] = df['股票代碼'].astype(str)
    # 回傳 DataFrame，保留所有記錄（包含重複的股票代碼）
    return df[['股票代碼', '族群']]


def get_all_institutional_data(start_date, end_date):
    """批次獲取所有股票的法人買賣超資料"""
    global API_REQUEST_COUNT

    print(f"  正在獲取法人買賣超資料 ({start_date} ~ {end_date})...")

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    all_data = []
    for idx, date in enumerate(date_list, 1):
        parameter = {
            "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
            "start_date": date,
            "end_date": date,
        }
        try:
            resp = requests.get(API_URL, headers=HEADERS, params=parameter, timeout=10)
            API_REQUEST_COUNT += 1
            data = resp.json()

            # 檢查 API 回應狀態
            if 'status' in data and data['status'] != 200:
                print(f"  ⚠ API 錯誤 (日期: {date}): {data.get('msg', 'Unknown error')}")
                if idx == 1:  # 只在第一次請求失敗時顯示詳細資訊
                    print(f"     HTTP Status: {resp.status_code}")
                    print(f"     Response: {data}")

            if 'data' in data and len(data['data']) > 0:
                all_data.extend(data['data'])
        except requests.exceptions.Timeout:
            if idx == 1:
                print(f"  ⚠ API 請求超時 (日期: {date})")
        except requests.exceptions.RequestException as e:
            if idx == 1:
                print(f"  ⚠ API 請求失敗 (日期: {date}): {str(e)}")
        except Exception as e:
            if idx == 1:
                print(f"  ⚠ 未預期的錯誤 (日期: {date}): {str(e)}")
        time.sleep(0.05)

    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        print(f"  ✓ 共獲取 {len(df)} 筆法人資料")
        return df
    else:
        print(f"  ✗ 無法獲取法人資料")
        return None


def get_all_stock_prices(start_date, end_date, valid_stocks, category_stocks=None):
    """批次獲取所有股票的日K線資料"""
    global API_REQUEST_COUNT

    print(f"  正在獲取日K線資料 ({start_date} ~ {end_date})...")

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    all_data = []
    for idx, date in enumerate(date_list, 1):
        parameter = {
            "dataset": "TaiwanStockPrice",
            "start_date": date,
            "end_date": date,
        }
        try:
            resp = requests.get(API_URL, headers=HEADERS, params=parameter, timeout=10)
            API_REQUEST_COUNT += 1
            data = resp.json()

            # 檢查 API 回應狀態
            if 'status' in data and data['status'] != 200:
                print(f"  ⚠ API 錯誤 (日期: {date}): {data.get('msg', 'Unknown error')}")
                if idx == 1:
                    print(f"     HTTP Status: {resp.status_code}")
                    print(f"     Response: {data}")

            if 'data' in data and len(data['data']) > 0:
                all_data.extend(data['data'])
        except requests.exceptions.Timeout:
            if idx == 1:
                print(f"  ⚠ API 請求超時 (日期: {date})")
        except requests.exceptions.RequestException as e:
            if idx == 1:
                print(f"  ⚠ API 請求失敗 (日期: {date}): {str(e)}")
        except Exception as e:
            if idx == 1:
                print(f"  ⚠ 未預期的錯誤 (日期: {date}): {str(e)}")
        time.sleep(0.05)

    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        df = df[df['stock_id'].isin(valid_stocks) | (df['stock_id'] == '0050')]
        print(f"  ✓ 共獲取 {len(df)} 筆價格資料")

        # 如果有提供族群股票清單，補抓所有族群股票
        if category_stocks is not None:
            print(f"  正在補抓 {len(category_stocks)} 支族群股票的資料...")
            補抓成功 = 0
            for stock_id in category_stocks:
                parameter = {
                    "dataset": "TaiwanStockPrice",
                    "data_id": stock_id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                try:
                    resp = requests.get(API_URL, headers=HEADERS, params=parameter)
                    API_REQUEST_COUNT += 1
                    data = resp.json()
                    if 'data' in data and len(data['data']) > 0:
                        all_data.extend(data['data'])
                        補抓成功 += 1
                except Exception as e:
                    pass
                time.sleep(0.05)

            df = pd.DataFrame(all_data)
            # 去重（因為有些股票可能已經在批次抓取中獲得）
            df = df.drop_duplicates(subset=['stock_id', 'date'])
            # 允許族群股票即使不在valid_stocks中也保留
            df = df[df['stock_id'].isin(valid_stocks) | df['stock_id'].isin(category_stocks) | (df['stock_id'] == '0050')]
            print(f"  ✓ 補抓成功 {補抓成功} 支，去重後共 {len(df)} 筆價格資料")

        return df
    else:
        print(f"  ✗ 無法獲取價格資料")
        return None


# ==================== 策略1：外資大量買超 ====================

def calculate_institutional_stats(stock_df, investor_type, price_df=None):
    """計算法人買賣超統計資料（張數，不計算金額）"""
    if len(stock_df) == 0:
        return {'day1_net': 0, 'day3_net': 0, 'day5_net': 0, 'day5_buy_days': 0}

    investor_df = stock_df[stock_df['name'] == investor_type].copy()
    if len(investor_df) == 0:
        return {'day1_net': 0, 'day3_net': 0, 'day5_net': 0, 'day5_buy_days': 0}

    investor_df = investor_df.sort_values('date', ascending=False)
    investor_df['net_buy'] = investor_df['buy'].astype(float) - investor_df['sell'].astype(float)

    # 計算張數
    day1_net = int(investor_df.iloc[0]['net_buy'] / 1000) if len(investor_df) >= 1 else 0
    day3_net = int(investor_df.head(3)['net_buy'].sum() / 1000) if len(investor_df) >= 3 else 0
    day5_net = int(investor_df.head(5)['net_buy'].sum() / 1000) if len(investor_df) >= 5 else 0
    day5_buy_days = (investor_df.head(5)['net_buy'] > 0).sum() if len(investor_df) >= 5 else 0

    return {
        'day1_net': day1_net,
        'day3_net': day3_net,
        'day5_net': day5_net,
        'day5_buy_days': day5_buy_days
    }


def screen_foreign_investment(target_date, inst_df_all, price_df_all, valid_stocks, stock_info):
    """篩選外資大量買超"""
    print("\n【策略1：外資大量買超】")
    print(f"  篩選條件：當日外資買超 > 5000張 或 買超金額 > 2億元")

    # 找出最近的交易日
    available_dates = sorted(inst_df_all['date'].unique(), reverse=True)
    if len(available_dates) == 0:
        print("  ✗ 無可用的交易日資料")
        return pd.DataFrame()

    actual_date = available_dates[0]
    print(f"  實際使用日期：{actual_date}")

    # 計算日期範圍
    start_date, _ = get_date_range(actual_date, days=10)

    # 過濾資料
    inst_df_filtered = inst_df_all[
        (inst_df_all['stock_id'].isin(valid_stocks)) &
        (inst_df_all['date'] >= start_date) &
        (inst_df_all['date'] <= actual_date)
    ]

    # 獲取目標日期的價格資料
    price_target = price_df_all[price_df_all['date'] == actual_date]
    if len(price_target) == 0:
        print("  ✗ 無價格資料")
        return pd.DataFrame()

    price_dict = price_target.set_index('stock_id')['close'].astype(float).to_dict()

    # 篩選外資資料
    target_date_df = inst_df_filtered[inst_df_filtered['date'] == actual_date]
    foreign_target = target_date_df[target_date_df['name'] == 'Foreign_Investor'].copy()

    if len(foreign_target) == 0:
        print("  ✗ 無外資資料")
        return pd.DataFrame()

    # 計算買超
    foreign_target['net_buy'] = foreign_target['buy'].astype(float) - foreign_target['sell'].astype(float)
    foreign_target['net_buy_lots'] = foreign_target['net_buy'] / 1000
    foreign_target['amount'] = foreign_target.apply(
        lambda row: row['net_buy'] * price_dict.get(row['stock_id'], 0),
        axis=1
    )

    # 篩選符合條件
    filtered_stocks = foreign_target[
        (foreign_target['net_buy_lots'] > 5000) |
        (foreign_target['amount'] > 200000000)
    ]['stock_id'].unique()

    print(f"  符合條件：{len(filtered_stocks)} 支")

    results = []
    for stock_id in filtered_stocks:
        stock_inst_df = inst_df_filtered[inst_df_filtered['stock_id'] == stock_id].copy()
        foreign_stats = calculate_institutional_stats(stock_inst_df, 'Foreign_Investor')
        trust_stats = calculate_institutional_stats(stock_inst_df, 'Investment_Trust')
        stock_name = stock_info.get(stock_id, '未知')

        results.append({
            '股票代碼': stock_id,
            '公司名稱': stock_name,
            '當日外資買超(張)': foreign_stats['day1_net'],
            '近三日外資買超(張)': foreign_stats['day3_net'],
            '近五日外資買超(張)': foreign_stats['day5_net'],
            '近五日外資買超天數': foreign_stats['day5_buy_days'],
            '當日投信買超(張)': trust_stats['day1_net'],
            '近三日投信買超(張)': trust_stats['day3_net'],
            '近五日投信買超(張)': trust_stats['day5_net'],
            '近五日投信買超天數': trust_stats['day5_buy_days'],
        })

    result_df = pd.DataFrame(results).sort_values('當日外資買超(張)', ascending=False)
    print(f"  ✓ 完成！找到 {len(result_df)} 支股票")
    return result_df


# ==================== 策略2：投信連續買超 ====================

def check_investment_trust_condition(stock_df, min_avg_lots=500):
    """檢查投信買賣超條件"""
    if len(stock_df) == 0:
        return False, 0, 0, 0

    stock_df = stock_df.sort_values('date', ascending=False).head(5)
    stock_df['net_buy'] = stock_df['buy'].astype(float) - stock_df['sell'].astype(float)
    buy_days = (stock_df['net_buy'] > 0).sum()
    total_net_buy = stock_df['net_buy'].sum()
    avg_buy_lots = total_net_buy / 1000 / 5

    is_pass = (buy_days >= 4) and (avg_buy_lots >= min_avg_lots)
    return is_pass, buy_days, int(total_net_buy), int(avg_buy_lots)


def check_price_volatility(stock_df, threshold=0.14):
    """檢查價格波動條件"""
    if len(stock_df) == 0:
        return False, 0, 0, 0, 0

    stock_df = stock_df.sort_values('date', ascending=False).head(5)
    max_price = stock_df['max'].astype(float).max()
    min_price = stock_df['min'].astype(float).min()
    latest_close = float(stock_df.iloc[0]['close'])

    if min_price > 0:
        volatility = (max_price - min_price) / min_price
    else:
        volatility = 999

    return volatility <= threshold, volatility, max_price, min_price, latest_close


def screen_investment_trust(target_date, inst_df_all, price_df_all, valid_stocks, stock_info):
    """篩選投信連續買超"""
    print("\n【策略2：投信連續買超】")
    print(f"  篩選條件：近5日有4日投信買超、平均買超≥500張、價格波動≤14%、股價≤1000元")

    # 找出最近的交易日
    available_dates = sorted(inst_df_all['date'].unique(), reverse=True)
    if len(available_dates) == 0:
        print("  ✗ 無可用的交易日資料")
        return pd.DataFrame()

    actual_date = available_dates[0]
    print(f"  實際使用日期：{actual_date}")

    start_date, _ = get_date_range(actual_date, days=10)

    # 過濾資料
    trust_df = inst_df_all[
        (inst_df_all['name'] == 'Investment_Trust') &
        (inst_df_all['stock_id'].isin(valid_stocks)) &
        (inst_df_all['date'] >= start_date) &
        (inst_df_all['date'] <= actual_date)
    ].copy()

    price_df_filtered = price_df_all[
        (price_df_all['stock_id'].isin(valid_stocks)) &
        (price_df_all['date'] >= start_date) &
        (price_df_all['date'] <= actual_date)
    ]

    stock_list = trust_df['stock_id'].unique()
    print(f"  檢查 {len(stock_list)} 支股票...")

    results = []
    for stock_id in stock_list:
        stock_trust_df = trust_df[trust_df['stock_id'] == stock_id]
        trust_pass, buy_days, total_net_buy, avg_buy_lots = check_investment_trust_condition(stock_trust_df, 500)

        if not trust_pass:
            continue

        stock_price_df = price_df_filtered[price_df_filtered['stock_id'] == stock_id]
        if len(stock_price_df) == 0:
            continue

        price_pass, volatility, highest_price, lowest_price, latest_close = check_price_volatility(stock_price_df)

        if not price_pass or latest_close > 1000:
            continue

        stock_name = stock_info.get(stock_id, '未知')
        results.append({
            '股票代碼': stock_id,
            '公司名稱': stock_name,
            '最新收盤價': latest_close,
            '投信買超天數': buy_days,
            '投信5日淨買超': total_net_buy,
            '平均買超張數': avg_buy_lots,
            '5日最高價': highest_price,
            '5日最低價': lowest_price,
            '價格波動率': f"{volatility*100:.2f}%",
        })

    result_df = pd.DataFrame(results)
    print(f"  ✓ 完成！找到 {len(result_df)} 支股票")
    return result_df


# ==================== 策略3：強勢股篩選 ====================

def calculate_ma(stock_df, period):
    """計算移動平均線"""
    if len(stock_df) < period:
        return None
    close_prices = stock_df.head(period)['close'].astype(float)
    return close_prices.mean()


def calculate_volume_ma(stock_df, period):
    """計算成交量移動平均"""
    if len(stock_df) < period:
        return None
    volumes = stock_df.head(period)['Trading_Volume'].astype(float)
    return volumes.mean()


def calculate_return(stock_df, days=10):
    """計算N日漲幅"""
    if len(stock_df) < days + 1:
        return None
    latest_close = float(stock_df.iloc[0]['close'])
    past_close = float(stock_df.iloc[days]['close'])
    if past_close == 0:
        return None
    return ((latest_close - past_close) / past_close) * 100


def check_strong_stock_conditions(stock_df, target_date, benchmark_return_10d):
    """檢查強勢股條件"""
    if len(stock_df) < 60:
        return False, None

    today_data = stock_df.iloc[0]
    today_close = float(today_data['close'])
    today_volume = float(today_data['Trading_Volume'])

    # 條件1: 近10日最高價
    last_10_days = stock_df.head(10)
    max_close_10d = last_10_days['close'].astype(float).max()
    if today_close < max_close_10d:
        return False, None

    # 計算均線
    ma_10 = calculate_ma(stock_df, 10)
    ma_20 = calculate_ma(stock_df, 20)
    ma_60 = calculate_ma(stock_df, 60)

    if ma_10 is None or ma_20 is None or ma_60 is None:
        return False, None

    # 條件2: 多頭排列
    if not (ma_10 > ma_20 > ma_60):
        return False, None

    # 條件3: 收盤價 > 20MA
    if today_close <= ma_20:
        return False, None

    # 條件4: 十日漲幅 > 0050
    stock_return_10d = calculate_return(stock_df, 10)
    if stock_return_10d is None or stock_return_10d <= benchmark_return_10d:
        return False, None

    # 條件5: 成交量 > 10000張
    today_volume_lots = today_volume / 1000
    if today_volume_lots <= 10000:
        return False, None

    # 條件6: 量能比 >= 1.5
    vol_ma_5 = calculate_volume_ma(stock_df, 5)
    vol_ma_60 = calculate_volume_ma(stock_df, 60)

    if vol_ma_5 is None or vol_ma_60 is None or vol_ma_60 == 0:
        return False, None

    volume_ratio = vol_ma_5 / vol_ma_60
    if volume_ratio < 1.5:
        return False, None

    detail = {
        '收盤價': today_close,
        '10MA': round(ma_10, 2),
        '20MA': round(ma_20, 2),
        '60MA': round(ma_60, 2),
        '近10日漲幅': round(stock_return_10d, 2),
        '成交量(張)': int(today_volume_lots),
        '量能比(5MA/60MA)': round(volume_ratio, 2),
    }

    return True, detail


def screen_strong_stocks(target_date, price_df_all, valid_stocks, stock_info):
    """篩選強勢股"""
    print("\n【策略3：強勢股篩選】")
    print(f"  篩選條件：多頭排列、近10日最高、漲幅>0050、大量能")

    # 找出最近的交易日
    available_dates = sorted(price_df_all['date'].unique(), reverse=True)
    if len(available_dates) == 0:
        print("  ✗ 無可用的交易日資料")
        return pd.DataFrame()

    actual_date = available_dates[0]
    print(f"  實際使用日期：{actual_date}")

    start_date, _ = get_date_range(actual_date, days=100)

    # 計算0050基準
    benchmark_df = price_df_all[price_df_all['stock_id'] == '0050'].copy()
    benchmark_df = benchmark_df.sort_values('date', ascending=False)
    benchmark_return_10d = calculate_return(benchmark_df, 10)

    if benchmark_return_10d is None:
        print("  ✗ 無法計算0050漲幅")
        return pd.DataFrame()

    print(f"  0050 十日漲幅: {benchmark_return_10d:.2f}%")

    # 篩選股票
    stock_list = price_df_all[price_df_all['stock_id'].isin(valid_stocks)]['stock_id'].unique()
    print(f"  檢查 {len(stock_list)} 支股票...")

    results = []
    for stock_id in stock_list:
        stock_price_df = price_df_all[price_df_all['stock_id'] == stock_id].copy()
        stock_price_df = stock_price_df.sort_values('date', ascending=False)

        is_pass, detail = check_strong_stock_conditions(stock_price_df, actual_date, benchmark_return_10d)

        if not is_pass:
            continue

        stock_name = stock_info.get(stock_id, '未知')
        results.append({
            '股票代碼': stock_id,
            '公司名稱': stock_name,
            '收盤價': detail['收盤價'],
            '近10日漲幅': f"{detail['近10日漲幅']}%",
            '成交量(張)': detail['成交量(張)'],
            '量能比': detail['量能比(5MA/60MA)'],
        })

    result_df = pd.DataFrame(results)
    print(f"  ✓ 完成！找到 {len(result_df)} 支股票")
    return result_df


# ==================== 策略4：盤整突破 ====================

def check_breakthrough(stock_df, target_date, check_days=3):
    """檢查盤整突破"""
    if len(stock_df) < 20 + check_days:
        return False, []

    stock_df = stock_df.sort_values('date', ascending=False)

    target_row = stock_df[stock_df['date'] == target_date]
    if len(target_row) == 0:
        return False, []

    today_close = float(target_row.iloc[0]['close'])
    target_idx = stock_df[stock_df['date'] == target_date].index[0]
    target_position = stock_df.index.get_loc(target_idx)

    check_range_df = stock_df.iloc[target_position:target_position + check_days]
    breakthrough_list = []

    for idx, row in check_range_df.iterrows():
        check_date = row['date']
        check_open = float(row['open'])
        check_volume = float(row['Trading_Volume'])
        check_volume_lots = check_volume / 1000

        check_position = stock_df.index.get_loc(idx)
        ma_data = stock_df.iloc[check_position:check_position + 20]

        if len(ma_data) < 20:
            continue

        volumes = ma_data.head(20)['Trading_Volume'].astype(float)
        volume_ma_20 = volumes.mean()

        if volume_ma_20 == 0:
            continue

        volume_ma_20_lots = volume_ma_20 / 1000
        volume_ratio = check_volume_lots / volume_ma_20_lots

        if volume_ratio > 5 and check_volume_lots > 5000:
            if check_open > 0:
                price_change_pct = ((today_close - check_open) / check_open) * 100
            else:
                price_change_pct = 0

            breakthrough_list.append({
                'breakthrough_date': check_date,
                'breakthrough_price': check_open,
                'breakthrough_volume': int(check_volume_lots),
                'volume_ma_20': int(volume_ma_20_lots),
                'volume_ratio': round(volume_ratio, 2),
                'price_change_pct': round(price_change_pct, 2)
            })

    if len(breakthrough_list) > 0:
        return True, breakthrough_list
    else:
        return False, []


def screen_breakthrough(target_date, price_df_all, valid_stocks, stock_info):
    """篩選盤整突破"""
    print("\n【策略4：盤整突破】")
    print(f"  篩選條件：成交量>20MA的5倍、成交量>5000張、近3個交易日內突破")

    # 找出最近的交易日
    available_dates = sorted(price_df_all['date'].unique(), reverse=True)
    if len(available_dates) < 3:
        print("  ✗ 交易日資料不足")
        return pd.DataFrame()

    actual_date = available_dates[0]
    print(f"  實際使用日期：{actual_date}")

    start_date, _ = get_date_range(actual_date, days=40)

    # 篩選股票
    stock_list = price_df_all[price_df_all['stock_id'].isin(valid_stocks)]['stock_id'].unique()
    print(f"  檢查 {len(stock_list)} 支股票...")

    results = []
    for stock_id in stock_list:
        stock_price_df = price_df_all[price_df_all['stock_id'] == stock_id].copy()
        stock_price_df = stock_price_df.sort_values('date', ascending=False)

        is_breakthrough, breakthrough_list = check_breakthrough(stock_price_df, actual_date, 3)

        if not is_breakthrough:
            continue

        stock_name = stock_info.get(stock_id, '未知')
        today_row = stock_price_df[stock_price_df['date'] == actual_date]
        today_close_price = float(today_row.iloc[0]['close']) if len(today_row) > 0 else 0

        for bt in breakthrough_list:
            results.append({
                '股票代碼': stock_id,
                '公司名稱': stock_name,
                '突破日期': bt['breakthrough_date'],
                '突破日股價': bt['breakthrough_price'],
                '今日收盤價': today_close_price,
                '今日至突破日漲跌幅': f"{bt['price_change_pct']}%",
                '突破日成交量(張)': bt['breakthrough_volume'],
                '20MA成交量(張)': bt['volume_ma_20'],
                '成交量倍數': bt['volume_ratio'],
            })

    result_df = pd.DataFrame(results)
    if len(result_df) > 0:
        result_df = result_df.sort_values('突破日期', ascending=False)

    print(f"  ✓ 完成！找到 {len(result_df)} 筆突破記錄")
    return result_df


# ==================== 新增功能：族群個股資料與族群排名 ====================

def calculate_stock_return(stock_df, days=1):
    """計算股票N日漲跌幅"""
    if len(stock_df) < days + 1:
        return None

    stock_df = stock_df.sort_values('date', ascending=False)
    latest_close = float(stock_df.iloc[0]['close'])
    past_close = float(stock_df.iloc[days]['close'])

    if past_close == 0:
        return None

    return ((latest_close - past_close) / past_close) * 100


def generate_category_stock_data(actual_date, price_df_all, inst_df_all, stock_info, stock_category_df):
    """生成族群個股資料（支援一對多）"""
    print("\n【生成族群個股資料】")

    # 取得所有唯一股票代碼
    category_stocks = set(stock_category_df['股票代碼'].unique())
    print(f"  族群內唯一股票數量：{len(category_stocks)}")
    print(f"  族群記錄總數：{len(stock_category_df)}")

    # 過濾價格資料
    stock_list = price_df_all[price_df_all['stock_id'].isin(category_stocks)]['stock_id'].unique()
    print(f"  有價格資料的股票：{len(stock_list)}")

    results = []
    # 對每個「股票代碼-族群」組合生成一筆記錄
    for _, row in stock_category_df.iterrows():
        stock_id = row['股票代碼']
        category = row['族群']

        # 檢查該股票是否有價格資料
        if stock_id not in stock_list:
            continue

        stock_price_df = price_df_all[price_df_all['stock_id'] == stock_id].copy()
        stock_price_df = stock_price_df.sort_values('date', ascending=False)

        # 檢查是否有今日資料
        today_data = stock_price_df[stock_price_df['date'] == actual_date]
        if len(today_data) == 0:
            continue

        # 計算漲跌幅
        return_1d = calculate_stock_return(stock_price_df, 1)
        return_3d = calculate_stock_return(stock_price_df, 3)

        if return_1d is None:
            continue

        # 今日成交量
        today_volume = float(today_data.iloc[0]['Trading_Volume']) / 1000

        # 取得公司名稱
        stock_name = stock_info.get(stock_id, '未知')

        results.append({
            '股票代碼': stock_id,
            '公司名稱': stock_name,
            '族群': category,
            '今日漲跌幅': round(return_1d, 2),
            '近三交易日漲跌幅': round(return_3d, 2) if return_3d is not None else 0,
            '今日成交量': int(today_volume),
        })

    result_df = pd.DataFrame(results)

    # 依族群分組，每個族群內用今日漲跌幅排序
    if len(result_df) > 0:
        result_df = result_df.sort_values(['族群', '今日漲跌幅'], ascending=[True, False])

    print(f"  ✓ 完成！共 {len(result_df)} 筆記錄（包含重複股票）")
    return result_df


def generate_category_ranking(actual_date, price_df_all, inst_df_all, stock_category, category_stock_df):
    """生成族群排名"""
    print("\n【生成族群排名】")

    if len(category_stock_df) == 0:
        print("  ✗ 無族群個股資料")
        return pd.DataFrame()

    # 計算每個族群的統計資料
    category_stats = []

    for category in category_stock_df['族群'].unique():
        category_df = category_stock_df[category_stock_df['族群'] == category]

        # 族群平均漲幅
        avg_return = category_df['今日漲跌幅'].mean()

        # 族群上漲檔數
        up_count = (category_df['今日漲跌幅'] > 0).sum()
        total_count = len(category_df)
        up_pct = (up_count / total_count * 100) if total_count > 0 else 0

        # 取得該族群的股票代碼
        category_stock_ids = category_df['股票代碼'].tolist()

        # 計算法人買賣超
        category_inst_df = inst_df_all[inst_df_all['stock_id'].isin(category_stock_ids)]

        # 外資買超（金額）
        foreign_df = category_inst_df[category_inst_df['name'] == 'Foreign_Investor'].copy()
        foreign_df = foreign_df.sort_values('date', ascending=False)

        foreign_1d = 0
        foreign_3d = 0
        if len(foreign_df) > 0:
            foreign_df['net_buy'] = foreign_df['buy'].astype(float) - foreign_df['sell'].astype(float)

            # 為每筆交易加上股價，計算金額
            for stock_id in category_stock_ids:
                stock_price_df = price_df_all[price_df_all['stock_id'] == stock_id]
                stock_foreign_df = foreign_df[foreign_df['stock_id'] == stock_id]

                for idx, row in stock_foreign_df.iterrows():
                    price_row = stock_price_df[stock_price_df['date'] == row['date']]
                    if len(price_row) > 0:
                        stock_price = float(price_row.iloc[0]['close'])
                        # 計算買超金額（張數 * 1000 * 股價）
                        foreign_df.loc[idx, 'net_buy_amount'] = (row['net_buy'] / 1000) * 1000 * stock_price
                    else:
                        foreign_df.loc[idx, 'net_buy_amount'] = 0

            # 最近一日
            day1_df = foreign_df[foreign_df['date'] == actual_date]
            foreign_1d = int(day1_df['net_buy_amount'].sum()) if len(day1_df) > 0 else 0
            # 近三日
            dates = sorted(foreign_df['date'].unique(), reverse=True)[:3]
            day3_df = foreign_df[foreign_df['date'].isin(dates)]
            foreign_3d = int(day3_df['net_buy_amount'].sum()) if len(day3_df) > 0 else 0

        # 投信買超（金額）
        trust_df = category_inst_df[category_inst_df['name'] == 'Investment_Trust'].copy()
        trust_df = trust_df.sort_values('date', ascending=False)

        trust_1d = 0
        trust_3d = 0
        if len(trust_df) > 0:
            trust_df['net_buy'] = trust_df['buy'].astype(float) - trust_df['sell'].astype(float)

            # 為每筆交易加上股價，計算金額
            for stock_id in category_stock_ids:
                stock_price_df = price_df_all[price_df_all['stock_id'] == stock_id]
                stock_trust_df = trust_df[trust_df['stock_id'] == stock_id]

                for idx, row in stock_trust_df.iterrows():
                    price_row = stock_price_df[stock_price_df['date'] == row['date']]
                    if len(price_row) > 0:
                        stock_price = float(price_row.iloc[0]['close'])
                        # 計算買超金額（張數 * 1000 * 股價）
                        trust_df.loc[idx, 'net_buy_amount'] = (row['net_buy'] / 1000) * 1000 * stock_price
                    else:
                        trust_df.loc[idx, 'net_buy_amount'] = 0

            # 最近一日
            day1_df = trust_df[trust_df['date'] == actual_date]
            trust_1d = int(day1_df['net_buy_amount'].sum()) if len(day1_df) > 0 else 0
            # 近三日
            dates = sorted(trust_df['date'].unique(), reverse=True)[:3]
            day3_df = trust_df[trust_df['date'].isin(dates)]
            trust_3d = int(day3_df['net_buy_amount'].sum()) if len(day3_df) > 0 else 0

        category_stats.append({
            '族群': category,
            '族群平均漲幅': round(avg_return, 2),
            f'族群上漲檔數(%)': round(up_pct, 2),
            '族群上漲檔數(數量)': f"{up_count}/{total_count}",
            '外資近一日總買超(億元)': round(foreign_1d / 100000000, 2),
            '外資近三日總買超(億元)': round(foreign_3d / 100000000, 2),
            '投信近一日總買超(億元)': round(trust_1d / 100000000, 2),
            '投信近三日總買超(億元)': round(trust_3d / 100000000, 2),
        })

    result_df = pd.DataFrame(category_stats)

    # 依上漲檔數(%)排序，並加上排名
    if len(result_df) > 0:
        result_df = result_df.sort_values('族群上漲檔數(%)', ascending=False)
        result_df.insert(0, '排名', range(1, len(result_df) + 1))

    print(f"  ✓ 完成！共 {len(result_df)} 個族群")
    return result_df


# ==================== 主程式 ====================

def main():
    """主程式 - 執行所有篩選策略"""
    start_time = time.time()

    print("=" * 80)
    print("台股綜合篩選系統".center(76))
    print("=" * 80)
    print(f"\n執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目標日期：{TODAY} (若為非交易日則自動使用最近交易日)")
    print("\n")

    # 讀取股票清單
    print("正在載入股票清單...")
    valid_stocks = get_valid_stock_list()
    stock_info = get_stock_info()
    stock_category_df = get_stock_category()
    unique_category_stocks = stock_category_df['股票代碼'].nunique()
    print(f"✓ 載入 {len(valid_stocks)} 支股票")
    print(f"✓ 載入 {unique_category_stocks} 支族群股票（共 {len(stock_category_df)} 筆記錄）\n")

    # 批次獲取共用資料
    print("=" * 80)
    print("開始獲取共用資料")
    print("=" * 80)

    # 法人資料（策略1、2使用）
    inst_start_date, _ = get_date_range(TODAY, days=10)
    inst_df_all = get_all_institutional_data(inst_start_date, TODAY)

    # 價格資料（所有策略使用，需要較長期間）
    price_start_date, _ = get_date_range(TODAY, days=100)
    category_stocks_set = set(stock_category_df['股票代碼'].unique())
    price_df_all = get_all_stock_prices(price_start_date, TODAY, valid_stocks, category_stocks_set)

    if inst_df_all is None or price_df_all is None:
        print("\n✗ 無法獲取必要資料，程式終止")
        print("請檢查：")
        print("1. FINMIND_TOKEN 是否正確")
        print("2. 網路連線是否正常")
        print("3. FinMind API 是否有速率限制")
        sys.exit(1)  # 返回錯誤碼，讓 GitHub Actions 知道失敗了

    print("\n✓ 共用資料獲取完成\n")

    # 找出實際使用的交易日期（用於檔名）
    available_dates = sorted(price_df_all['date'].unique(), reverse=True)
    actual_trade_date = available_dates[0] if len(available_dates) > 0 else TODAY
    print(f"\n實際交易日期：{actual_trade_date}")

    # 執行四個策略
    print("\n" + "=" * 80)
    print("開始執行篩選策略")
    print("=" * 80)

    results = {}

    # 策略1：外資大量買超
    results['外資大量買超'] = screen_foreign_investment(
        TODAY, inst_df_all, price_df_all, valid_stocks, stock_info
    )

    # 策略2：投信連續買超
    results['投信連續買超'] = screen_investment_trust(
        TODAY, inst_df_all, price_df_all, valid_stocks, stock_info
    )

    # 策略3：強勢股篩選
    results['強勢股篩選'] = screen_strong_stocks(
        TODAY, price_df_all, valid_stocks, stock_info
    )

    # 策略4：盤整突破
    results['盤整突破'] = screen_breakthrough(
        TODAY, price_df_all, valid_stocks, stock_info
    )

    # 新增功能：族群個股資料
    category_stock_df = generate_category_stock_data(
        actual_trade_date, price_df_all, inst_df_all, stock_info, stock_category_df
    )

    # 新增功能：族群排名
    category_ranking_df = generate_category_ranking(
        actual_trade_date, price_df_all, inst_df_all, stock_category_df, category_stock_df
    )

    # 輸出結果
    print("\n" + "=" * 80)
    print("篩選結果摘要".center(76))
    print("=" * 80)

    for strategy, df in results.items():
        print(f"\n{strategy}：{len(df)} 個結果")
        if len(df) > 0:
            print(df.head(10).to_string(index=False))
            if len(df) > 10:
                print(f"... (共 {len(df)} 筆，僅顯示前10筆)")

    # 顯示族群排名摘要
    if len(category_ranking_df) > 0:
        print(f"\n族群排名：{len(category_ranking_df)} 個族群")
        print(category_ranking_df.head(10).to_string(index=False))
        if len(category_ranking_df) > 10:
            print(f"... (共 {len(category_ranking_df)} 個族群，僅顯示前10名)")

    # 顯示族群個股資料摘要
    if len(category_stock_df) > 0:
        print(f"\n族群個股資料：{len(category_stock_df)} 支股票")

    # 儲存結果
    print("\n" + "=" * 80)
    print("儲存結果檔案".center(76))
    print("=" * 80)

    # 使用實際交易日期作為檔名
    date_str = actual_trade_date.replace('-', '')

    for strategy, df in results.items():
        if len(df) > 0:
            filename = f"{date_str}_{strategy}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✓ {filename}")

    # 儲存族群個股資料
    if len(category_stock_df) > 0:
        filename = f"{date_str}_族群個股資料.csv"
        category_stock_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ {filename}")

    # 儲存族群排名
    if len(category_ranking_df) > 0:
        filename = f"{date_str}_族群排名.csv"
        category_ranking_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ {filename}")

    # 執行統計
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("\n" + "=" * 80)
    print("執行完成".center(76))
    print("=" * 80)
    print(f"\n總執行時間：{elapsed_time:.2f} 秒")
    print(f"API 請求總次數：{API_REQUEST_COUNT} 次")
    print(f"總共找到 {sum(len(df) for df in results.values())} 筆符合條件的記錄")
    print("\n所有檔案已儲存完成！\n")


if __name__ == "__main__":
    main()
