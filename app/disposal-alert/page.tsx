'use client'

import { useEffect, useState } from 'react'
import DisposalAlertTable from '@/components/DisposalAlertTable'

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

export default function DisposalAlertPage() {
  const [data, setData] = useState<DisposalAlertData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError(null)

        // 加上時間戳避免快取
        const timestamp = new Date().getTime()
        const response = await fetch(
          `https://raw.githubusercontent.com/Roy12123/stock-analysis-platform/main/data/latest/處置注意股.csv?t=${timestamp}`
        )

        if (!response.ok) {
          throw new Error('無法載入資料')
        }

        const csvText = await response.text()

        // 使用 PapaParse 解析 CSV
        const Papa = (await import('papaparse')).default
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          dynamicTyping: true,
          complete: (results) => {
            setData(results.data as DisposalAlertData[])
            setLoading(false)
          },
          error: (error: Error) => {
            console.error('CSV 解析錯誤:', error)
            setError('資料解析失敗')
            setLoading(false)
          }
        })
      } catch (err) {
        console.error('載入資料錯誤:', err)
        setError(err instanceof Error ? err.message : '載入失敗')
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            <p className="mt-4 text-gray-600">載入中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <p className="text-red-600 text-lg">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 transition-colors"
            >
              重新載入
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 標題區域 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-5xl">⚠️</span>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                處置注意股預警
              </h1>
              <p className="text-gray-600 mt-1">
                預測可能被處置的股票，提前規避風險
              </p>
            </div>
          </div>

          {/* 說明卡片 */}
          <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">📋 策略說明</h2>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div>
                <h3 className="font-medium text-gray-800 mb-2">處置條件</h3>
                <ul className="space-y-1">
                  <li>• 連續 3 日注意股 → 高風險</li>
                  <li>• 連續 5 日注意股 → 極高風險</li>
                  <li>• 近 10 日有 6 日 → 高風險</li>
                  <li>• 近 30 日有 12 日 → 中風險</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-gray-800 mb-2">注意事項</h3>
                <ul className="space-y-1">
                  <li>• 處置股票漲跌幅限制 ±3.5%</li>
                  <li>• 撮合間隔延長至 20 秒</li>
                  <li>• 流動性大幅降低</li>
                  <li>• 建議避開或提前減碼</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* 資料表格 */}
        <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-sm border border-gray-200 p-6">
          <DisposalAlertTable data={data} />
        </div>

        {/* 更新時間 */}
        <div className="mt-6 text-center text-sm text-gray-500">
          資料每日 19:00 自動更新
        </div>
      </div>
    </div>
  )
}
