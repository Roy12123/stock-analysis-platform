# 🚀 立即部署指南

代碼已經準備好了！按照以下步驟部署到 GitHub + Vercel。

---

## 步驟 1: 在 GitHub 創建 Repository

### 1.1 前往 GitHub
打開瀏覽器，前往：https://github.com/new

### 1.2 填寫資訊
- **Repository name**: `stock-analysis-platform` (或您喜歡的名稱)
- **Description**: 台股分析平台 - 自動化篩選分析系統
- **Visibility**:
  - 選擇 **Public** (推薦，Vercel 免費部署)
  - 或 **Private** (需要 Vercel Pro)
- **不要**勾選 "Initialize this repository with a README"
- 點擊 **Create repository**

---

## 步驟 2: 推送代碼到 GitHub

### 2.1 複製以下命令（GitHub 會提供）

GitHub 創建完成後會顯示類似這樣的命令：

```bash
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-platform.git
git branch -M main
git push -u origin main
```

### 2.2 在終端執行

**打開新的終端視窗**，執行：

```bash
cd /Users/roysmacbook/Desktop/策略網站備份/stock-analysis-platform

# 替換成您的 GitHub username 和 repository name
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-platform.git
git branch -M main
git push -u origin main
```

**輸入 GitHub 帳號密碼**（或使用 Personal Access Token）

---

## 步驟 3: 設置 GitHub Secret (重要！)

### 3.1 前往 GitHub Repository 設定
在 GitHub Repository 頁面，點擊：
**Settings** → **Secrets and variables** → **Actions**

### 3.2 新增 Secret
1. 點擊 **New repository secret**
2. Name: `FINMIND_TOKEN`
3. Value: 貼上您的 FinMind API Token
4. 點擊 **Add secret**

**⚠️ 沒有這個 Secret，GitHub Actions 無法執行！**

---

## 步驟 4: 測試 GitHub Actions（可選但推薦）

### 4.1 前往 Actions 頁面
在 GitHub Repository，點擊 **Actions** 頁籤

### 4.2 手動執行測試
1. 左側選擇 **股票綜合篩選** 或 **股東持有比例差**
2. 點擊右側 **Run workflow** → **Run workflow**
3. 等待執行完成（約 2-5 分鐘）

### 4.3 檢查結果
- ✅ 綠色勾勾：成功！
- ❌ 紅色叉叉：失敗，點進去看錯誤訊息

**如果成功**，您會在 `data/latest/` 目錄看到產生的 CSV 檔案

---

## 步驟 5: 部署到 Vercel

### 5.1 前往 Vercel
打開瀏覽器：https://vercel.com/

### 5.2 登入
- 點擊 **Sign Up** 或 **Log In**
- 選擇 **Continue with GitHub** (推薦)
- 授權 Vercel 存取您的 GitHub

### 5.3 Import Project
1. 點擊 **Add New...** → **Project**
2. 找到您的 repository: `stock-analysis-platform`
3. 點擊 **Import**

### 5.4 配置專案
- **Framework Preset**: Next.js (自動偵測)
- **Root Directory**: `./` (預設)
- **Build Command**: `npm run build` (預設)
- **Output Directory**: `.next` (預設)
- **Environment Variables**: 不需要設置（前端不需要 Token）

### 5.5 部署
1. 點擊 **Deploy**
2. 等待建置完成（約 1-3 分鐘）
3. 看到 🎉 恭喜畫面就成功了！

### 5.6 取得網址
Vercel 會提供一個網址，例如：
```
https://stock-analysis-platform.vercel.app
```

---

## 步驟 6: 驗證部署

### 6.1 打開網站
點擊 Vercel 提供的網址

### 6.2 檢查
- ✅ 首頁正常顯示
- ✅ 7 個策略卡片都能點擊
- ⚠️ 資料頁面可能顯示「資料尚未準備」（正常）

### 6.3 等待資料
- 如果顯示「資料尚未準備」，回到 GitHub Actions 手動執行一次
- 執行完成後，Vercel 會自動重新部署
- 重新整理網站，應該就能看到資料了！

---

## 🎉 完成！

恭喜！您的台股分析平台已經上線了！

### 自動化流程
從現在開始，系統會自動：
- ✅ 每天 10:00 (台北時間) 執行股東持有比例差分析
- ✅ 每天 18:00 (台北時間) 執行股票綜合篩選
- ✅ 自動推送資料到 GitHub
- ✅ Vercel 自動偵測並重新部署
- ✅ 網站自動更新最新資料

### 後續管理
- 查看執行狀態：GitHub → Actions
- 查看部署狀態：Vercel Dashboard
- 查看網站流量：Vercel → Analytics

---

## ⚠️ 疑難排解

### GitHub Actions 執行失敗
**檢查**：
1. GitHub Secret `FINMIND_TOKEN` 是否設置正確
2. Token 是否有效（登入 FinMind 確認）
3. 查看 Actions 日誌找出錯誤

### Vercel 建置失敗
**檢查**：
1. Node.js 版本（應該 >= 18）
2. 依賴是否正確安裝
3. 查看 Vercel 建置日誌

### 網站顯示「資料尚未準備」
**解決**：
1. 確認 GitHub Actions 已成功執行
2. 確認 `data/latest/` 目錄有 CSV 檔案
3. 強制重新整理瀏覽器 (Cmd + Shift + R)

---

## 📞 需要幫助？

如果遇到問題，請檢查：
1. README.md - 完整專案說明
2. DEPLOYMENT.md - 詳細部署指南
3. TESTING.md - 測試清單

---

**祝您部署順利！** 🚀
