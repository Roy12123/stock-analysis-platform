"""
處置股票預測模組
根據注意股歷史記錄和即時行情，預測明天可能被處置的股票
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_data_fetcher import StockDataFetcher


class DisposalPredictor:
    def __init__(self):
        """初始化預測器"""
        self.fetcher = StockDataFetcher()

        # 注意股 → 處置股的條件
        self.disposal_conditions = {
            '連續3日': 3,
            '連續5日': 5,
            '近10日有6日': (10, 6),
            '近30日有12日': (30, 12)
        }

    def load_attention_history(self, csv_file):
        """
        載入注意股歷史記錄

        Args:
            csv_file: 注意股 CSV 檔案路徑

        Returns:
            DataFrame: 注意股歷史資料
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            return df
        except Exception as e:
            print(f"載入注意股記錄失敗: {e}")
            return pd.DataFrame()

    def analyze_attention_history(self, stock_id, history_df):
        """
        分析某股票的注意股歷史

        Args:
            stock_id: 股票代碼
            history_df: 注意股歷史資料 DataFrame

        Returns:
            dict: {
                'total_days': 總共被列入注意股天數,
                'recent_dates': 最近被列入注意股的日期列表,
                'consecutive_days': 連續天數,
                'days_in_10': 近10天內天數,
                'days_in_30': 近30天內天數,
                'will_dispose': 是否即將被處置,
                'dispose_reason': 處置原因,
                'stock_name': 證券名稱
            }
        """
        # 過濾出該股票的記錄（轉成整數比較）
        try:
            stock_id_int = int(stock_id)
            stock_records = history_df[history_df['證券代號'] == stock_id_int].copy()
        except:
            stock_records = history_df[history_df['證券代號'] == str(stock_id)].copy()

        if stock_records.empty:
            return {
                'total_days': 0,
                'recent_dates': [],
                'consecutive_days': 0,
                'days_in_10': 0,
                'days_in_30': 0,
                'will_dispose': False,
                'dispose_reason': None,
                'stock_name': '未知'
            }

        # 取得證券名稱（從第一筆記錄）
        stock_name = stock_records.iloc[0].get('證券名稱', '未知') if '證券名稱' in stock_records.columns else '未知'

        # 解析日期（民國年轉西元年）
        def roc_to_ad(roc_date):
            """民國年轉西元年"""
            try:
                # 移除可能的空白和BOM字元
                roc_date = str(roc_date).strip().replace('\ufeff', '')
                parts = roc_date.split('.')
                year = int(parts[0]) + 1911
                month = int(parts[1])
                day = int(parts[2])
                return datetime(year, month, day)
            except Exception as e:
                # print(f"日期解析失敗: {roc_date}, 錯誤: {e}")
                return None

        stock_records['西元日期'] = stock_records['日期'].apply(roc_to_ad)
        stock_records = stock_records.dropna(subset=['西元日期'])
        stock_records = stock_records.sort_values('西元日期')

        dates_list = stock_records['西元日期'].tolist()
        total_days = len(dates_list)

        # 計算連續天數（考慮只計算交易日）
        consecutive = self._count_consecutive_days(dates_list)

        # 計算近10天、近30天內的天數
        today = datetime.now()
        days_in_10 = sum(1 for d in dates_list if (today - d).days <= 10)
        days_in_30 = sum(1 for d in dates_list if (today - d).days <= 30)

        # 判斷是否即將被處置
        will_dispose = False
        dispose_reason = None

        if consecutive >= 3:
            will_dispose = True
            dispose_reason = f"連續{consecutive}日注意股（已達連續3日標準）"
        elif consecutive >= 5:
            will_dispose = True
            dispose_reason = f"連續{consecutive}日注意股（已達連續5日標準）"
        elif days_in_10 >= 6:
            will_dispose = True
            dispose_reason = f"近10日內{days_in_10}日注意股（已達6日標準）"
        elif days_in_30 >= 12:
            will_dispose = True
            dispose_reason = f"近30日內{days_in_30}日注意股（已達12日標準）"

        return {
            'total_days': total_days,
            'recent_dates': [d.strftime('%Y-%m-%d') for d in dates_list],
            'consecutive_days': consecutive,
            'days_in_10': days_in_10,
            'days_in_30': days_in_30,
            'will_dispose': will_dispose,
            'dispose_reason': dispose_reason,
            'stock_name': stock_name
        }

    def _count_consecutive_days(self, dates_list):
        """
        計算連續天數（只計算交易日）

        Args:
            dates_list: datetime 物件列表（已排序）

        Returns:
            int: 連續天數
        """
        if not dates_list:
            return 0

        # 從最新的日期往回算
        dates_list = sorted(dates_list, reverse=True)

        consecutive = 1
        for i in range(len(dates_list) - 1):
            diff = (dates_list[i] - dates_list[i+1]).days

            # 如果差距在1-3天內（考慮週末），視為連續
            if diff <= 3:
                consecutive += 1
            else:
                break

        return consecutive

    def calculate_next_day_thresholds(self, stock_id, market_index_data=None):
        """
        計算明天會觸發注意股的門檻值

        Args:
            stock_id: 股票代碼
            market_index_data: 大盤指數資料（選填，用於計算差幅）

        Returns:
            dict: {
                'stock_id': 股票代碼,
                'stock_name': 股票名稱,
                'latest_close': 最新收盤價,
                'thresholds': {
                    '振幅觸發條件': {
                        'amplitude_threshold': 振幅門檻值 (%),
                        'max_price_threshold': 最高價門檻,
                        'min_price_threshold': 最低價門檻
                    },
                    '漲跌幅觸發條件': {
                        'change_threshold': 漲跌幅門檻值 (%),
                        'price_up_threshold': 上漲價格門檻,
                        'price_down_threshold': 下跌價格門檻
                    },
                    '週轉率觸發條件': {
                        'turnover_threshold': 週轉率門檻值 (%),
                        'volume_threshold': 成交量門檻（股）
                    }
                }
            }
        """
        # 取得最近資料
        df = self.fetcher.get_recent_days(stock_id, days=10)

        if df.empty:
            return None

        latest = df.iloc[-1]
        prev_close = df.iloc[-2]['close'] if len(df) >= 2 else latest['close']

        # 取得股票基本資訊
        info = self.fetcher.get_stock_info(stock_id)
        stock_name = info['公司名稱'] if info else '未知'

        # 計算門檻值
        thresholds = {}

        # 1. 振幅觸發條件：振幅 > 9% 且與大盤差幅 ≥ 5%
        # 簡化：假設大盤振幅約 2-3%，所以振幅需 > 9%
        amplitude_threshold = 9.0  # %
        max_price_for_9pct = prev_close * (1 + amplitude_threshold / 100)
        min_price_for_9pct = prev_close * (1 - amplitude_threshold / 100)

        thresholds['振幅觸發條件'] = {
            'amplitude_threshold': amplitude_threshold,
            '說明': f'當日最高價 - 最低價 > 昨收 × {amplitude_threshold}%',
            '範例': f'若最高{max_price_for_9pct:.2f}、最低{min_price_for_9pct:.2f}，振幅={(max_price_for_9pct-min_price_for_9pct)/prev_close*100:.2f}%'
        }

        # 2. 漲跌幅觸發條件：漲跌幅 > 6% 且與大盤差幅 ≥ 4%
        # 簡化：假設大盤漲跌幅約 ±1%，所以需漲跌幅 > 6%
        change_threshold = 6.0  # %
        price_up_threshold = prev_close * (1 + change_threshold / 100)
        price_down_threshold = prev_close * (1 - change_threshold / 100)

        thresholds['漲跌幅觸發條件'] = {
            'change_threshold': change_threshold,
            '漲停門檻': f'{price_up_threshold:.2f}',
            '跌停門檻': f'{price_down_threshold:.2f}',
            '說明': f'收盤價 > {price_up_threshold:.2f} 或 < {price_down_threshold:.2f}'
        }

        # 3. 週轉率觸發條件：週轉率 > 10%
        # 週轉率 = 成交股數 / 發行股數 × 100%
        # 問題：我們沒有發行股數資料，需要估算或另外取得
        turnover_threshold = 10.0  # %

        # 嘗試估算發行股數（用最近的成交量均值反推）
        # 這只是粗略估計，實際應該從其他來源取得發行股數
        avg_volume = df['Trading_Volume'].mean()

        thresholds['週轉率觸發條件'] = {
            'turnover_threshold': turnover_threshold,
            '說明': '週轉率 = 成交股數 / 發行股數 × 100% > 10%',
            '注意': '需要發行股數資料才能準確計算',
            '參考平均成交量': f'{avg_volume:,.0f} 股'
        }

        return {
            'stock_id': stock_id,
            'stock_name': stock_name,
            'latest_date': latest['date'],
            'latest_close': latest['close'],
            'prev_close': prev_close,
            'thresholds': thresholds
        }

    def predict_tomorrow_disposal(self, attention_history_file):
        """
        預測明天可能被處置的股票

        Args:
            attention_history_file: 注意股歷史記錄 CSV 檔案

        Returns:
            DataFrame: 預測結果，包含股票代碼、原因、風險等級等
        """
        # 載入注意股歷史
        history_df = self.load_attention_history(attention_history_file)

        if history_df.empty:
            print("無注意股歷史記錄")
            return pd.DataFrame()

        # 取得所有被列入注意股的股票
        unique_stocks = history_df['證券代號'].unique()

        print(f"分析 {len(unique_stocks)} 檔注意股...")

        predictions = []

        for stock_id in unique_stocks:
            # 分析注意股歷史
            analysis = self.analyze_attention_history(stock_id, history_df)

            if analysis['will_dispose']:
                # 計算明天的門檻值
                thresholds = self.calculate_next_day_thresholds(stock_id)

                if thresholds:
                    predictions.append({
                        '證券代號': stock_id,
                        '證券名稱': analysis['stock_name'],  # 使用 analysis 中的證券名稱
                        '最新收盤價': thresholds['latest_close'],
                        '累計注意股次數': analysis['total_days'],
                        '連續天數': analysis['consecutive_days'],
                        '預測處置原因': analysis['dispose_reason'],
                        '風險等級': self._calculate_risk_level(analysis),
                        '漲幅門檻': f"+{thresholds['thresholds']['漲跌幅觸發條件']['change_threshold']}% (>{thresholds['thresholds']['漲跌幅觸發條件']['漲停門檻']})",
                        '跌幅門檻': f"-{thresholds['thresholds']['漲跌幅觸發條件']['change_threshold']}% (<{thresholds['thresholds']['漲跌幅觸發條件']['跌停門檻']})"
                    })

        if predictions:
            result_df = pd.DataFrame(predictions)
            result_df = result_df.sort_values('風險等級', ascending=False)
            return result_df
        else:
            return pd.DataFrame()

    def _calculate_risk_level(self, analysis):
        """
        計算風險等級（即將被處置的機率）

        Args:
            analysis: 注意股分析結果

        Returns:
            str: 高/中/低
        """
        if analysis['consecutive_days'] >= 5:
            return '極高'
        elif analysis['consecutive_days'] >= 3:
            return '高'
        elif analysis['days_in_10'] >= 6:
            return '高'
        elif analysis['days_in_30'] >= 12:
            return '中'
        elif analysis['consecutive_days'] >= 2:
            return '中'
        else:
            return '低'


def main():
    """測試用主程式"""
    print("="*60)
    print("處置股票預測系統測試")
    print("="*60)

    predictor = DisposalPredictor()

    # 測試1: 分析單一股票的注意股歷史
    print("\n[測試1] 分析 3057 喬鼎的注意股歷史")

    history_file = '注意股票_近7日.csv'
    history_df = predictor.load_attention_history(history_file)

    if not history_df.empty:
        analysis = predictor.analyze_attention_history('3057', history_df)

        print(f"累計注意股天數: {analysis['total_days']}")
        print(f"連續天數: {analysis['consecutive_days']}")
        print(f"近10日天數: {analysis['days_in_10']}")
        print(f"近30日天數: {analysis['days_in_30']}")
        print(f"是否即將處置: {'是' if analysis['will_dispose'] else '否'}")
        if analysis['dispose_reason']:
            print(f"處置原因: {analysis['dispose_reason']}")

    # 測試2: 計算明天的門檻值
    print("\n" + "="*60)
    print("[測試2] 計算 3057 喬鼎明天的注意股門檻")

    thresholds = predictor.calculate_next_day_thresholds('3057')

    if thresholds:
        print(f"\n股票: {thresholds['stock_name']} ({thresholds['stock_id']})")
        print(f"最新收盤價: {thresholds['latest_close']}")
        print(f"昨收: {thresholds['prev_close']}")

        print(f"\n明天觸發注意股的條件:")
        for condition, details in thresholds['thresholds'].items():
            print(f"\n【{condition}】")
            for key, value in details.items():
                print(f"  {key}: {value}")

    # 測試3: 預測明天可能被處置的股票
    print("\n" + "="*60)
    print("[測試3] 預測明天可能被處置的股票")

    predictions = predictor.predict_tomorrow_disposal(history_file)

    if not predictions.empty:
        print(f"\n發現 {len(predictions)} 檔股票可能被處置:")
        print(predictions.to_string(index=False))
    else:
        print("\n目前無股票達到處置標準")


if __name__ == '__main__':
    main()
