"""
股價資料取得模組
使用 FinMind API 取得股票的歷史價量資料
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time


class StockDataFetcher:
    def __init__(self, token_file='FinMind_API/token'):
        """
        初始化股價資料取得器

        Args:
            token_file: FinMind API token 檔案路徑
        """
        with open(token_file, 'r') as f:
            self.token = f.read().strip()

        self.base_url = "https://api.finmindtrade.com/api/v4/data"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_stock_price(self, stock_id, start_date, end_date, retry=3):
        """
        取得個股股價資料

        Args:
            stock_id: 股票代碼 (字串)
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期 'YYYY-MM-DD'
            retry: 失敗重試次數

        Returns:
            DataFrame: 股價資料，欄位包括：
                - date: 日期
                - stock_id: 股票代碼
                - open: 開盤價
                - max: 最高價
                - min: 最低價
                - close: 收盤價
                - Trading_Volume: 成交股數
                - Trading_money: 成交金額
                - spread: 漲跌
                - Trading_turnover: 成交筆數
        """
        parameter = {
            "dataset": "TaiwanStockPrice",
            "data_id": str(stock_id),
            "start_date": start_date,
            "end_date": end_date,
        }

        for attempt in range(retry):
            try:
                resp = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=parameter,
                    timeout=10
                )
                resp.raise_for_status()

                data = resp.json()

                if data.get('status') != 200:
                    print(f"API 回應錯誤: {data.get('msg')}")
                    return pd.DataFrame()

                if 'data' in data and data['data']:
                    df = pd.DataFrame(data['data'])

                    # 轉換資料型態
                    numeric_cols = ['open', 'max', 'min', 'close', 'Trading_Volume',
                                    'Trading_money', 'spread', 'Trading_turnover']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                    return df
                else:
                    return pd.DataFrame()

            except Exception as e:
                print(f"取得 {stock_id} 資料失敗 (嘗試 {attempt+1}/{retry}): {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        return pd.DataFrame()

    def get_multiple_stocks(self, stock_list, start_date, end_date, delay=0.2):
        """
        批次取得多檔股票資料

        Args:
            stock_list: 股票代碼列表
            start_date: 起始日期 'YYYY-MM-DD'
            end_date: 結束日期 'YYYY-MM-DD'
            delay: 每次請求間隔(秒)，避免過快

        Returns:
            dict: {股票代碼: DataFrame}
        """
        result = {}

        for idx, stock_id in enumerate(stock_list, 1):
            print(f"正在取得 {stock_id} 資料... ({idx}/{len(stock_list)})")

            df = self.get_stock_price(stock_id, start_date, end_date)

            if not df.empty:
                result[stock_id] = df
            else:
                print(f"  查無 {stock_id} 資料")

            # 避免請求過快
            if idx < len(stock_list):
                time.sleep(delay)

        print(f"\n成功取得 {len(result)}/{len(stock_list)} 檔股票資料")
        return result

    def get_recent_days(self, stock_id, days=10):
        """
        取得最近N天的股價資料

        Args:
            stock_id: 股票代碼
            days: 天數（預設10天，會自動往前推算避開假日）

        Returns:
            DataFrame: 股價資料
        """
        end_date = datetime.now()
        # 往前推算更多天以確保有足夠的交易日
        start_date = end_date - timedelta(days=days*2)

        df = self.get_stock_price(
            stock_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # 只保留最近的 N 筆交易日資料
        if not df.empty and len(df) > days:
            df = df.tail(days)

        return df

    def get_stock_info(self, stock_id, info_file='../(all)stock_info_list.csv'):
        """
        從股票清單中取得股票基本資訊

        Args:
            stock_id: 股票代碼
            info_file: 股票資訊檔案路徑

        Returns:
            dict: {'股票代碼', '公司名稱', '公司產業', '上市櫃', '發行股數'}
                  如果找不到則返回 None
        """
        try:
            df = pd.read_csv(info_file, encoding='utf-8-sig')
            df['股票代碼'] = df['股票代碼'].astype(str)

            stock = df[df['股票代碼'] == str(stock_id)]

            if not stock.empty:
                info = stock.iloc[0].to_dict()

                # 嘗試取得發行股數（如果有的話）
                # 注意：(all)stock_info_list.csv 可能沒有發行股數欄位
                # 之後可能需要另外抓取或手動補充
                if '發行股數' not in info:
                    info['發行股數'] = None

                return info
            else:
                return None

        except Exception as e:
            print(f"讀取股票資訊失敗: {e}")
            return None


def main():
    """測試用主程式"""
    print("="*60)
    print("股價資料取得模組測試")
    print("="*60)

    fetcher = StockDataFetcher()

    # 測試1: 取得單一股票最近資料
    print("\n[測試1] 取得 3057 喬鼎最近10天資料")
    df = fetcher.get_recent_days('3057', days=10)
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("無資料")

    # 測試2: 取得多檔股票資料
    print("\n" + "="*60)
    print("[測試2] 批次取得注意股資料")

    attention_stocks = ['3057', '3167', '1735']  # 從注意股清單中選幾檔
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

    stock_data = fetcher.get_multiple_stocks(attention_stocks, start_date, end_date)

    for stock_id, df in stock_data.items():
        print(f"\n{stock_id} 最近一筆資料:")
        if not df.empty:
            latest = df.iloc[-1]
            print(f"  日期: {latest['date']}")
            print(f"  收盤價: {latest['close']}")
            print(f"  成交量: {latest['Trading_Volume']:,.0f}")

    # 測試3: 取得股票基本資訊
    print("\n" + "="*60)
    print("[測試3] 取得股票基本資訊")
    info = fetcher.get_stock_info('3057')
    if info:
        print(f"股票代碼: {info['股票代碼']}")
        print(f"公司名稱: {info['公司名稱']}")
        print(f"產業: {info['公司產業']}")
        print(f"市場: {info['上市櫃']}")


if __name__ == '__main__':
    main()
