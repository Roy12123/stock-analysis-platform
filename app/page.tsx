import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const strategies = [
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
    icon: '🚀',
    description: '成交量>20MA的5倍、成交量>5000張、近3個交易日內突破',
    color: 'bg-purple-50 border-purple-200',
  },
  {
    name: '族群個股資料',
    href: '/category-stocks',
    icon: '📊',
    description: '依族群分類的個股資料，包含今日漲跌幅、成交量等',
    color: 'bg-yellow-50 border-yellow-200',
  },
  {
    name: '族群排名',
    href: '/category-ranking',
    icon: '🏆',
    description: '族群平均漲幅排名、上漲檔數、法人買賣超統計',
    color: 'bg-orange-50 border-orange-200',
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
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          台股分析平台
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          自動化台股篩選分析系統
        </p>
        <p className="text-sm text-gray-500">
          每日自動更新 | 台北時間 10:00 & 18:00
        </p>
      </div>

      {/* 系統說明 */}
      <Card className="mb-12">
        <CardHeader>
          <CardTitle>系統說明</CardTitle>
          <CardDescription>
            本平台透過 GitHub Actions 自動執行 Python 腳本，每日定時分析台股資料
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">📊 股票綜合篩選</h3>
              <p className="text-sm text-gray-600 mb-1">執行時間：每日 18:00 (台北時間)</p>
              <p className="text-sm text-gray-500">
                包含外資買超、投信買超、強勢股、盤整突破、族群分析等六種策略
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">💎 股東持有比例差</h3>
              <p className="text-sm text-gray-600 mb-1">執行時間：每日 10:00 (台北時間)</p>
              <p className="text-sm text-gray-500">
                分析大戶持股比例變化，追蹤主力資金動向
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 策略卡片 */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">篩選策略</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy) => (
            <Link key={strategy.href} href={strategy.href}>
              <Card className={`h-full transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer ${strategy.color}`}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">{strategy.icon}</span>
                    <span>{strategy.name}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700">{strategy.description}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* 功能特色 */}
      <Card>
        <CardHeader>
          <CardTitle>功能特色</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-2xl mb-2">⚡</div>
              <h3 className="font-semibold mb-1">自動化執行</h3>
              <p className="text-sm text-gray-600">
                GitHub Actions 定時自動執行，無需手動操作
              </p>
            </div>
            <div>
              <div className="text-2xl mb-2">📈</div>
              <h3 className="font-semibold mb-1">多維度分析</h3>
              <p className="text-sm text-gray-600">
                7種策略全方位分析台股，找出潛力標的
              </p>
            </div>
            <div>
              <div className="text-2xl mb-2">🔍</div>
              <h3 className="font-semibold mb-1">即時搜尋篩選</h3>
              <p className="text-sm text-gray-600">
                支援關鍵字搜尋、欄位排序、分頁瀏覽
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 注意事項 */}
      <div className="mt-12 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="font-semibold text-yellow-900 mb-2">⚠️ 免責聲明</h3>
        <p className="text-sm text-yellow-800">
          本平台僅提供資料篩選與分析功能，不構成任何投資建議。投資有風險，請謹慎評估並自行承擔投資決策責任。
        </p>
      </div>
    </div>
  )
}
