# 📊 台股智能分析平台 - 專案摘要

## 🎯 專案概述

這是一個全自動化的台股分析平台，結合了：
- **Python** 資料分析腳本
- **Next.js 15** 現代化前端框架
- **GitHub Actions** 自動化執行
- **Vercel** 無縫部署

## 📂 專案架構總覽

```
台股智能分析平台
│
├── 🤖 自動化層（GitHub Actions）
│   ├── 每日 10:00 → 執行股東持有比例差分析
│   └── 每日 18:00 → 執行股票綜合篩選
│
├── 🐍 資料處理層（Python）
│   ├── 股票綜合篩選.py → 產生 6 個 CSV
│   └── 股東持有比例差.py → 產生 1 個 CSV
│
├── 💾 資料儲存層（GitHub Repository）
│   ├── data/latest/ → 最新資料
│   └── data/history/ → 歷史資料
│
└── 🌐 展示層（Next.js + Vercel）
    ├── 首頁 → 策略介紹
    └── 7 個策略頁面 → 資料展示
```

## 📋 7 種策略說明

| # | 策略名稱 | 篩選條件 | 更新時間 |
|---|---------|---------|---------|
| 1 | 外資大量買超 | 當日買超 > 5000張 或 > 2億元 | 每日 18:00 |
| 2 | 投信連續買超 | 近5日4日買超、平均≥500張 | 每日 18:00 |
| 3 | 強勢股篩選 | 多頭排列、新高、量能大 | 每日 18:00 |
| 4 | 盤整突破 | 成交量爆發、突破盤整 | 每日 18:00 |
| 5 | 族群個股資料 | 族群分類、漲跌幅統計 | 每日 18:00 |
| 6 | 族群排名 | 族群漲幅、法人買賣超 | 每日 18:00 |
| 7 | 大戶持有比例差 | 主力持股變化追蹤 | 每日 10:00 |

## 🛠️ 技術棧詳細

### 前端技術
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **UI Components**: 自製 Card、Table 組件
- **CSV Parser**: PapaParse
- **Font**: Noto Sans TC（中文優化）

### 後端技術
- **Language**: Python 3.11
- **Libraries**:
  - `pandas` - 資料處理
  - `requests` - API 請求
- **Data Source**: FinMind API

### DevOps
- **CI/CD**: GitHub Actions
- **Hosting**: Vercel
- **Version Control**: Git/GitHub

## 📊 資料流程圖

```
[FinMind API]
      ↓
[Python 腳本分析]
      ↓
[產生 CSV 檔案]
      ↓
[提交到 GitHub]
      ↓
[觸發 Vercel 部署]
      ↓
[網站自動更新]
      ↓
[使用者瀏覽最新資料]
```

## 🔐 安全性設計

1. **API Token 保護**
   - Token 僅存於 GitHub Secrets
   - `.gitignore` 排除 `python/token`
   - 前端完全不接觸 Token

2. **資料驗證**
   - CSV 解析錯誤處理
   - 友善的錯誤提示
   - 資料缺失時的備用顯示

## 🚀 部署策略

### 本地開發
```bash
npm run dev        # 啟動前端
cd python && python 股票綜合篩選.py  # 執行分析
```

### 生產環境
1. 推送代碼到 GitHub
2. GitHub Actions 自動執行
3. Vercel 自動部署
4. 全程無需人工介入

## 📈 效能優化

- **靜態生成**: Next.js SSG 提升載入速度
- **批次 API**: Python 腳本批次請求減少延遲
- **資料快取**: CSV 檔案作為靜態資源
- **按需載入**: 分頁系統避免一次載入過多資料

## 🎨 UI/UX 特色

1. **直覺導航**: 頂部固定導航欄
2. **即時搜尋**: 關鍵字搜尋、欄位排序
3. **顏色編碼**: 紅漲綠跌、數值格式化
4. **響應式**: 支援桌面、平板、手機
5. **Loading 狀態**: 載入動畫、錯誤提示

## 📁 核心檔案說明

### GitHub Actions
- `comprehensive-screening.yml` - 股票綜合篩選工作流程
- `shareholder-analysis.yml` - 股東持有比例差工作流程

### Python 腳本
- `股票綜合篩選.py` - 主要分析腳本（6種策略）
- `股東持有比例差.py` - 大戶持股分析
- `requirements.txt` - Python 依賴

### 前端組件
- `app/layout.tsx` - 主要佈局
- `components/Navigation.tsx` - 導航欄
- `components/StrategyPage.tsx` - 策略頁面模板
- `components/DataTable.tsx` - 資料表格

### 文件
- `README.md` - 專案說明
- `DEPLOYMENT.md` - 部署指南
- `TESTING.md` - 測試清單

## 💡 使用情境

### 投資者
- 每日瀏覽外資、投信動向
- 追蹤強勢股、突破股
- 關注族群輪動

### 研究者
- 下載歷史資料分析
- 比對不同策略成效
- 追蹤市場趨勢

### 開發者
- 學習 Next.js + Python 整合
- 了解 GitHub Actions 自動化
- 參考 UI/UX 設計

## 🔄 維護計劃

### 每日
- ✅ 自動執行腳本
- ✅ 自動產生資料
- ✅ 自動部署更新

### 每週
- 檢查 GitHub Actions 執行狀態
- 查看 Vercel 流量統計

### 每月
- 更新 Python 依賴
- 更新 Next.js 依賴
- 檢視並優化效能

## 📊 預期成效

- **時間節省**: 每日自動化省下 30-60 分鐘手動操作
- **資料及時**: 每日固定時間更新，不漏接關鍵資訊
- **易於分享**: 網址分享即可，無需安裝軟體
- **歷史追蹤**: 自動保存歷史資料，方便回溯

## 🎯 未來擴充方向

### 短期（1-3個月）
- [ ] 新增更多篩選策略
- [ ] 資料視覺化圖表
- [ ] 匯出 Excel 功能

### 中期（3-6個月）
- [ ] 歷史資料查詢功能
- [ ] 策略績效回測
- [ ] Email 通知功能

### 長期（6個月以上）
- [ ] AI 預測模型整合
- [ ] 會員系統與個人化設定
- [ ] 行動 App 開發

## 📞 聯絡與支援

- **GitHub Issues**: 回報問題與建議
- **Documentation**: 詳見 README.md
- **Deployment Guide**: 詳見 DEPLOYMENT.md

## 🏆 專案亮點

✨ **全自動化** - 設定一次，永久運行
✨ **零成本** - GitHub + Vercel 免費方案
✨ **高效能** - Next.js 極速載入
✨ **易維護** - 清晰的架構與文件
✨ **可擴充** - 模組化設計便於新增功能

---

**專案狀態**: ✅ 已完成，可立即部署
**最後更新**: 2025-12-08
**版本**: 1.0.0
