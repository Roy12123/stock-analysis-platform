"""
證交所注意股票爬蟲程式
抓取 TWSE 公布的注意有價證券資訊
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

class TWSEAttentionStockCrawler:
    def __init__(self, stock_list_path='../(all)stock_info_list.csv'):
        """
        初始化爬蟲

        Args:
            stock_list_path: 股票清單CSV檔案路徑
        """
        self.base_url = 'https://www.twse.com.tw'
        self.notice_url = f'{self.base_url}/rwd/zh/announcement/notice'

        # 讀取有效股票代碼清單
        self.valid_stocks = self._load_valid_stocks(stock_list_path)
        if self.valid_stocks:
            print(f"已載入 {len(self.valid_stocks)} 檔有效股票")
        else:
            print("未載入股票清單，將顯示所有注意股票")

        # 設定 headers 避免被擋
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_valid_stocks(self, file_path):
        """載入有效股票代碼清單"""
        if not file_path:
            return None

        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            # 將股票代碼轉為字串格式，並去除可能的空白
            stock_codes = df['股票代碼'].astype(str).str.strip().tolist()
            return set(stock_codes)
        except Exception as e:
            print(f"讀取股票清單失敗: {e}，將顯示所有注意股票")
            return None

    def fetch_attention_stocks(self, start_date=None, end_date=None):
        """
        抓取指定日期範圍的注意股票資訊

        Args:
            start_date: 起始日期字串，格式 'YYYYMMDD'，若為 None 則使用今日
            end_date: 結束日期字串，格式 'YYYYMMDD'，若為 None 則使用今日

        Returns:
            DataFrame: 注意股票資料
        """
        if start_date is None:
            start_date = datetime.now().strftime('%Y%m%d')
        if end_date is None:
            end_date = start_date

        # 證交所 API 參數
        params = {
            'response': 'json',
            'startDate': start_date,
            'endDate': end_date
        }

        print(f"正在抓取 {start_date} 至 {end_date} 的注意股票資訊...")
        print(f"API URL: {self.base_url}/rwd/zh/announcement/notice")

        try:
            response = requests.get(
                f'{self.base_url}/rwd/zh/announcement/notice',
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            # 解析 JSON 資料
            data = response.json()

            if 'data' not in data or not data['data']:
                print(f"查無 {start_date} 至 {end_date} 的注意股票資料")
                return pd.DataFrame()

            # 解析資料：data 是 list of lists 格式
            # fields: ["編號","證券代號","證券名稱","累計次數","注意交易資訊","日期","收盤價","本益比"]
            fields = data.get('fields', [])
            rows = data.get('data', [])

            # 轉換為 DataFrame
            df = pd.DataFrame(rows, columns=fields)

            print(f"原始資料共 {len(df)} 筆")

            # 過濾：只保留在 valid_stocks 清單中的股票（如果有清單的話）
            if self.valid_stocks:
                df = df[df['證券代號'].isin(self.valid_stocks)]
                print(f"過濾後剩餘 {len(df)} 筆（在股票清單中）")
            else:
                print(f"未過濾，保留所有 {len(df)} 筆資料")

            # 新增查詢日期欄位
            df['查詢起始日'] = start_date
            df['查詢結束日'] = end_date

            return df

        except requests.exceptions.RequestException as e:
            print(f"網路請求失敗: {e}")
            return pd.DataFrame()
        except json.JSONDecodeError as e:
            print(f"JSON 解析失敗: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"發生錯誤: {e}")
            return pd.DataFrame()

    def fetch_date_range(self, start_date, end_date):
        """
        抓取日期區間的注意股票資訊（直接使用一次API呼叫）

        Args:
            start_date: 起始日期 'YYYYMMDD'
            end_date: 結束日期 'YYYYMMDD'

        Returns:
            DataFrame: 彙整的注意股票資料
        """
        # 證交所API支援日期區間查詢，不需要一天一天抓
        df = self.fetch_attention_stocks(start_date, end_date)

        if not df.empty:
            print(f"\n總共抓取 {len(df)} 筆注意股票資料")
        else:
            print("未抓取到任何資料")

        return df

    def save_to_csv(self, df, filename=None):
        """
        儲存資料到 CSV 檔案

        Args:
            df: DataFrame
            filename: 檔案名稱，若為 None 則自動產生
        """
        if df.empty:
            print("無資料可儲存")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'注意股票_{timestamp}.csv'

        # 確保儲存在處置project資料夾內
        output_path = os.path.join(os.path.dirname(__file__), filename)

        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"已儲存至: {output_path}")
        print(f"共 {len(df)} 筆資料")

    def parse_and_clean_data(self, df):
        """
        解析和清理注意股票資料

        Args:
            df: 原始 DataFrame

        Returns:
            DataFrame: 清理後的資料
        """
        if df.empty:
            return df

        # 資料已經是正確的欄位名稱，只需要選擇需要的欄位
        keep_columns = ['證券代號', '證券名稱', '累計次數', '注意交易資訊', '日期', '收盤價', '本益比']

        # 只保留存在的欄位
        available_cols = [col for col in keep_columns if col in df.columns]
        df_clean = df[available_cols].copy()

        # 清理資料：去除空白
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].str.strip()

        return df_clean


def main():
    """主程式"""
    print("="*60)
    print("證交所注意股票爬蟲程式")
    print("="*60)

    # 初始化爬蟲
    crawler = TWSEAttentionStockCrawler()

    # 選項1: 抓取今日資料
    print("\n[選項1] 抓取今日注意股票")
    today_str = datetime.now().strftime('%Y%m%d')
    today_df = crawler.fetch_attention_stocks(today_str, today_str)

    if not today_df.empty:
        # 解析和清理資料
        today_clean = crawler.parse_and_clean_data(today_df)

        # 顯示結果
        print("\n今日注意股票:")
        print(today_clean.to_string(index=False))

        # 儲存
        crawler.save_to_csv(today_clean, f'注意股票_今日.csv')

    # 選項2: 抓取最近7天資料
    print("\n" + "="*60)
    print("[選項2] 抓取最近7天注意股票")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    range_df = crawler.fetch_date_range(
        start_date.strftime('%Y%m%d'),
        end_date.strftime('%Y%m%d')
    )

    if not range_df.empty:
        range_clean = crawler.parse_and_clean_data(range_df)
        crawler.save_to_csv(range_clean, f'注意股票_近7日.csv')

        # 統計分析
        print("\n統計分析:")
        print(f"不同股票數量: {range_clean['證券代號'].nunique()}")
        print(f"\n被列入注意股次數最多的前10名:")
        top_stocks = range_clean['證券代號'].value_counts().head(10)
        for code, count in top_stocks.items():
            stock_name = range_clean[range_clean['證券代號']==code]['證券名稱'].iloc[0]
            print(f"  {code} {stock_name}: {count}次")


if __name__ == '__main__':
    main()
