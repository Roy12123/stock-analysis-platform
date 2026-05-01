'use client'

import { useState, useEffect } from 'react'
import Papa from 'papaparse'
import ConvertibleBondTable from '@/components/ConvertibleBondTable'

export default function ConvertibleBondsPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const basePath = process.env.NODE_ENV === 'production' ? '/stock-analysis-platform' : ''
    fetch(`${basePath}/data/latest/convertible-bonds.csv`)
      .then(res => res.text())
      .then(csvText => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (result) => {
            const processedData = result.data.map((row: any) => ({
              ...row,
              個股現價: parseFloat(row['個股現價']) || 0,
              轉換價格: parseFloat(row['轉換價格']) || 0,
              '距轉換價差距(%)': parseFloat(row['距轉換價差距(%)']) || 0,
              '餘額比例(%)': row['餘額比例(%)'] !== '' ? parseFloat(row['餘額比例(%)']) : '',
            }))
            setData(processedData)
            setLoading(false)
          },
          error: (error: Error) => {
            console.error('CSV parsing error:', error)
            setError('無法載入資料')
            setLoading(false)
          }
        })
      })
      .catch(err => {
        console.error('Fetch error:', err)
        setError('無法載入資料')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⏳</div>
            <p className="text-gray-500 text-lg">載入中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-red-500 text-lg">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 標題區 */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">📊</span>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              可轉債篩選
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            篩選條件：個股現價在轉換價格 ±5% 範圍內
          </p>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-blue-600 font-medium text-sm">價格條件</div>
              <div className="text-gray-700 mt-1">現價距轉換價 ±5% 內</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-purple-600 font-medium text-sm">資料來源</div>
              <div className="text-gray-700 mt-1">已發行CB ＋ 近期上市CB</div>
            </div>
          </div>
        </div>

        {/* 資料表格 */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <ConvertibleBondTable data={data} />
        </div>

        {/* 說明區 */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100">
          <h2 className="text-lg font-bold text-gray-800 mb-3">💡 使用說明</h2>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>距轉換價差距</strong>：正值代表現價高於轉換價（溢價），負值代表現價低於轉換價（折價），數值越小代表越接近轉換價</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>餘額比例</strong>：尚未轉換的 CB 餘額佔發行總額的比例，近期上市 CB 固定為 100%</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>已發行CB / 近期上市</strong>：可透過上方 Tab 分類篩選</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>更新時間</strong>：每日 18:00 自動更新資料</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
