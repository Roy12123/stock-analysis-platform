'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

const strategies = [
  { name: '首頁', href: '/', icon: '🏠' },
  { name: '外資大量買超', href: '/foreign-investment', icon: '🌐' },
  { name: '投信連續買超', href: '/investment-trust', icon: '🏦' },
  { name: '強勢股篩選', href: '/strong-stocks', icon: '📈' },
  { name: '盤整突破', href: '/breakthrough', icon: '🚀' },
  { name: '族群個股資料', href: '/category-stocks', icon: '📊' },
  { name: '族群排名', href: '/category-ranking', icon: '🏆' },
  { name: '大戶持有比例差', href: '/shareholder', icon: '💎' },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-2xl">📊</span>
              <span className="text-xl font-bold text-gray-800">台股分析平台</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 水平選單 */}
      <div className="border-t border-gray-200 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex overflow-x-auto hide-scrollbar">
            {strategies.map((strategy) => {
              const isActive = pathname === strategy.href
              return (
                <Link
                  key={strategy.href}
                  href={strategy.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors',
                    isActive
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
                  )}
                >
                  <span>{strategy.icon}</span>
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
