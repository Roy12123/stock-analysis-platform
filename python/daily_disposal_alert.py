#!/usr/bin/env python3
"""
每日處置股票預警系統
執行流程：
1. 爬取最新注意股票公告
2. 分析歷史記錄，預測明天可能被處置的股票
3. 計算明天的觸發門檻（價格、漲跌幅等）
4. 輸出預警報告
"""

from datetime import datetime, timedelta
from crawl_attention_stocks import TWSEAttentionStockCrawler
from disposal_predictor import DisposalPredictor
import pandas as pd
import os


def main():
    """主程式"""
    print("="*80)
    print(" "*25 + "處置股票每日預警系統")
    print("="*80)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # ===== 步驟1: 爬取最新注意股票 =====
    print("\n【步驟1】爬取最新注意股票公告...")
    print("-"*80)

    # 初始化爬蟲（不過濾股票清單，顯示所有注意股票）
    crawler = TWSEAttentionStockCrawler(stock_list_path=None)

    # 爬取最近30天的資料（確保有足夠的歷史記錄）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    attention_df = crawler.fetch_date_range(
        start_date.strftime('%Y%m%d'),
        end_date.strftime('%Y%m%d')
    )

    if attention_df.empty:
        print("\n⚠️  近30天無注意股票資料")

        # 建立空的輸出檔案
        df_empty = pd.DataFrame(columns=[
            '股票代碼', '公司名稱', '風險等級',
            '累計注意股次數', '連續天數', '預測處置原因',
            '最新收盤價', '漲幅門檻', '跌幅門檻'
        ])

        output_file = '../data/latest/處置注意股.csv' if os.path.exists('../data/latest') else 'data/latest/處置注意股.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_empty.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 空結果已儲存至: {output_file}")
        print("="*80)
        return

    # 清理並儲存歷史資料（臨時檔案）
    clean_df = crawler.parse_and_clean_data(attention_df)

    # 使用臨時檔案路徑
    temp_history_file = f'注意股票_歷史_{datetime.now().strftime("%Y%m%d")}.csv'
    temp_history_path = os.path.join(os.path.dirname(__file__), temp_history_file)
    clean_df.to_csv(temp_history_path, index=False, encoding='utf-8-sig')

    print(f"\n✓ 成功抓取 {len(clean_df)} 筆注意股票記錄")
    print(f"✓ 涵蓋 {clean_df['證券代號'].nunique()} 檔不同股票")

    # ===== 步驟2: 分析並預測處置股票 =====
    print("\n【步驟2】分析注意股歷史，預測明天可能被處置的股票...")
    print("-"*80)

    predictor = DisposalPredictor()
    predictions = predictor.predict_tomorrow_disposal(temp_history_path)

    if predictions.empty:
        print("\n✓ 目前無股票達到處置標準")

        # 建立空的輸出檔案
        df_empty = pd.DataFrame(columns=[
            '股票代碼', '公司名稱', '風險等級',
            '累計注意股次數', '連續天數', '預測處置原因',
            '最新收盤價', '漲幅門檻', '跌幅門檻'
        ])

        output_file = '../data/latest/處置注意股.csv' if os.path.exists('../data/latest') else 'data/latest/處置注意股.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_empty.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 空結果已儲存至: {output_file}")

        # 刪除臨時檔案
        if os.path.exists(temp_history_path):
            os.remove(temp_history_path)

        print("="*80)
        return

    print(f"\n⚠️  發現 {len(predictions)} 檔股票可能被處置！")

    # ===== 步驟3: 輸出詳細預警報告（終端機顯示）=====
    print("\n【步驟3】處置預警明細報告")
    print("="*80)

    for idx, row in predictions.iterrows():
        print(f"\n股票 {idx+1}: {row['證券代號']} {row['證券名稱']}")
        print(f"{'-'*80}")
        print(f"風險等級: {'🔴' if row['風險等級'] in ['極高', '高'] else '🟡'} {row['風險等級']}")
        print(f"預測原因: {row['預測處置原因']}")
        print(f"")
        print(f"注意股統計:")
        print(f"  - 累計次數: {row['累計注意股次數']}次")
        print(f"  - 連續天數: {row['連續天數']}天")
        print(f"")
        print(f"最新股價:")
        print(f"  - 最新收盤: {row['最新收盤價']}")
        print(f"")
        print(f"明天觸發注意股的門檻:")
        print(f"  - 漲幅超過: {row['漲幅門檻']}")
        print(f"  - 跌幅超過: {row['跌幅門檻']}")

    # ===== 步驟4: 儲存為網站用的 CSV =====
    print("\n" + "="*80)
    print("【步驟4】儲存網站用 CSV...")
    print("-"*80)

    # 選擇需要的欄位並重新命名
    predictions_web = predictions[[
        '證券代號', '證券名稱', '風險等級',
        '累計注意股次數', '連續天數', '預測處置原因',
        '最新收盤價', '漲幅門檻', '跌幅門檻'
    ]].copy()

    # 重新命名欄位
    predictions_web.columns = [
        '股票代碼', '公司名稱', '風險等級',
        '累計注意股次數', '連續天數', '預測處置原因',
        '最新收盤價', '漲幅門檻', '跌幅門檻'
    ]

    # 儲存到 data/latest 目錄
    output_file = '../data/latest/處置注意股.csv' if os.path.exists('../data/latest') else 'data/latest/處置注意股.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    predictions_web.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ 網站用 CSV 已儲存: {output_file}")

    # ===== 統計摘要 =====
    print("\n" + "="*80)
    print("統計摘要")
    print("="*80)
    print(f"極高風險: {len(predictions[predictions['風險等級']=='極高'])} 檔")
    print(f"高風險:   {len(predictions[predictions['風險等級']=='高'])} 檔")
    print(f"中風險:   {len(predictions[predictions['風險等級']=='中'])} 檔")
    print(f"低風險:   {len(predictions[predictions['風險等級']=='低'])} 檔")

    print("\n高風險股票清單:")
    high_risk = predictions[predictions['風險等級'].isin(['極高', '高'])]
    for _, row in high_risk.iterrows():
        print(f"  🔴 {row['證券代號']} {row['證券名稱']:8s} - {row['預測處置原因']}")

    # 刪除臨時檔案
    if os.path.exists(temp_history_path):
        os.remove(temp_history_path)
        print(f"\n✓ 已清理臨時檔案: {temp_history_file}")

    print("\n" + "="*80)
    print("執行完成！")
    print("="*80)


if __name__ == '__main__':
    main()
