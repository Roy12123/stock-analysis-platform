'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useLastUpdate } from '@/hooks/useLastUpdate'

const strategies = [
  { name: '首頁', href: '/', icon: '🏠' },
  { name: '隔日衝策略', href: '/daily-rush', icon: '🚀' },
  { name: '外資大量買超', href: '/foreign-investment', icon: '🌐' },
  { name: '投信連續買超', href: '/investment-trust', icon: '🏦' },
  { name: '強勢股篩選', href: '/strong-stocks', icon: '📈' },
  { name: '盤整突破', href: '/breakthrough', icon: '🔥' },
  { name: '族群排名', href: '/category-ranking', icon: '🏆' },
  { name: '族群個股資料', href: '/category-stocks', icon: '📊' },
  { name: '大戶持有比例差', href: '/shareholder', icon: '💎' },
]

export default function Navigation() {
  const pathname = usePathname()
  const { updateData, loading } = useLastUpdate()

  return (
    <nav className="bg-white/95 backdrop-blur-md border-b border-gray-200/80 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-3 group">
              <span className="text-3xl transition-transform group-hover:scale-110">📊</span>
              <div className="flex flex-col">
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                  台股分析平台
                </span>
                <span className="text-xs text-gray-500">Stock Analysis Platform</span>
              </div>
            </Link>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <div className="flex flex-col items-end gap-0.5">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-full border border-blue-200">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-xs font-medium text-gray-700">每日更新 10:00 & 18:00</span>
              </div>
              {!loading && updateData?.stock_analysis && (
                <span className="text-xs text-gray-500 px-2">
                  最後更新: {updateData.stock_analysis.updated_at.split(' ')[0]} {updateData.stock_analysis.updated_at.split(' ')[1]}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 水平選單 */}
      <div className="border-t border-gray-200/80 bg-gradient-to-r from-gray-50 to-blue-50/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex overflow-x-auto hide-scrollbar gap-1">
            {strategies.map((strategy) => {
              const isActive = pathname === strategy.href
              return (
                <Link
                  key={strategy.href}
                  href={strategy.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 rounded-t-lg',
                    isActive
                      ? 'border-blue-600 text-blue-600 bg-white shadow-sm'
                      : 'border-transparent text-gray-600 hover:text-blue-600 hover:bg-white/50 hover:border-blue-300'
                  )}
                >
                  <span className="text-base transition-transform hover:scale-110">{strategy.icon}</span>
                  <span>{strategy.name}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>

      <style jsx>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </nav>
  )
}
