'use client'

import { useState, useMemo } from 'react'

interface ConvertibleBondData {
  CB代號: string
  CB名稱: string
  個股現價: number
  轉換價格: number
  '餘額比例(%)': number | string
  '距轉換價差距(%)': number
  '已發行/近期上市': string
}

interface ConvertibleBondTableProps {
  data: ConvertibleBondData[]
}

type TabType = '全部' | '已發行CB' | '近期上市'

export default function ConvertibleBondTable({ data }: ConvertibleBondTableProps) {
  const [activeTab, setActiveTab] = useState<TabType>('全部')
  const [sortColumn, setSortColumn] = useState<string>('距轉換價差距(%)')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const tabCounts = useMemo(() => ({
    全部: data.length,
    已發行CB: data.filter(r => r['已發行/近期上市'] === '已發行CB').length,
    近期上市: data.filter(r => r['已發行/近期上市'] === '近期上市').length,
  }), [data])

  const filteredData = useMemo(() => {
    if (activeTab === '全部') return data
    return data.filter(r => r['已發行/近期上市'] === activeTab)
  }, [data, activeTab])

  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortColumn as keyof ConvertibleBondData]
      const bVal = b[sortColumn as keyof ConvertibleBondData]
      if (sortColumn === '距轉換價差距(%)') {
        const aAbs = Math.abs(Number(aVal))
        const bAbs = Math.abs(Number(bVal))
        return sortDirection === 'asc' ? aAbs - bAbs : bAbs - aAbs
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }
      return sortDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal))
    })
  }, [filteredData, sortColumn, sortDirection])

  const totalPages = Math.ceil(sortedData.length / itemsPerPage)
  const paginatedData = sortedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
    setCurrentPage(1)
  }

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    setCurrentPage(1)
  }

  const SortIcon = ({ column }: { column: string }) =>
    sortColumn === column ? (
      <span className="text-blue-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
    ) : null

  const GapBadge = ({ value }: { value: number }) => {
    const color = value > 0
      ? 'text-red-600 bg-red-50'
      : value < 0
        ? 'text-green-600 bg-green-50'
        : 'text-gray-600 bg-gray-50'
    return (
      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
        {value > 0 ? '+' : ''}{value.toFixed(2)}%
      </span>
    )
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📊</div>
        <p className="text-gray-500 text-lg">目前沒有符合條件的可轉債</p>
        <p className="text-gray-400 text-sm mt-2">資料將在每日 18:00 自動更新</p>
      </div>
    )
  }

  const tabs: TabType[] = ['全部', '已發行CB', '近期上市']

  return (
    <div className="space-y-4">
      {/* Tab 切換 */}
      <div className="flex gap-2 border-b border-gray-200">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => handleTabChange(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {tab}
            <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
              activeTab === tab ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'
            }`}>
              {tabCounts[tab]}
            </span>
          </button>
        ))}
      </div>

      <div className="text-sm text-gray-500">
        共 {sortedData.length} 檔符合條件
      </div>

      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase w-12">
                排名
              </th>
              {[
                { key: 'CB代號', label: 'CB 代號', align: 'left' },
                { key: 'CB名稱', label: 'CB 名稱', align: 'left' },
                { key: '個股現價', label: '個股現價', align: 'right' },
                { key: '轉換價格', label: '轉換價格', align: 'right' },
                { key: '距轉換價差距(%)', label: '距轉換價差距', align: 'right' },
                { key: '餘額比例(%)', label: '餘額比例(%)', align: 'right' },
                { key: '已發行/近期上市', label: '類型', align: 'center' },
              ].map(({ key, label, align }) => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors text-${align}`}
                >
                  <div className={`flex items-center gap-1 ${align === 'right' ? 'justify-end' : align === 'center' ? 'justify-center' : ''}`}>
                    {label}
                    <SortIcon column={key} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400">
                  #{(currentPage - 1) * itemsPerPage + idx + 1}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                  {row.CB代號}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                  {row.CB名稱}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right">
                  {row.個股現價.toFixed(2)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right">
                  {row.轉換價格.toFixed(2)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right">
                  <GapBadge value={row['距轉換價差距(%)']} />
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-right">
                  {row['餘額比例(%)'] !== '' && row['餘額比例(%)'] !== null
                    ? `${Number(row['餘額比例(%)']).toFixed(1)}%`
                    : '-'}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center">
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                    row['已發行/近期上市'] === '近期上市'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {row['已發行/近期上市']}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            第 {currentPage} 頁，共 {totalPages} 頁
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors text-sm"
            >
              上一頁
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors text-sm"
            >
              下一頁
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
