'use client';

import { useEffect, useState } from 'react';

interface StockData {
  股票代碼: string;
  公司名稱: string;
  當下價格: number;
  '當下漲跌幅(%)': number;
  '外資昨日買超(張)': number;
  '外資前三日總買超(張)': number;
  '投信昨日買超(張)': number;
  '投信前三日總買超(張)': number;
}

export default function DailyRushPage() {
  const [data, setData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [updateTime, setUpdateTime] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetch('/api/daily-rush')
      .then(res => res.json())
      .then(result => {
        if (result.success) {
          setData(result.data || []);
          setUpdateTime(result.updateTime || '');
          setError('');
        } else {
          setError(result.error || '無法載入資料');
          setData([]);
        }
        setLoading(false);
      })
      .catch(err => {
        setError('無法連接到伺服器');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">載入中...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
                🚀 隔日衝策略 - 每日篩選
              </h1>
              <p className="text-gray-600 mt-2">
                篩選條件：紅K棒 + 實體&gt;前日1.5倍 + 量&gt;5日均量2倍 + 上下影線&lt;實體30% + 收在高點 + 量≥10000張
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">更新時間</div>
              <div className="text-lg font-semibold text-blue-600">{updateTime}</div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Card */}
        {!error && (
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md p-6 mb-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">今日符合條件股票</p>
                <p className="text-4xl font-bold mt-1">{data.length} 檔</p>
              </div>
              <div className="text-6xl opacity-20">🎯</div>
            </div>
          </div>
        )}

        {/* Table */}
        {data.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      排名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      股票代碼
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      公司名稱
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      當下價格
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      漲跌幅(%)
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      外資昨日
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      外資3日
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      投信昨日
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      投信3日
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.map((stock, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        #{idx + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {stock.股票代碼}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.公司名稱}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                        {stock.當下價格?.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                        <span className={stock['當下漲跌幅(%)'] > 0 ? 'text-red-600' : 'text-green-600'}>
                          {stock['當下漲跌幅(%)'] > 0 ? '+' : ''}{stock['當下漲跌幅(%)']?.toFixed(2)}%
                        </span>
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${
                        stock['外資昨日買超(張)'] > 0 ? 'text-red-600' : stock['外資昨日買超(張)'] < 0 ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {stock['外資昨日買超(張)']?.toFixed(0)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${
                        stock['外資前三日總買超(張)'] > 0 ? 'text-red-600' : stock['外資前三日總買超(張)'] < 0 ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {stock['外資前三日總買超(張)']?.toFixed(0)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${
                        stock['投信昨日買超(張)'] > 0 ? 'text-red-600' : stock['投信昨日買超(張)'] < 0 ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {stock['投信昨日買超(張)']?.toFixed(0)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${
                        stock['投信前三日總買超(張)'] > 0 ? 'text-red-600' : stock['投信前三日總買超(張)'] < 0 ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {stock['投信前三日總買超(張)']?.toFixed(0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : !error && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">今天沒有符合條件的股票</h3>
            <p className="text-gray-500">請明天再來查看</p>
          </div>
        )}

        {/* Footer Info */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>策略說明：</strong>本策略篩選出當日強勢爆量且收在高點的股票，適合短線操作。
            紅K棒且實體大於前日1.5倍、成交量大於5日均量2倍、上下影線小於實體30%、收盤價在最高價的98%以上、成交量大於10000張。
          </p>
          <p className="text-xs text-blue-600 mt-2">
            ⚠️ 本資料僅供參考，不構成投資建議。投資有風險，請謹慎評估。
          </p>
        </div>
      </div>
    </div>
  );
}
