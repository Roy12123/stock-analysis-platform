'use client'

import StrategyPage from '@/components/StrategyPage'

export default function InvestmentTrustPage() {
  return (
    <StrategyPage
      title="投信連續買超"
      description="近5日有4日投信買超、平均買超≥500張、價格波動≤14%、股價≤1000元"
      fileName="投信連續買超.csv"
      icon="🏦"
    />
  )
}
