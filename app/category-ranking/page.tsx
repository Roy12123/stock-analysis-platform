'use client'

import StrategyPage from '@/components/StrategyPage'

export default function CategoryRankingPage() {
  return (
    <StrategyPage
      title="族群排名"
      description="族群平均漲幅排名、上漲檔數統計、外資與投信近期買賣超金額"
      fileName="族群排名.csv"
      icon="🏆"
    />
  )
}
