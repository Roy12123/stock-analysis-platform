# 🚀 部署指南

本文件說明如何將台股智能分析平台部署到 GitHub 和 Vercel。

## 📋 前置準備

### 1. 準備 FinMind API Token

1. 前往 [FinMind](https://finmindtrade.com/) 註冊帳號
2. 登入後取得 API Token
3. 保存您的 Token，稍後會用到

### 2. 檢查專案檔案

確認以下檔案都已準備好：
- ✅ `python/股票綜合篩選.py`
- ✅ `python/股東持有比例差.py`
- ✅ `python/(all)stock_info_list.csv`
- ✅ `python/stock_category.csv`
- ✅ `python/requirements.txt`
- ✅ `.github/workflows/comprehensive-screening.yml`
- ✅ `.github/workflows/shareholder-analysis.yml`

## 🌐 步驟 1: 上傳到 GitHub

### 1.1 初始化 Git（如果尚未初始化）

```bash
cd stock-analysis-platform
git init
git add .
git commit -m "Initial commit: 台股智能分析平台"
```

### 1.2 在 GitHub 創建新的 Repository

1. 前往 [GitHub](https://github.com/) 並登入
2. 點擊右上角的 "+" → "New repository"
3. Repository name: `stock-analysis-platform` (或您想要的名稱)
4. 選擇 **Public** 或 **Private**
5. **不要**勾選 "Initialize this repository with a README"
6. 點擊 "Create repository"

### 1.3 推送代碼到 GitHub

```bash
# 替換成您的 GitHub username 和 repository name
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-platform.git
git branch -M main
git push -u origin main
```

### 1.4 設置 GitHub Secrets

這是**最重要**的步驟！

1. 前往您的 GitHub Repository 頁面
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **New repository secret**
4. Name: `FINMIND_TOKEN`
5. Value: 貼上您的 FinMind API Token
6. 點擊 **Add secret**

## ⚙️ 步驟 2: 測試 GitHub Actions

### 2.1 手動觸發 Workflow

1. 前往 Repository 的 **Actions** 頁籤
2. 選擇左側的 **股票綜合篩選** 或 **股東持有比例差**
3. 點擊右側的 **Run workflow** → **Run workflow**
4. 等待執行完成（約 2-5 分鐘）

### 2.2 檢查執行結果

1. 點擊剛才的 workflow run
2. 查看各個步驟是否都成功（綠色勾勾）
3. 如果失敗，點擊失敗的步驟查看錯誤訊息

### 2.3 確認資料已產生

執行成功後，到 Repository 的 **Code** 頁面：
1. 進入 `data/latest/` 目錄
2. 應該會看到生成的 CSV 檔案（例如：外資大量買超.csv）

## 🌍 步驟 3: 部署到 Vercel

### 3.1 登入 Vercel

1. 前往 [Vercel](https://vercel.com/)
2. 使用 GitHub 帳號登入（推薦）

### 3.2 Import 專案

1. 點擊 **Add New...** → **Project**
2. 選擇您的 GitHub Repository: `stock-analysis-platform`
3. 點擊 **Import**

### 3.3 配置專案設定

在 Configure Project 頁面：

| 設定項目 | 值 |
|---------|---|
| Framework Preset | Next.js |
| Root Directory | ./ |
| Build Command | `npm run build` (預設) |
| Output Directory | `.next` (預設) |
| Install Command | `npm install` (預設) |

**不需要設置任何環境變數**（因為前端不需要 API Token）

### 3.4 部署

1. 點擊 **Deploy**
2. 等待建置完成（約 1-3 分鐘）
3. 部署成功後會顯示您的網站連結

## ✅ 步驟 4: 驗證部署

### 4.1 測試網站

1. 點擊 Vercel 提供的網址（例如：`your-project.vercel.app`）
2. 確認首頁正常顯示
3. 點擊各個策略分頁，應該會看到「資料尚未準備」的提示（正常，因為 CSV 檔案還在 GitHub Actions 產生中）

### 4.2 等待資料更新

首次部署後，您需要：
1. 回到 GitHub Actions 手動執行兩個 workflow
2. 等待執行完成並產生 CSV 檔案
3. Vercel 會自動偵測到新的 commit 並重新部署
4. 重新整理網站，應該就能看到資料了

## 🔄 日常運作流程

部署完成後，系統會自動運作：

```
每天 10:00 (台北時間)
  ↓
GitHub Actions 執行「股東持有比例差」
  ↓
產生 CSV → 提交到 data/latest/
  ↓
GitHub 推送變更
  ↓
Vercel 自動偵測並重新部署
  ↓
網站顯示最新資料

------

每天 18:00 (台北時間)
  ↓
GitHub Actions 執行「股票綜合篩選」
  ↓
產生 6 個 CSV → 提交到 data/latest/
  ↓
GitHub 推送變更
  ↓
Vercel 自動偵測並重新部署
  ↓
網站顯示最新資料
```

## 🐛 常見問題

### Q: GitHub Actions 執行失敗，顯示 "401 Unauthorized"

**A:** 檢查 GitHub Secret `FINMIND_TOKEN` 是否設置正確
- 重新檢查 Token 是否有效
- 確認 Secret 名稱拼寫正確（大小寫敏感）

### Q: 網站顯示「資料尚未準備」

**A:** 這是正常的，有幾種可能：
1. GitHub Actions 還沒執行過（手動執行一次即可）
2. CSV 檔案還沒產生（檢查 Actions 日誌）
3. CSV 檔案路徑不正確（應該在 `public/data/latest/`）

### Q: Vercel 建置失敗

**A:** 常見原因：
1. 檢查 Node.js 版本是否相容（建議 18+）
2. 確認所有依賴都已安裝（`npm install`）
3. 查看 Vercel 建置日誌找出具體錯誤

### Q: 如何自訂網域？

**A:** 在 Vercel 專案設定中：
1. Settings → Domains
2. 輸入您的網域
3. 按照指示設置 DNS

### Q: 如何修改執行時間？

**A:** 編輯 `.github/workflows/*.yml` 中的 cron 表達式：
```yaml
schedule:
  - cron: '0 10 * * *'  # UTC 時間
```

## 📊 監控與維護

### 查看 GitHub Actions 執行狀態

- 前往 Repository → Actions
- 可以看到所有執行歷史
- 失敗的會標示紅色 ❌

### 查看 Vercel 部署狀態

- 前往 Vercel Dashboard
- 點擊您的專案
- 可以看到所有部署歷史

### 查看 Vercel 流量統計

- Vercel Dashboard → Analytics
- 可以看到訪問量、效能指標等

## 🎉 完成！

恭喜！您已成功部署台股智能分析平台。

系統現在會：
- ✅ 每天自動執行 Python 腳本
- ✅ 自動產生分析資料
- ✅ 自動更新網站內容
- ✅ 提供即時的股票篩選資訊

## 📧 需要協助？

如果遇到問題：
1. 檢查 GitHub Actions 日誌
2. 檢查 Vercel 建置日誌
3. 參考 README.md 的疑難排解章節

---

**祝您使用愉快！** 📈
