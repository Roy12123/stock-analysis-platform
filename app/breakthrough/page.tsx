import StrategyPage from '@/components/StrategyPage'

export default function BreakthroughPage() {
  return (
    <StrategyPage
      title="盤整突破"
      description="成交量 > 20MA的5倍、成交量 > 5000張、近3個交易日內突破"
      fileName="盤整突破.csv"
      icon="🚀"
    />
  )
}
