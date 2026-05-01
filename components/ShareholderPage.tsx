'use client'

import { useEffect, useState } from 'react'
import Papa from 'papaparse'
import DataTable from './DataTable'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

export default function ShareholderPage() {
  const [data, setData] = useState<Record<string, string | number>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState<string>('')

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError(null)

        const timestamp = new Date().getTime()
        const response = await fetch(`https://raw.githubusercontent.com/Roy12123/stock-analysis-platform/main/data/latest/大戶持有比例差.csv?t=${timestamp}`)

        if (!response.ok) {
          throw new Error('資料檔案尚未產生，請等待 GitHub Actions 執行')
        }

        const csvText = await response.text()

        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const raw = results.data as Record<string, string | number>[]

            // 簡化公司產業，並調整欄位順序（公司名稱在前）
            const processed = raw.map(row => {
              const newRow: Record<string, string | number> = {}
              const keys = Object.keys(row)
              const nameIdx = keys.indexOf('公司名稱')
              const industryIdx = keys.indexOf('公司產業')
              if (nameIdx > industryIdx && nameIdx !== -1 && industryIdx !== -1) {
                keys.splice(nameIdx, 1)
                keys.splice(industryIdx, 0, '公司名稱')
              }
              keys.forEach(k => {
                const val = row[k]
                newRow[k] = k === '公司產業' && typeof val === 'string'
                  ? val.replace(/^全部\(.*\)$/, '全部')
                  : val
              })
              return newRow
            })

            setData(processed)

            // 從檔案名稱提取日期（如果可能的話）
            // 或顯示通用的分析期間說明
            setDateRange('分析期間：最近兩次股東持股資料更新日')

            setLoading(false)
          },
          error: (error: Error) => {
            setError(`解析 CSV 失敗: ${error.message}`)
            setLoading(false)
          }
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : '載入資料失敗')
        setLoading(false)
      }
    }

    loadData()
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-4xl">💎</span>
          <h1 className="text-3xl font-bold text-gray-900">大戶持有比例差</h1>
        </div>
        <p className="text-gray-600">分析大戶持股比例變化，追蹤主力資金動向，包含持股增減幅度與價格變化</p>
        {dateRange && (
          <p className="text-sm text-gray-500 mt-2">
            {dateRange}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-1">
          註：股東持股資料通常每週更新一次（週五），分析比較最近兩筆資料
        </p>
      </div>

      {loading && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-600">載入資料中...</p>
            </div>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="text-yellow-900">⚠️ 資料尚未準備</CardTitle>
            <CardDescription className="text-yellow-700">{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-yellow-800 space-y-2">
              <p>請確認：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>GitHub Actions 是否已成功執行</li>
                <li>CSV 檔案是否已推送到 data/latest 目錄</li>
                <li>檔名是否正確: 大戶持有比例差.csv</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {!loading && !error && data.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <DataTable data={data} />
          </CardContent>
        </Card>
      )}

      {!loading && !error && data.length === 0 && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <p className="text-gray-500 text-lg">暫無資料</p>
              <p className="text-gray-400 text-sm mt-2">資料將在 GitHub Actions 執行後自動更新</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
