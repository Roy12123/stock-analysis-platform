'use client'

import { useState, useMemo } from 'react'

interface DisposalAlertData {
  股票代碼: string
  公司名稱: string
  風險等級: string
  累計注意股次數: number
  連續天數: number
  預測處置原因: string
  最新收盤價: number
  漲幅門檻: string
  跌幅門檻: string
}

interface DisposalAlertTableProps {
  data: DisposalAlertData[]
}

export default function DisposalAlertTable({ data }: DisposalAlertTableProps) {
  const [sortColumn, setSortColumn] = useState<string>('風險等級')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [filterRisk, setFilterRisk] = useState<string>('全部')

  // 風險等級排序權重
  const riskWeight: Record<string, number> = {
    '極高': 4,
    '高': 3,
    '中': 2,
    '低': 1
  }

  // 風險等級顏色映射
  const riskColorMap: Record<string, string> = {
    '極高': 'bg-red-100 text-red-700 border-red-300',
    '高': 'bg-orange-100 text-orange-700 border-orange-300',
    '中': 'bg-yellow-100 text-yellow-700 border-yellow-300',
    '低': 'bg-green-100 text-green-700 border-green-300',
  }

  // 過濾資料
  const filteredData = useMemo(() => {
    if (filterRisk === '全部') return data
    return data.filter(row => row.風險等級 === filterRisk)
  }, [data, filterRisk])

  // 排序資料
  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData

    return [...filteredData].sort((a, b) => {
      let aVal: any = a[sortColumn as keyof DisposalAlertData]
      let bVal: any = b[sortColumn as keyof DisposalAlertData]

      // 風險等級使用權重排序
      if (sortColumn === '風險等級') {
        aVal = riskWeight[a.風險等級] || 0
        bVal = riskWeight[b.風險等級] || 0
      }

      // 數字比較
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      // 字串比較
      return sortDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal))
    })
  }, [filteredData, sortColumn, sortDirection])

  // 處理排序
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('desc')
    }
  }

  // 統計資訊
  const stats = useMemo(() => {
    return {
      極高: data.filter(d => d.風險等級 === '極高').length,
      高: data.filter(d => d.風險等級 === '高').length,
      中: data.filter(d => d.風險等級 === '中').length,
      低: data.filter(d => d.風險等級 === '低').length,
    }
  }, [data])

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">✅</div>
        <p className="text-gray-500 text-lg">目前沒有股票達到處置標準</p>
        <p className="text-gray-400 text-sm mt-2">資料將在每日 18:00 自動更新</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 統計摘要 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-600 text-sm font-medium">極高風險</div>
          <div className="text-red-900 text-2xl font-bold mt-1">{stats.極高}</div>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="text-orange-600 text-sm font-medium">高風險</div>
          <div className="text-orange-900 text-2xl font-bold mt-1">{stats.高}</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-yellow-600 text-sm font-medium">中風險</div>
          <div className="text-yellow-900 text-2xl font-bold mt-1">{stats.中}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-green-600 text-sm font-medium">低風險</div>
          <div className="text-green-900 text-2xl font-bold mt-1">{stats.低}</div>
        </div>
      </div>

      {/* 風險等級篩選器 */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm text-gray-600">篩選風險等級：</span>
        {['全部', '極高', '高', '中', '低'].map(risk => (
          <button
            key={risk}
            onClick={() => setFilterRisk(risk)}
            className={`px-3 py-1 text-sm rounded border transition-colors ${
              filterRisk === risk
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {risk}
          </button>
        ))}
      </div>

      <div className="text-sm text-gray-600">
        共 {sortedData.length} 檔股票{filterRisk !== '全部' ? `（${filterRisk}風險）` : ''}
      </div>

      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                排名
              </th>
              <th
                onClick={() => handleSort('股票代碼')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-1">
                  股票代碼
                  {sortColumn === '股票代碼' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th
                onClick={() => handleSort('公司名稱')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-1">
                  公司名稱
                  {sortColumn === '公司名稱' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th
                onClick={() => handleSort('風險等級')}
                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-center gap-1">
                  風險等級
                  {sortColumn === '風險等級' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th
                onClick={() => handleSort('累計注意股次數')}
                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-center gap-1">
                  累計次數
                  {sortColumn === '累計注意股次數' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th
                onClick={() => handleSort('連續天數')}
                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-center gap-1">
                  連續天數
                  {sortColumn === '連續天數' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                預測處置原因
              </th>
              <th
                onClick={() => handleSort('最新收盤價')}
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-end gap-1">
                  最新收盤
                  {sortColumn === '最新收盤價' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                明天門檻
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  #{idx + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <a
                    href={`https://goodinfo.tw/tw/ShowBuySaleChart.asp?STOCK_ID=${row.股票代碼}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    {row.股票代碼}
                  </a>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row.公司名稱}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`inline-block px-3 py-1 text-xs font-medium rounded border ${
                    riskColorMap[row.風險等級] || 'bg-gray-100 text-gray-700 border-gray-300'
                  }`}>
                    {row.風險等級}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                  {row.累計注意股次數}次
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                  {row.連續天數}天
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {row.預測處置原因}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                  {typeof row.最新收盤價 === 'number' ? row.最新收盤價.toFixed(2) : row.最新收盤價}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="text-red-600">漲: {row.漲幅門檻}</div>
                  <div className="text-green-600">跌: {row.跌幅門檻}</div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 說明文字 */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
        <div className="font-medium text-yellow-800 mb-2">⚠️ 處置股票說明</div>
        <ul className="text-yellow-700 space-y-1 list-disc list-inside">
          <li>處置股票受限於當日漲跌幅 ±3.5% 且撮合間隔延長</li>
          <li>風險等級依據：連續天數越長、累計次數越多，風險越高</li>
          <li>明天門檻：顯示達到何種價格會觸發注意股條件</li>
          <li>建議：避開高風險股票，已持有者可考慮提前減碼</li>
        </ul>
      </div>
    </div>
  )
}
