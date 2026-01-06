'use client'

import { useState, useMemo } from 'react'
import { formatNumber, getPriceColor } from '@/lib/utils'

interface CategoryStocksTableProps {
  data: Record<string, string | number>[]
}

export default function CategoryStocksTable({ data }: CategoryStocksTableProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('全部')
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  // 取得所有族群
  const categories = useMemo(() => {
    const categorySet = new Set<string>()
    data.forEach(row => {
      if (row['族群']) {
        categorySet.add(String(row['族群']))
      }
    })
    return ['全部', ...Array.from(categorySet).sort()]
  }, [data])

  // 取得欄位名稱
  const columns = data.length > 0 ? Object.keys(data[0]) : []

  // 篩選和排序資料
  const filteredAndSortedData = useMemo(() => {
    let filtered = selectedCategory === '全部'
      ? [...data]
      : data.filter(row => row['族群'] === selectedCategory)

    if (sortColumn) {
      filtered.sort((a, b) => {
        const aVal = a[sortColumn]
        const bVal = b[sortColumn]

        // 嘗試轉換為數字比較
        const aNum = typeof aVal === 'string' ? parseFloat(aVal.replace(/[^0-9.-]/g, '')) : aVal
        const bNum = typeof bVal === 'string' ? parseFloat(bVal.replace(/[^0-9.-]/g, '')) : bVal

        if (!isNaN(aNum as number) && !isNaN(bNum as number)) {
          return sortDirection === 'asc'
            ? (aNum as number) - (bNum as number)
            : (bNum as number) - (aNum as number)
        }

        // 字串比較
        return sortDirection === 'asc'
          ? String(aVal).localeCompare(String(bVal))
          : String(bVal).localeCompare(String(aVal))
      })
    }

    return filtered
  }, [data, selectedCategory, sortColumn, sortDirection])

  // 分頁資料
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage)
  const paginatedData = filteredAndSortedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // 處理排序
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('desc')
    }
  }

  // 格式化儲存格值
  const formatCellValue = (key: string, value: string | number) => {
    const strValue = String(value)

    // 股票代碼 - 加上 Goodinfo 超連結
    if (key === 'stock_id' && strValue) {
      const stockId = strValue.trim()
      return (
        <a
          href={`https://goodinfo.tw/tw/ShowBuySaleChart.asp?STOCK_ID=${stockId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
        >
          {stockId}
        </a>
      )
    }

    // 百分比或漲跌幅
    if (strValue.includes('%') || key.includes('漲跌') || key.includes('漲幅') || key.includes('波動')) {
      const numValue = parseFloat(strValue.replace(/[^0-9.-]/g, ''))
      if (!isNaN(numValue)) {
        return <span className={getPriceColor(numValue)}>{strValue}</span>
      }
    }

    // 數字（千分位）
    if (key.includes('張') || key.includes('價') || key.includes('量') || key.includes('元')) {
      const numValue = typeof value === 'string' ? parseFloat(value) : value
      if (!isNaN(numValue)) {
        return formatNumber(numValue)
      }
    }

    return strValue
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">暫無資料</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 族群選擇器 */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          共 {filteredAndSortedData.length} 筆資料
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-700 font-medium">族群篩選：</label>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value)
              setCurrentPage(1)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 表格 */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  onClick={() => handleSort(column)}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-1">
                    {column}
                    {sortColumn === column && (
                      <span className="text-blue-600">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                {columns.map((column) => (
                  <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCellValue(column, row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分頁 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            第 {currentPage} 頁，共 {totalPages} 頁
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              上一頁
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              下一頁
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
