'use client'

import { useState, useMemo } from 'react'

interface MultiStrategyData {
  股票代碼: string
  公司名稱: string
  符合策略數: number
  符合策略: string
}

interface MultiStrategyTableProps {
  data: MultiStrategyData[]
}

export default function MultiStrategyTable({ data }: MultiStrategyTableProps) {
  const [sortColumn, setSortColumn] = useState<string>('符合策略數')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')

  // 排序資料
  const sortedData = useMemo(() => {
    if (!sortColumn) return data

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn as keyof MultiStrategyData]
      const bVal = b[sortColumn as keyof MultiStrategyData]

      // 數字比較
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      // 字串比較
      return sortDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal))
    })
  }, [data, sortColumn, sortDirection])

  // 處理排序
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('desc')
    }
  }

  // 策略顏色標籤
  const getStrategyBadges = (strategies: string) => {
    const strategyList = strategies.split(', ')
    const colorMap: Record<string, string> = {
      '隔日衝': 'bg-red-100 text-red-700 border-red-300',
      '外資買超': 'bg-blue-100 text-blue-700 border-blue-300',
      '投信連續': 'bg-green-100 text-green-700 border-green-300',
      '強勢股': 'bg-purple-100 text-purple-700 border-purple-300',
      '盤整突破': 'bg-orange-100 text-orange-700 border-orange-300',
      '大戶持有': 'bg-indigo-100 text-indigo-700 border-indigo-300',
    }

    return (
      <div className="flex flex-wrap gap-1">
        {strategyList.map((strategy, idx) => (
          <span
            key={idx}
            className={`inline-block px-2 py-0.5 text-xs font-medium rounded border ${
              colorMap[strategy] || 'bg-gray-100 text-gray-700 border-gray-300'
            }`}
          >
            {strategy}
          </span>
        ))}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🔍</div>
        <p className="text-gray-500 text-lg">目前沒有股票同時符合3個以上策略</p>
        <p className="text-gray-400 text-sm mt-2">資料將在每日 18:30 自動更新</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600">
        共 {data.length} 檔股票符合至少 3 個策略
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
                onClick={() => handleSort('符合策略數')}
                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-center gap-1">
                  符合策略數
                  {sortColumn === '符合策略數' && (
                    <span className="text-blue-600">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                符合策略
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  #{idx + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {row.股票代碼}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row.公司名稱}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm">
                    {row.符合策略數}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {getStrategyBadges(row.符合策略)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
