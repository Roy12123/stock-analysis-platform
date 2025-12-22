"""
隔日衝策略 - 階段1: 準備歷史資料
執行時間: 每日早上 7:00 台北時間
功能: 抓取最近15天的日K資料和法人買賣資料,計算技術指標
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import numpy as np
import os

def print_separator(char="=", length=80):
    print(char * length)

def print_header(text):
    print_separator()
    print(text)
    print_separator()

def load_token():
    """從環境變數或檔案讀取 FinMind API Token"""
    # 優先從環境變數讀取 (GitHub Actions)
    token = os.environ.get('FINMIND_TOKEN', '')
    if token:
        print("✅ 從環境變數讀取 Token")
        return token

    # 本地測試時從檔案讀取
    try:
        with open('./token', 'r') as f:
            token = f.read().strip()
            print("✅ 從檔案讀取 Token")
            return token
    except FileNotFoundError:
        print("❌ 找不到 Token")
        raise

def prepare_historical_data(token):
    """
    階段1：準備歷史資料
    """
    print_header("階段1：準備歷史資料")

    headers = {"Authorization": f"Bearer {token}"}

    # 讀取股票清單
    print("\n[1/5] 讀取股票清單...")
    df_stocks = pd.read_csv('(all)stock_info_list.csv')
    all_stock_ids = df_stocks['股票代碼'].astype(str).tolist()
    print(f"✅ 總共 {len(all_stock_ids)} 檔股票")

    # 設定日期範圍
    today = datetime.now()
    start_date = (today - timedelta(days=15)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    print(f"📅 資料日期範圍: {start_date} ~ {end_date}")

    # ========================================================================
    # 抓取日K資料
    # ========================================================================
    print("\n[2/5] 抓取日K資料（每檔股票最近10天）...")
    print("⚠️  這會需要一些時間，請耐心等待...")

    url_daily = "https://api.finmindtrade.com/api/v4/data"
    all_daily_data = []
    failed_stocks = []

    start_time = time.time()
    for idx, stock_id in enumerate(all_stock_ids):
        try:
            parameter = {
                "dataset": "TaiwanStockPriceAdj",
                "data_id": stock_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            resp = requests.get(url_daily, headers=headers, params=parameter, timeout=10)
            data = resp.json()

            if "data" in data and len(data["data"]) > 0:
                df_stock = pd.DataFrame(data["data"])
                all_daily_data.append(df_stock)

            # 每100檔顯示進度
            if (idx + 1) % 100 == 0:
                elapsed = time.time() - start_time
                progress = (idx + 1) / len(all_stock_ids) * 100
                avg_time = elapsed / (idx + 1)
                remaining = avg_time * (len(all_stock_ids) - idx - 1)
                print(f"  進度: {idx + 1}/{len(all_stock_ids)} ({progress:.1f}%) - 已耗時: {elapsed:.0f}秒 - 預計剩餘: {remaining:.0f}秒")

            time.sleep(0.05)

        except Exception as e:
            failed_stocks.append(stock_id)
            if len(failed_stocks) <= 5:
                print(f"  ⚠️  股票 {stock_id} 失敗: {e}")

    elapsed = time.time() - start_time
    print(f"\n✅ 日K資料抓取完成！總耗時: {elapsed:.1f}秒")
    print(f"   成功: {len(all_daily_data)} 檔 | 失敗: {len(failed_stocks)} 檔")

    if len(all_daily_data) == 0:
        print("❌ 沒有成功抓取任何日K資料，程式終止")
        return False

    # 合併所有日K資料
    df_daily_all = pd.concat(all_daily_data, ignore_index=True)
    print(f"   總共 {len(df_daily_all)} 筆日K資料")

    # ========================================================================
    # 計算技術指標
    # ========================================================================
    print("\n[3/5] 計算技術指標...")

    df_daily_all['Trading_Volume'] = pd.to_numeric(df_daily_all['Trading_Volume'], errors='coerce')
    df_daily_all['open'] = pd.to_numeric(df_daily_all['open'], errors='coerce')
    df_daily_all['close'] = pd.to_numeric(df_daily_all['close'], errors='coerce')
    df_daily_all = df_daily_all.sort_values(['stock_id', 'date'])

    result_list = []
    for stock_id, group in df_daily_all.groupby('stock_id'):
        group = group.sort_values('date').tail(6)
        if len(group) < 2:
            continue

        latest = group.iloc[-1]
        prev_body = abs(latest['close'] - latest['open'])

        if len(group) >= 5:
            volumes_5d = group.tail(5)['Trading_Volume'].values / 1000
            avg_volume_5d = np.mean(volumes_5d)
        else:
            avg_volume_5d = np.mean(group['Trading_Volume'].values) / 1000

        result_list.append({
            'stock_id': stock_id,
            'prev_date': latest['date'],
            'prev_body': prev_body,
            'avg_volume_5d': avg_volume_5d,
        })

    df_indicators = pd.DataFrame(result_list)
    print(f"✅ 成功計算 {len(df_indicators)} 檔股票的技術指標")

    # ========================================================================
    # 抓取法人買賣資料
    # ========================================================================
    print("\n[4/5] 抓取法人買賣資料...")

    all_institution_data = []
    failed_institution = []

    start_time = time.time()
    for idx, stock_id in enumerate(all_stock_ids):
        try:
            parameter = {
                "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
                "data_id": stock_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            resp = requests.get(url_daily, headers=headers, params=parameter, timeout=10)
            data = resp.json()

            if "data" in data and len(data["data"]) > 0:
                df_inst = pd.DataFrame(data["data"])
                all_institution_data.append(df_inst)

            if (idx + 1) % 100 == 0:
                elapsed = time.time() - start_time
                progress = (idx + 1) / len(all_stock_ids) * 100
                avg_time = elapsed / (idx + 1)
                remaining = avg_time * (len(all_stock_ids) - idx - 1)
                print(f"  進度: {idx + 1}/{len(all_stock_ids)} ({progress:.1f}%) - 已耗時: {elapsed:.0f}秒 - 預計剩餘: {remaining:.0f}秒")

            time.sleep(0.05)

        except Exception as e:
            failed_institution.append(stock_id)

    elapsed = time.time() - start_time
    print(f"\n✅ 法人資料抓取完成！總耗時: {elapsed:.1f}秒")
    print(f"   成功: {len(all_institution_data)} 檔 | 失敗: {len(failed_institution)} 檔")

    # 處理法人資料
    if len(all_institution_data) > 0:
        df_institution_all = pd.concat(all_institution_data, ignore_index=True)
        print(f"   總共 {len(df_institution_all)} 筆法人資料")

        institution_result = []
        for stock_id, group in df_institution_all.groupby('stock_id'):
            group = group.sort_values('date')

            foreign = group[group['name'] == 'Foreign_Investor'].tail(3)
            trust = group[group['name'] == 'Investment_Trust'].tail(3)

            if len(foreign) > 0:
                foreign['net'] = foreign['buy'] - foreign['sell']
                foreign_yesterday = foreign.iloc[-1]['net'] / 1000 if len(foreign) >= 1 else 0
                foreign_3days = foreign['net'].sum() / 1000 if len(foreign) >= 1 else 0
            else:
                foreign_yesterday = 0
                foreign_3days = 0

            if len(trust) > 0:
                trust['net'] = trust['buy'] - trust['sell']
                trust_yesterday = trust.iloc[-1]['net'] / 1000 if len(trust) >= 1 else 0
                trust_3days = trust['net'].sum() / 1000 if len(trust) >= 1 else 0
            else:
                trust_yesterday = 0
                trust_3days = 0

            institution_result.append({
                'stock_id': stock_id,
                'foreign_yesterday': round(foreign_yesterday, 2),
                'foreign_3days': round(foreign_3days, 2),
                'trust_yesterday': round(trust_yesterday, 2),
                'trust_3days': round(trust_3days, 2),
            })

        df_institution_summary = pd.DataFrame(institution_result)
        print(f"✅ 成功處理 {len(df_institution_summary)} 檔股票的法人資料")
    else:
        print("⚠️  沒有法人資料，將使用空值")
        df_institution_summary = pd.DataFrame({
            'stock_id': all_stock_ids,
            'foreign_yesterday': 0,
            'foreign_3days': 0,
            'trust_yesterday': 0,
            'trust_3days': 0,
        })

    # ========================================================================
    # 合併資料並儲存
    # ========================================================================
    print("\n[5/5] 合併資料並儲存...")

    df_final = df_stocks.copy()
    df_final['股票代碼'] = df_final['股票代碼'].astype(str)

    df_final = df_final.merge(df_indicators, left_on='股票代碼', right_on='stock_id', how='left')
    df_final = df_final.merge(df_institution_summary, left_on='股票代碼', right_on='stock_id', how='left')

    df_final['prev_body'] = df_final['prev_body'].fillna(0)
    df_final['avg_volume_5d'] = df_final['avg_volume_5d'].fillna(0)
    df_final['foreign_yesterday'] = df_final['foreign_yesterday'].fillna(0)
    df_final['foreign_3days'] = df_final['foreign_3days'].fillna(0)
    df_final['trust_yesterday'] = df_final['trust_yesterday'].fillna(0)
    df_final['trust_3days'] = df_final['trust_3days'].fillna(0)

    df_output = df_final[[
        '股票代碼', '公司名稱', '公司產業', '上市櫃',
        'prev_body', 'avg_volume_5d',
        'foreign_yesterday', 'foreign_3days',
        'trust_yesterday', 'trust_3days'
    ]]

    # 儲存到 data/latest 目錄（支援從 python/ 或根目錄執行）
    output_file = '../data/latest/隔日衝_歷史資料.csv' if os.path.exists('../data/latest') else 'data/latest/隔日衝_歷史資料.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_output.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"✅ 資料已儲存至: {output_file}")
    print(f"   總共 {len(df_output)} 檔股票")

    return True

def main():
    """
    主程式
    """
    print_header("隔日衝策略 - 階段1: 準備歷史資料")
    print(f"📅 執行日期: {datetime.now().strftime('%Y年%m月%d日 %A')}")
    print(f"⏰ 啟動時間: {datetime.now().strftime('%H:%M:%S')}")
    print_separator()

    # 讀取 token
    token = load_token()

    # 執行階段1：準備歷史資料
    success = prepare_historical_data(token)

    if success:
        print("\n" + "=" * 80)
        print("🎉 階段1完成！歷史資料已準備就緒")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 階段1失敗")
        print("=" * 80)
        exit(1)

if __name__ == "__main__":
    main()
