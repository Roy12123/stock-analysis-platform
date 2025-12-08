import StrategyPage from '@/components/StrategyPage'

export default function StrongStocksPage() {
  return (
    <StrategyPage
      title="強勢股篩選"
      description="多頭排列（10MA > 20MA > 60MA）、近10日最高、漲幅>0050、成交量>10000張、量能比≥1.5"
      fileName="強勢股篩選.csv"
      icon="📈"
    />
  )
}
