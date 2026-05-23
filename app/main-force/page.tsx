'use client'

import { useState, useEffect } from 'react'
import Papa from 'papaparse'
import DataTable from '@/components/DataTable'

const BASE = 'https://raw.githubusercontent.com/Roy12123/stock-analysis-platform/main/data/latest/'

const TABS = [
  {
    id: 'screen1_3d',
    label: '連續3天買超',
    file: '主力買超_連續3天.csv',
    desc: '連續 3 個交易日主力皆為淨買超（正值）',
  },
  {
    id: 'screen1_5d',
    label: '連續5天買超',
    file: '主力買超_連續5天.csv',
    desc: '連續 5 個交易日主力皆為淨買超（正值）',
  },
  {
    id: 'screen2',
    label: '5天≥3天買超',
    file: '主力買超_5天3正.csv',
    desc: '近 5 天中有 3 天以上為正，且最近 2 天皆為正',
  },
  {
    id: 'screen3',
    label: '5天累積排名',
    file: '主力買超_累積排名.csv',
    desc: '近 5 個交易日累積主力買超張數排名 Top 50',
  },
]

export default function MainForcePage() {
  const [activeTab, setActiveTab] = useState('screen1_3d')
  const [dataMap, setDataMap] = useState<Record<string, Record<string, string | number>[]>>({})
  const [loadingMap, setLoadingMap] = useState<Record<string, boolean>>({})
  const [errorMap, setErrorMap] = useState<Record<string, string | null>>({})

  const tab = TABS.find(t => t.id === activeTab)!

  useEffect(() => {
    if (dataMap[activeTab] !== undefined) return

    setLoadingMap(prev => ({ ...prev, [activeTab]: true }))

    fetch(`${BASE}${tab.file}?t=${Date.now()}`)
      .then(res => {
        if (!res.ok) throw new Error('資料尚未產生，請等待每日 21:00 自動更新')
        return res.text()
      })
      .then(csv => {
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: result => {
            setDataMap(prev => ({ ...prev, [activeTab]: result.data as Record<string, string | number>[] }))
            setLoadingMap(prev => ({ ...prev, [activeTab]: false }))
          },
          error: (err: Error) => {
            setErrorMap(prev => ({ ...prev, [activeTab]: err.message }))
            setLoadingMap(prev => ({ ...prev, [activeTab]: false }))
          },
        })
      })
      .catch(err => {
        setErrorMap(prev => ({ ...prev, [activeTab]: err.message }))
        setLoadingMap(prev => ({ ...prev, [activeTab]: false }))
      })
  }, [activeTab])

  const data = dataMap[activeTab] ?? []
  const loading = loadingMap[activeTab] ?? false
  const error = errorMap[activeTab] ?? null

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* 標題 */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">🏹</span>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              主力買賣超
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            每日分析全市場券商分點買賣資料，追蹤主力資金進出訊號
          </p>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-blue-600 font-medium text-sm">主力定義</div>
              <div className="text-gray-700 mt-1">買超／賣超前 15 大券商分點</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-green-600 font-medium text-sm">計算公式</div>
              <div className="text-gray-700 mt-1">前15買 − 前15賣（張）</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-purple-600 font-medium text-sm">更新時間</div>
              <div className="text-gray-700 mt-1">每日 21:00 自動更新</div>
            </div>
          </div>
        </div>

        {/* Tabs + 表格 */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          {/* Tab 列 */}
          <div className="flex border-b border-gray-200">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex-1 px-4 py-4 text-sm font-medium transition-all whitespace-nowrap ${
                  activeTab === t.id
                    ? 'bg-blue-600 text-white border-b-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-blue-600'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* 內容 */}
          <div className="p-6">
            <p className="text-sm text-gray-500 mb-4">{tab.desc}</p>

            {loading && (
              <div className="text-center py-16">
                <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4" />
                <p className="text-gray-500">載入中...</p>
              </div>
            )}

            {error && (
              <div className="text-center py-16">
                <div className="text-5xl mb-4">⚠️</div>
                <p className="text-red-500">{error}</p>
                <p className="text-gray-400 text-sm mt-2">資料將於每日 21:00 自動更新</p>
              </div>
            )}

            {!loading && !error && (
              <DataTable data={data} />
            )}
          </div>
        </div>

        {/* 說明 */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100">
          <h2 className="text-lg font-bold text-gray-800 mb-3">💡 使用說明</h2>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>主力買超（張）</strong>：當日前15大買超分點 買量 − 前15大賣超分點 賣量，正值代表主力淨買進</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span><strong>5日累積買超</strong>：最近5個交易日主力買超張數加總，數值越高代表主力持續進場</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>資料來源：FinMind TaiwanStockTradingDailyReport，含零股與盤後交易</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>點擊股票代碼可連結至 Goodinfo 查看詳細資訊</span>
            </li>
          </ul>
        </div>

      </div>
    </div>
  )
}
