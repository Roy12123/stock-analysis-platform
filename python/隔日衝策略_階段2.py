"""
隔日衝策略 - 階段2: 即時篩選
執行時間: 每日下午 13:20 台北時間
功能: 抓取即時價格,套用篩選條件,輸出符合條件的股票
"""

import requests
import pandas as pd
from datetime import datetime
import time
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

def realtime_screen(token):
    """
    階段2：即時篩選
    """
    print_header(f"階段2：即時篩選 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    headers = {"Authorization": f"Bearer {token}"}

    # 讀取歷史資料
    print("\n[1/3] 讀取歷史資料...")
    # 支援從 python/ 目錄或根目錄執行
    historical_file = '../data/latest/隔日衝_歷史資料.csv' if os.path.exists('../data/latest/隔日衝_歷史資料.csv') else 'data/latest/隔日衝_歷史資料.csv'

    try:
        df_historical = pd.read_csv(historical_file)
        # 確保股票代碼是字串型態
        df_historical['股票代碼'] = df_historical['股票代碼'].astype(str)
        print(f"✅ 成功讀取 {len(df_historical)} 檔股票的歷史資料")
    except FileNotFoundError:
        print(f"❌ 找不到 {historical_file}")
        print("   請確認階段1已執行完成")
        return False

    # 抓取即時價格（分批查詢 + 重試機制）
    print("\n[2/3] 抓取即時價格...")
    all_stock_ids = df_historical['股票代碼'].astype(str).tolist()
    url_realtime = "https://api.finmindtrade.com/api/v4/taiwan_stock_tick_snapshot"

    # 分批查詢（每批500檔，避免URL過長）
    batch_size = 500
    batches = [all_stock_ids[i:i+batch_size] for i in range(0, len(all_stock_ids), batch_size)]

    print(f"  將 {len(all_stock_ids)} 檔股票分成 {len(batches)} 批查詢")

    all_realtime_data = []
    max_retries = 10

    for batch_idx, batch in enumerate(batches, 1):
        print(f"\n  查詢第 {batch_idx}/{len(batches)} 批 ({len(batch)} 檔)...")

        success = False
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    print(f"    第 {attempt} 次嘗試...")

                parameter = {"data_id": batch}
                resp = requests.get(url_realtime, headers=headers, params=parameter, timeout=30)

                if resp.status_code != 200:
                    print(f"    ⚠️  HTTP {resp.status_code}")
                    if attempt < max_retries:
                        print(f"    等待2秒後重試...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"    回應: {resp.text[:200]}")
                        break

                if not resp.text or len(resp.text.strip()) == 0:
                    print(f"    ⚠️  空白回應")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    else:
                        break

                try:
                    data = resp.json()
                except Exception as json_error:
                    print(f"    ⚠️  JSON解析失敗: {json_error}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    else:
                        break

                if "data" in data and len(data["data"]) > 0:
                    all_realtime_data.extend(data["data"])
                    print(f"    ✅ 成功取得 {len(data['data'])} 檔")
                    success = True
                    break
                else:
                    print(f"    ⚠️  無資料")
                    if "msg" in data:
                        print(f"    訊息: {data['msg']}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue

            except requests.exceptions.Timeout:
                print(f"    ⚠️  逾時")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
            except Exception as e:
                print(f"    ⚠️  錯誤: {e}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue

        if not success:
            print(f"    ❌ 第 {batch_idx} 批查詢失敗（已嘗試{max_retries}次）")

        # 批次間稍微延遲
        if batch_idx < len(batches):
            time.sleep(0.5)

    if len(all_realtime_data) == 0:
        print("\n❌ 沒有成功取得任何即時資料")
        return False

    df_realtime = pd.DataFrame(all_realtime_data)
    print(f"\n✅ 總共成功取得 {len(df_realtime)} 檔股票的即時資料")

    # 確保數值型態正確
    df_realtime['open'] = pd.to_numeric(df_realtime['open'], errors='coerce')
    df_realtime['close'] = pd.to_numeric(df_realtime['close'], errors='coerce')
    df_realtime['high'] = pd.to_numeric(df_realtime['high'], errors='coerce')
    df_realtime['low'] = pd.to_numeric(df_realtime['low'], errors='coerce')
    df_realtime['total_volume'] = pd.to_numeric(df_realtime['total_volume'], errors='coerce')
    df_realtime['change_rate'] = pd.to_numeric(df_realtime['change_rate'], errors='coerce')

    # 套用篩選條件
    print("\n[3/3] 套用篩選條件...")

    df_combined = df_historical.merge(
        df_realtime,
        left_on='股票代碼',
        right_on='stock_id',
        how='inner'
    )

    print(f"  合併後總共 {len(df_combined)} 檔股票")

    # 計算當日實體、上下影線
    df_combined['current_body'] = abs(df_combined['close'] - df_combined['open'])
    df_combined['upper_shadow'] = df_combined['high'] - df_combined[['open', 'close']].max(axis=1)
    df_combined['lower_shadow'] = df_combined[['open', 'close']].min(axis=1) - df_combined['low']

    df_filtered = df_combined.copy()
    initial_count = len(df_filtered)

    # 條件1: 紅K棒
    df_filtered = df_filtered[df_filtered['close'] > df_filtered['open']]
    print(f"  ✅ 條件1 (紅K棒): {len(df_filtered)} 檔符合 (篩掉 {initial_count - len(df_filtered)} 檔)")

    # 條件2: 實體 > 前日1.5倍
    cond2_count = len(df_filtered)
    df_filtered = df_filtered[df_filtered['current_body'] > df_filtered['prev_body'] * 1.5]
    print(f"  ✅ 條件2 (實體>前日1.5倍): {len(df_filtered)} 檔符合 (篩掉 {cond2_count - len(df_filtered)} 檔)")

    # 條件3: 量 > 5日均量2倍
    cond3_count = len(df_filtered)
    df_filtered = df_filtered[df_filtered['total_volume'] > df_filtered['avg_volume_5d'] * 2]
    print(f"  ✅ 條件3 (量>5日均量2倍): {len(df_filtered)} 檔符合 (篩掉 {cond3_count - len(df_filtered)} 檔)")

    # 條件4: 上影線 < 實體30%
    cond4_count = len(df_filtered)
    df_filtered = df_filtered[
        (df_filtered['current_body'] > 0) &
        (df_filtered['upper_shadow'] < df_filtered['current_body'] * 0.3)
    ]
    print(f"  ✅ 條件4 (上影線<實體30%): {len(df_filtered)} 檔符合 (篩掉 {cond4_count - len(df_filtered)} 檔)")

    # 條件5: 下影線 < 實體30%
    cond5_count = len(df_filtered)
    df_filtered = df_filtered[
        (df_filtered['current_body'] > 0) &
        (df_filtered['lower_shadow'] < df_filtered['current_body'] * 0.3)
    ]
    print(f"  ✅ 條件5 (下影線<實體30%): {len(df_filtered)} 檔符合 (篩掉 {cond5_count - len(df_filtered)} 檔)")

    # 條件6: 收在高點
    cond6_count = len(df_filtered)
    df_filtered = df_filtered[df_filtered['close'] >= df_filtered['high'] * 0.98]
    print(f"  ✅ 條件6 (收在高點): {len(df_filtered)} 檔符合 (篩掉 {cond6_count - len(df_filtered)} 檔)")

    # 條件7: 量 >= 10000張
    cond7_count = len(df_filtered)
    df_filtered = df_filtered[df_filtered['total_volume'] >= 10000]
    print(f"  ✅ 條件7 (量>=10000張): {len(df_filtered)} 檔符合 (篩掉 {cond7_count - len(df_filtered)} 檔)")

    print(f"\n🎯 最終篩選結果: {len(df_filtered)} 檔股票符合所有條件")

    # 整理輸出資料
    if len(df_filtered) > 0:
        df_output = df_filtered[[
            '股票代碼', '公司名稱', 'close', 'change_rate',
            'foreign_yesterday', 'foreign_3days',
            'trust_yesterday', 'trust_3days'
        ]].copy()

        df_output.columns = [
            '股票代碼', '公司名稱', '當下價格', '當下漲跌幅(%)',
            '外資昨日買超(張)', '外資前三日總買超(張)',
            '投信昨日買超(張)', '投信前三日總買超(張)'
        ]

        df_output = df_output.sort_values('當下漲跌幅(%)', ascending=False)

        # 儲存到 data/latest 目錄（支援從 python/ 或根目錄執行）
        output_file = '../data/latest/隔日衝_篩選結果.csv' if os.path.exists('../data/latest') else 'data/latest/隔日衝_篩選結果.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_output.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n✅ 篩選結果已儲存至: {output_file}")
        print("\n" + "=" * 80)
        print("符合條件的股票清單：")
        print("=" * 80)
        print(df_output.to_string(index=False))
    else:
        print("\n⚠️  今天沒有股票符合所有條件")

        # 即使沒有資料也建立空檔案
        df_empty = pd.DataFrame(columns=[
            '股票代碼', '公司名稱', '當下價格', '當下漲跌幅(%)',
            '外資昨日買超(張)', '外資前三日總買超(張)',
            '投信昨日買超(張)', '投信前三日總買超(張)'
        ])
        output_file = '../data/latest/隔日衝_篩選結果.csv' if os.path.exists('../data/latest') else 'data/latest/隔日衝_篩選結果.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_empty.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 空結果已儲存至: {output_file}")

    return True

def main():
    """
    主程式
    """
    print_header("隔日衝策略 - 階段2: 即時篩選")
    print(f"📅 執行日期: {datetime.now().strftime('%Y年%m月%d日 %A')}")
    print(f"⏰ 啟動時間: {datetime.now().strftime('%H:%M:%S')}")
    print_separator()

    # 讀取 token
    token = load_token()

    # 執行階段2：即時篩選
    success = realtime_screen(token)

    if success:
        print("\n" + "=" * 80)
        print("🎉 階段2完成！篩選結果已輸出")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 階段2失敗")
        print("=" * 80)
        exit(1)

if __name__ == "__main__":
    main()
