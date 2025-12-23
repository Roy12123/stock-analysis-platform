"""
多策略交集分析
功能: 找出被至少3個策略同時篩選出來的股票
"""

import pandas as pd
import os
from datetime import datetime

def load_strategy_data():
    """載入各策略的篩選結果"""
    strategies = {}

    # 定義各策略的檔案路徑和欄位名稱
    strategy_files = {
        '隔日衝': '../data/latest/隔日衝_篩選結果.csv',
        '外資買超': '../data/latest/外資大量買超.csv',
        '投信連續': '../data/latest/投信連續買超.csv',
        '強勢股': '../data/latest/強勢股篩選.csv',
        '盤整突破': '../data/latest/盤整突破.csv',
        '大戶持有': '../data/latest/大戶持有比例差.csv',
    }

    # 支援從 python/ 或根目錄執行
    for name, file_path in strategy_files.items():
        alt_path = file_path.replace('../data/', 'data/')
        actual_path = file_path if os.path.exists(file_path) else alt_path

        try:
            df = pd.read_csv(actual_path, encoding='utf-8-sig')
            if len(df) > 0:
                # 確保股票代碼是字串型態
                if '股票代碼' in df.columns:
                    df['股票代碼'] = df['股票代碼'].astype(str)
                    strategies[name] = df
                    print(f"✅ {name}: {len(df)} 檔股票")
                else:
                    print(f"⚠️  {name}: 找不到「股票代碼」欄位")
            else:
                print(f"⚠️  {name}: 檔案為空")
        except FileNotFoundError:
            print(f"⚠️  {name}: 檔案不存在 ({actual_path})")
        except Exception as e:
            print(f"❌ {name}: 載入失敗 - {e}")

    return strategies

def analyze_intersections(strategies, min_strategies=3):
    """分析策略交集"""
    print(f"\n開始分析交集（至少符合 {min_strategies} 個策略）...")

    # 收集所有股票及其符合的策略
    stock_strategies = {}

    for strategy_name, df in strategies.items():
        for _, row in df.iterrows():
            stock_id = str(row['股票代碼'])
            company_name = row.get('公司名稱', '') or row.get('stock_name', '')

            if stock_id not in stock_strategies:
                stock_strategies[stock_id] = {
                    '股票代碼': stock_id,
                    '公司名稱': company_name,
                    '符合策略': []
                }

            stock_strategies[stock_id]['符合策略'].append(strategy_name)

    # 篩選出符合至少 min_strategies 個策略的股票
    result = []
    for stock_id, info in stock_strategies.items():
        strategy_count = len(info['符合策略'])
        if strategy_count >= min_strategies:
            result.append({
                '股票代碼': info['股票代碼'],
                '公司名稱': info['公司名稱'],
                '符合策略數': strategy_count,
                '符合策略': ', '.join(info['符合策略'])
            })

    # 按符合策略數排序（由多到少）
    result = sorted(result, key=lambda x: x['符合策略數'], reverse=True)

    return result

def main():
    print("=" * 80)
    print("多策略交集分析")
    print("=" * 80)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 載入各策略資料
    strategies = load_strategy_data()

    if len(strategies) == 0:
        print("\n❌ 沒有可用的策略資料")
        return

    print(f"\n總共載入 {len(strategies)} 個策略")

    # 分析交集（至少3個策略）
    result = analyze_intersections(strategies, min_strategies=3)

    print(f"\n🎯 找到 {len(result)} 檔股票符合至少3個策略\n")

    if len(result) > 0:
        # 建立 DataFrame
        df_result = pd.DataFrame(result)

        # 輸出檔案路徑
        output_file = '../data/latest/多策略交集.csv' if os.path.exists('../data/latest') else 'data/latest/多策略交集.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 儲存結果
        df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 結果已儲存至: {output_file}\n")

        # 顯示結果
        print("=" * 80)
        print("符合多策略的股票清單：")
        print("=" * 80)
        print(df_result.to_string(index=False))
        print("=" * 80)
    else:
        print("⚠️  目前沒有股票同時符合3個以上策略")

        # 建立空檔案
        df_empty = pd.DataFrame(columns=['股票代碼', '公司名稱', '符合策略數', '符合策略'])
        output_file = '../data/latest/多策略交集.csv' if os.path.exists('../data/latest') else 'data/latest/多策略交集.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_empty.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 空結果已儲存至: {output_file}")

if __name__ == "__main__":
    main()
