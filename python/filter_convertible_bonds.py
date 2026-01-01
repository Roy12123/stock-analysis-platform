import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def get_token():
    """讀取API token"""
    # 優先使用環境變數
    token = os.getenv('FINMIND_TOKEN')

    if not token:
        # 嘗試從檔案讀取
        token_file = 'FinMind_API/token'
        try:
            with open(token_file, 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print(f"⚠️ Token 檔案不存在: {token_file}")
            raise ValueError("無法取得 FinMind API token（請設定環境變數 FINMIND_TOKEN 或提供 token_file）")

    return token


def get_latest_trading_date():
    """
    取得最近的交易日（今天或往前推最多7天）
    """
    token = get_token()
    url = 'https://api.finmindtrade.com/api/v4/data'
    headers = {'Authorization': f'Bearer {token}'}

    # 從今天往回找最近7天
    for days_ago in range(8):
        check_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        parameter = {
            'dataset': 'TaiwanStockPriceAdj',
            'start_date': check_date,
        }

        print(f"檢查日期: {check_date}...", end=' ')
        resp = requests.get(url, headers=headers, params=parameter)
        data = resp.json()

        if 'data' in data and len(data['data']) > 0:
            print(f"✓ 找到交易資料！")
            return check_date, pd.DataFrame(data['data'])
        else:
            print("無交易資料")

    return None, None


def get_stock_volume_data(stock_ids, end_date):
    """
    取得股票過去30天的成交量資料（用於計算5MA）
    """
    token = get_token()
    url = 'https://api.finmindtrade.com/api/v4/data'
    headers = {'Authorization': f'Bearer {token}'}

    # 計算起始日期（往前推40天確保有足夠資料）
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=40)).strftime("%Y-%m-%d")

    all_data = []

    # 分批取得股票資料（避免一次請求太多）
    batch_size = 50
    for i in range(0, len(stock_ids), batch_size):
        batch = stock_ids[i:i+batch_size]

        for stock_id in batch:
            parameter = {
                'dataset': 'TaiwanStockPriceAdj',
                'data_id': stock_id,
                'start_date': start_date,
                'end_date': end_date,
            }

            resp = requests.get(url, headers=headers, params=parameter)
            data = resp.json()

            if 'data' in data and len(data['data']) > 0:
                all_data.extend(data['data'])

    if all_data:
        return pd.DataFrame(all_data)
    return pd.DataFrame()


def get_cb_volume_data(cb_ids, end_date):
    """
    取得可轉債過去30天的成交量資料（用於計算5MA）
    """
    token = get_token()
    url = 'https://api.finmindtrade.com/api/v4/data'
    headers = {'Authorization': f'Bearer {token}'}

    # 計算起始日期
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=40)).strftime("%Y-%m-%d")

    all_data = []

    for cb_id in cb_ids:
        parameter = {
            'dataset': 'TaiwanStockConvertibleBondDaily',
            'data_id': cb_id,
            'start_date': start_date,
            'end_date': end_date,
        }

        resp = requests.get(url, headers=headers, params=parameter)
        data = resp.json()

        if 'data' in data and len(data['data']) > 0:
            all_data.extend(data['data'])

    if all_data:
        return pd.DataFrame(all_data)
    return pd.DataFrame()


def get_convertible_bonds_list():
    """
    從 FinMind API 取得所有可轉債資料
    """
    token = get_token()
    url = 'https://api.finmindtrade.com/api/v4/data'
    headers = {'Authorization': f'Bearer {token}'}

    # 取得基本資訊
    print("      從 FinMind API 取得可轉債基本資訊...")
    parameter = {
        'dataset': 'TaiwanStockConvertibleBondInfo',
    }
    resp = requests.get(url, headers=headers, params=parameter)
    data = resp.json()

    if 'data' not in data or len(data['data']) == 0:
        print("      ⚠️ 無法取得可轉債資訊")
        return pd.DataFrame()

    info_df = pd.DataFrame(data['data'])

    # 取得最新總覽資料（有轉換價格）
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"      取得最新可轉債總覽...")
    parameter = {
        'dataset': 'TaiwanStockConvertibleBondDailyOverview',
        'start_date': today,
        'end_date': today,
    }
    resp = requests.get(url, headers=headers, params=parameter)
    data = resp.json()

    # 如果今天無資料，嘗試前一天
    if 'data' not in data or len(data['data']) == 0:
        yesterday = (pd.Timestamp(today) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        parameter['start_date'] = yesterday
        parameter['end_date'] = yesterday
        resp = requests.get(url, headers=headers, params=parameter)
        data = resp.json()

    if 'data' not in data or len(data['data']) == 0:
        print("      ⚠️ 無法取得可轉債總覽資料")
        return pd.DataFrame()

    overview_df = pd.DataFrame(data['data'])

    # 合併資料
    merged_df = info_df.merge(
        overview_df[['cb_id', 'ConversionPrice', 'date']],
        on='cb_id',
        how='left'
    )

    # 移除已下市或無總覽資料的
    merged_df = merged_df.dropna(subset=['ConversionPrice'])

    # 從 cb_id 提取股票代碼（前4碼）
    merged_df['stock_id'] = merged_df['cb_id'].astype(str).str[:4]

    # 只保留需要的欄位並重新命名
    result_df = merged_df[['stock_id', 'cb_name', 'cb_id', 'ConversionPrice']].copy()
    result_df.columns = ['股票代碼', '標的債券', '債券代號', '轉換價格']

    return result_df


def filter_convertible_bonds():
    """
    篩選轉換價格在收盤價正負5%內，且成交量大於5MA兩倍的可轉債
    """
    print("=" * 70)
    print("可轉債篩選程式 - 價格+成交量雙重篩選")
    print("=" * 70)

    # 1. 取得可轉債資料
    print("\n[1/7] 取得可轉債資料...")
    cb_df = get_convertible_bonds_list()

    if cb_df.empty:
        print("      ⚠️ 無法取得可轉債資料，程式終止")
        return pd.DataFrame()

    print(f"      共 {len(cb_df)} 檔可轉債")

    # 2. 取得最新股價資料
    print("\n[2/7] 取得最新股價資料...")
    trading_date, stock_df = get_latest_trading_date()

    if stock_df is None:
        print("      ✗ 無法取得股價資料，程式終止")
        return

    print(f"      最新交易日: {trading_date}")
    print(f"      共 {len(stock_df)} 檔股票資料")

    # 3. 合併資料
    print("\n[3/7] 比對可轉債與股價...")

    # 準備股票資料（只保留需要的欄位）
    stock_df = stock_df[['stock_id', 'close']].copy()
    stock_df.columns = ['股票代碼', '最新收盤價']

    # 確保股票代碼為字串型別
    stock_df['股票代碼'] = stock_df['股票代碼'].astype(str)
    cb_df['股票代碼'] = cb_df['股票代碼'].astype(str)

    # 合併可轉債資料與股價資料
    merged_df = cb_df.merge(stock_df, on='股票代碼', how='left')

    # 移除沒有股價資料的
    merged_df = merged_df.dropna(subset=['最新收盤價'])
    print(f"      找到 {len(merged_df)} 檔有股價資料的可轉債")

    # 4. 篩選條件：轉換價格在收盤價的正負5%內
    print("\n[4/7] 篩選轉換價格在收盤價 ±5% 範圍內的標的...")

    merged_df['轉換價格'] = pd.to_numeric(merged_df['轉換價格'], errors='coerce')
    merged_df['差異百分比'] = ((merged_df['轉換價格'] - merged_df['最新收盤價']) / merged_df['最新收盤價'] * 100)

    # 篩選條件：-5% <= 差異百分比 <= 5%
    filtered_df = merged_df[
        (merged_df['差異百分比'] >= -5) &
        (merged_df['差異百分比'] <= 5)
    ].copy()

    print(f"      價格符合條件: {len(filtered_df)} 檔")

    if len(filtered_df) == 0:
        print("\n      沒有符合價格條件的可轉債")
        return pd.DataFrame()

    # 5. 取得股票成交量資料
    print(f"\n[5/7] 取得股票成交量資料（過去30天）...")
    stock_ids = filtered_df['股票代碼'].unique().tolist()
    stock_volume_df = get_stock_volume_data(stock_ids, trading_date)

    if len(stock_volume_df) == 0:
        print("      ✗ 無法取得股票成交量資料")
        return pd.DataFrame()

    print(f"      取得 {len(stock_volume_df)} 筆股票歷史資料")

    # 6. 取得可轉債成交量資料
    print(f"\n[6/7] 取得可轉債成交量資料（過去30天）...")
    cb_ids = filtered_df['債券代號'].unique().tolist()
    cb_volume_df = get_cb_volume_data(cb_ids, trading_date)

    if len(cb_volume_df) == 0:
        print("      ✗ 無法取得可轉債成交量資料")
        return pd.DataFrame()

    print(f"      取得 {len(cb_volume_df)} 筆可轉債歷史資料")

    # 7. 計算5MA並篩選成交量條件
    print(f"\n[7/7] 篩選成交量 > 5MA × 2 的標的...")

    # 計算股票5MA
    stock_volume_df['stock_id'] = stock_volume_df['stock_id'].astype(str)
    stock_volume_df = stock_volume_df.sort_values(['stock_id', 'date'])
    stock_volume_df['volume_5ma'] = stock_volume_df.groupby('stock_id')['Trading_Volume'].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    # 取最新一天的資料
    stock_latest = stock_volume_df[stock_volume_df['date'] == trading_date].copy()
    stock_latest['stock_volume_ok'] = stock_latest['Trading_Volume'] > (stock_latest['volume_5ma'] * 2)
    stock_latest = stock_latest[['stock_id', 'Trading_Volume', 'volume_5ma', 'stock_volume_ok']]
    stock_latest.columns = ['股票代碼', '股票成交量', '股票5MA', '股票量符合']

    # 計算可轉債5MA
    cb_volume_df = cb_volume_df.sort_values(['cb_id', 'date'])
    cb_volume_df['unit_5ma'] = cb_volume_df.groupby('cb_id')['unit'].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    # 取最新一天的資料
    cb_latest = cb_volume_df[cb_volume_df['date'] == trading_date].copy()
    cb_latest['cb_volume_ok'] = cb_latest['unit'] > (cb_latest['unit_5ma'] * 2)
    cb_latest = cb_latest[['cb_id', 'unit', 'unit_5ma', 'cb_volume_ok']]
    cb_latest.columns = ['債券代號', '可轉債成交量', '可轉債5MA', '可轉債量符合']

    # 確保債券代號型別一致
    cb_latest['債券代號'] = cb_latest['債券代號'].astype(str)
    filtered_df['債券代號'] = filtered_df['債券代號'].astype(str)

    # 合併成交量資料
    filtered_df = filtered_df.merge(stock_latest, on='股票代碼', how='left')
    filtered_df = filtered_df.merge(cb_latest, on='債券代號', how='left')

    # 篩選：兩者成交量都符合條件
    final_df = filtered_df[
        (filtered_df['股票量符合'] == True) &
        (filtered_df['可轉債量符合'] == True)
    ].copy()

    print(f"      股票量符合: {filtered_df['股票量符合'].sum()} 檔")
    print(f"      可轉債量符合: {filtered_df['可轉債量符合'].sum()} 檔")
    print(f"      雙重條件符合: {len(final_df)} 檔")

    # 整理輸出欄位
    final_df['公司名稱'] = final_df['標的債券'].str.replace(r'[一二三四五六七八九十]+$', '', regex=True).str.replace('KY', '').str.replace('永', '')

    result_df = final_df[[
        '公司名稱',
        '股票代碼',
        '最新收盤價',
        '標的債券',
        '債券代號',
        '轉換價格',
        '差異百分比',
        '股票成交量',
        '股票5MA',
        '可轉債成交量',
        '可轉債5MA'
    ]].copy()

    # 四捨五入
    result_df['最新收盤價'] = result_df['最新收盤價'].round(2)
    result_df['轉換價格'] = result_df['轉換價格'].round(2)
    result_df['差異百分比'] = result_df['差異百分比'].round(2)
    result_df['股票5MA'] = result_df['股票5MA'].round(0)
    result_df['可轉債5MA'] = result_df['可轉債5MA'].round(0)

    # 依差異百分比絕對值排序
    result_df['abs_diff'] = result_df['差異百分比'].abs()
    result_df = result_df.sort_values('abs_diff')
    result_df = result_df.drop('abs_diff', axis=1)

    # 匯出結果到 public/data/latest 目錄
    output_file_latest = '../public/data/latest/可轉債篩選.csv' if os.path.exists('../public/data/latest') else 'public/data/latest/可轉債篩選.csv'
    os.makedirs(os.path.dirname(output_file_latest), exist_ok=True)
    result_df.to_csv(output_file_latest, index=False, encoding='utf-8-sig')

    # 同時匯出到 history 目錄（以日期命名）
    history_date = trading_date.replace('-', '')
    output_file_history = f'../public/data/history/{history_date}/可轉債篩選.csv' if os.path.exists('../public/data/history') else f'public/data/history/{history_date}/可轉債篩選.csv'
    os.makedirs(os.path.dirname(output_file_history), exist_ok=True)
    result_df.to_csv(output_file_history, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 70)
    print("篩選完成！")
    print("=" * 70)
    print(f"\n最新資料: {output_file_latest}")
    print(f"歷史資料: {output_file_history}")
    print(f"交易日期: {trading_date}")
    print(f"符合條件: {len(result_df)} 檔可轉債")

    if len(result_df) > 0:
        print(f"\n結果預覽：")
        print(result_df.to_string(index=False))

        print("\n\n統計資訊：")
        print(f"  - 轉換價格低於股價（折價）: {len(result_df[result_df['差異百分比'] < 0])} 檔")
        print(f"  - 轉換價格高於股價（溢價）: {len(result_df[result_df['差異百分比'] > 0])} 檔")
        print(f"  - 平均股票成交量/5MA比值: {(result_df['股票成交量'] / result_df['股票5MA']).mean():.2f}x")
        print(f"  - 平均可轉債成交量/5MA比值: {(result_df['可轉債成交量'] / result_df['可轉債5MA']).mean():.2f}x")

    return result_df


if __name__ == "__main__":
    result = filter_convertible_bonds()
