import StrategyPage from '@/components/StrategyPage'

export default function ForeignInvestmentPage() {
  return (
    <StrategyPage
      title="外資大量買超"
      description="篩選當日外資買超 > 5000張 或 買超金額 > 2億元的股票，包含近期買超統計"
      fileName="外資大量買超.csv"
      icon="🌐"
    />
  )
}
