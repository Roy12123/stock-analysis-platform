import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 格式化日期
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(date)
  } catch {
    return dateString
  }
}

// 格式化數字（千分位）
export function formatNumber(num: number | string): string {
  const numValue = typeof num === 'string' ? parseFloat(num) : num
  if (isNaN(numValue)) return '-'
  return new Intl.NumberFormat('zh-TW').format(numValue)
}

// 格式化百分比
export function formatPercent(num: number | string): string {
  const numValue = typeof num === 'string' ? parseFloat(num) : num
  if (isNaN(numValue)) return '-'
  const sign = numValue > 0 ? '+' : ''
  return `${sign}${numValue.toFixed(2)}%`
}

// 取得漲跌顏色
export function getPriceColor(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return 'text-gray-600'
  if (numValue > 0) return 'text-red-600'
  if (numValue < 0) return 'text-green-600'
  return 'text-gray-600'
}
