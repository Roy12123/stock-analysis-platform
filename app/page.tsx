'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useLastUpdate } from '@/hooks/useLastUpdate'

const strategies = [
  {
    name: '隔日衝策略',
    href: '/daily-rush',
    icon: '🚀',
    description: '紅K棒+實體>前日1.5倍+量>5日均量2倍+收在高點+大量能',
    color: 'bg-red-50 border-red-200',
    badge: '每日13:20更新',
  },
  {
    name: '外資大量買超',
    href: '/foreign-investment',
    icon: '🌐',
    description: '篩選當日外資買超 > 5000張 或 買超金額 > 2億元的股票',
    color: 'bg-blue-50 border-blue-200',
  },
  {
    name: '投信連續買超',
    href: '/investment-trust',
    icon: '🏦',
    description: '近5日有4日投信買超、平均買超≥500張、價格波動≤14%',
    color: 'bg-green-50 border-green-200',
  },
  {
    name: '強勢股篩選',
    href: '/strong-stocks',
    icon: '📈',
    description: '多頭排列、近10日最高、漲幅>0050、大量能',
    color: 'bg-red-50 border-red-200',
  },
  {
    name: '盤整突破',
    href: '/breakthrough',
    icon: '🔥',
    description: '成交量>20MA的5倍、成交量>5000張、近3個交易日內突破',
    color: 'bg-purple-50 border-purple-200',
  },
  {
    name: '族群排名',
    href: '/category-ranking',
    icon: '🏆',
    description: '族群平均漲幅排名、上漲檔數、法人買賣超統計',
    color: 'bg-orange-50 border-orange-200',
  },
  {
    name: '族群個股資料',
    href: '/category-stocks',
    icon: '📊',
    description: '依族群分類的個股資料，包含今日漲跌幅、成交量等',
    color: 'bg-yellow-50 border-yellow-200',
  },
  {
    name: '大戶持有比例差',
    href: '/shareholder',
    icon: '💎',
    description: '分析大戶持股比例變化，追蹤主力動向',
    color: 'bg-indigo-50 border-indigo-200',
  },
]

export default function HomePage() {
  const { updateData, loading } = useLastUpdate()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16 fade-in">
        <div className="inline-block mb-6">
          <div className="text-6xl mb-4 animate-bounce">📊</div>
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6">
          <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-blue-600 bg-clip-text text-transparent">
            台股分析平台
          </span>
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 mb-3 font-medium">
          自動化台股篩選分析系統
        </p>
        <div className="flex flex-col items-center justify-center gap-2 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-full border border-green-200">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              自動更新時間
            </span>
            <span className="text-gray-400">|</span>
            <span className="text-gray-600">台北時間 10:00 & 18:00</span>
          </div>
          {!loading && updateData?.stock_analysis && (
            <div className="text-xs text-gray-500">
              最後更新：{updateData.stock_analysis.updated_at} (資料日期: {updateData.stock_analysis.trade_date})
            </div>
          )}
        </div>
      </div>

      {/* 系統說明 */}
      <Card className="mb-12 border-2 border-blue-100 shadow-lg bg-gradient-to-br from-white to-blue-50/30">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <span className="text-blue-600">⚙️</span>
            系統說明
          </CardTitle>
          <CardDescription className="text-base">
            本平台透過 GitHub Actions 自動執行 Python 腳本，每日定時分析台股資料
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-5 bg-white rounded-xl border border-red-100 shadow-sm hover:shadow-md transition-shadow">
              <h3 className="font-bold text-gray-900 mb-3 text-lg flex items-center gap-2">
                <span className="text-2xl">🚀</span>
                隔日衝策略
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-red-600 font-semibold">⏰</span>
                  <span className="text-gray-600">每日 07:00 & 13:20 (台北時間)</span>
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">
                  篩選強勢爆量股票，適合短線操作
                </p>
              </div>
            </div>
            <div className="p-5 bg-white rounded-xl border border-blue-100 shadow-sm hover:shadow-md transition-shadow">
              <h3 className="font-bold text-gray-900 mb-3 text-lg flex items-center gap-2">
                <span className="text-2xl">📊</span>
                股票綜合篩選
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-600 font-semibold">⏰</span>
                  <span className="text-gray-600">執行時間：每日 18:00 (台北時間)</span>
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">
                  包含外資買超、投信買超、強勢股、盤整突破、族群分析等六種策略
                </p>
              </div>
            </div>
            <div className="p-5 bg-white rounded-xl border border-indigo-100 shadow-sm hover:shadow-md transition-shadow">
              <h3 className="font-bold text-gray-900 mb-3 text-lg flex items-center gap-2">
                <span className="text-2xl">💎</span>
                股東持有比例差
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-600 font-semibold">⏰</span>
                  <span className="text-gray-600">執行時間：每日 10:00 (台北時間)</span>
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">
                  分析大戶持股比例變化，追蹤主力資金動向
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 策略卡片 */}
      <div className="mb-12">
        <div className="flex items-center gap-3 mb-8">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            篩選策略
          </h2>
          <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
            8 種策略
          </span>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy, index) => (
            <Link key={strategy.href} href={strategy.href}>
              <Card
                className={`h-full transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 cursor-pointer border-2 ${strategy.color} group relative overflow-hidden`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-white/20 rounded-full -mr-10 -mt-10 group-hover:scale-150 transition-transform duration-500"></div>
                <CardHeader className="relative z-10">
                  <CardTitle className="flex items-center gap-3">
                    <span className="text-3xl group-hover:scale-125 transition-transform duration-300">{strategy.icon}</span>
                    <div className="flex flex-col gap-1">
                      <span className="group-hover:text-blue-700 transition-colors">{strategy.name}</span>
                      {strategy.badge && (
                        <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full w-fit">
                          {strategy.badge}
                        </span>
                      )}
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative z-10">
                  <p className="text-sm text-gray-700 leading-relaxed">{strategy.description}</p>
                  <div className="mt-4 flex items-center text-blue-600 text-sm font-medium group-hover:translate-x-2 transition-transform">
                    查看詳情 →
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* 功能特色 */}
      <Card className="border-2 border-gray-200 shadow-lg bg-gradient-to-br from-white via-gray-50 to-white">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <span className="text-yellow-500">✨</span>
            功能特色
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="group p-6 rounded-2xl bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 hover:shadow-xl transition-all duration-300">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">⚡</div>
              <h3 className="font-bold text-lg mb-2 text-gray-900">自動化執行</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                GitHub Actions 定時自動執行，無需手動操作
              </p>
            </div>
            <div className="group p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 hover:shadow-xl transition-all duration-300">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📈</div>
              <h3 className="font-bold text-lg mb-2 text-gray-900">多維度分析</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                8種策略全方位分析台股，找出潛力標的
              </p>
            </div>
            <div className="group p-6 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 hover:shadow-xl transition-all duration-300">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🔍</div>
              <h3 className="font-bold text-lg mb-2 text-gray-900">即時搜尋篩選</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                支援關鍵字搜尋、欄位排序、分頁瀏覽
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 注意事項 */}
      <div className="mt-12 p-8 bg-gradient-to-r from-yellow-50 via-orange-50 to-yellow-50 border-2 border-yellow-300 rounded-2xl shadow-lg">
        <div className="flex items-start gap-4">
          <div className="text-4xl">⚠️</div>
          <div className="flex-1">
            <h3 className="font-bold text-yellow-900 mb-3 text-lg">免責聲明</h3>
            <p className="text-sm text-yellow-800 leading-relaxed">
              本平台僅提供資料篩選與分析功能，不構成任何投資建議。投資有風險，請謹慎評估並自行承擔投資決策責任。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
