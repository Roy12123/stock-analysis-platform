# ✅ 測試清單

在部署前，請依照以下清單進行測試。

## 🖥️ 本地開發測試

### 1. 環境設置
- [ ] Node.js 版本 >= 18
- [ ] Python 版本 >= 3.11
- [ ] 已取得 FinMind API Token

### 2. 安裝依賴
```bash
# 前端依賴
npm install

# Python 依賴
cd python
pip install -r requirements.txt
cd ..
```

### 3. 測試前端
```bash
# 啟動開發伺服器
npm run dev

# 開啟瀏覽器訪問 http://localhost:3000
```

**檢查項目：**
- [ ] 首頁正常顯示
- [ ] 7個策略卡片都可以點擊
- [ ] 導航欄正確顯示所有分頁
- [ ] 點擊各分頁，顯示「資料尚未準備」提示（正常）

### 4. 測試 Python 腳本

在執行前，確認：
- [ ] `python/token` 檔案已創建並包含有效的 API Token
- [ ] `python/(all)stock_info_list.csv` 存在
- [ ] `python/stock_category.csv` 存在

執行測試：
```bash
cd python

# 測試股票綜合篩選（執行時間約 2-5 分鐘）
python 股票綜合篩選.py

# 應該產生以下檔案：
# - YYYYMMDD_外資大量買超.csv
# - YYYYMMDD_投信連續買超.csv
# - YYYYMMDD_強勢股篩選.csv
# - YYYYMMDD_盤整突破.csv
# - YYYYMMDD_族群個股資料.csv
# - YYYYMMDD_族群排名.csv
```

```bash
# 測試股東持有比例差（執行時間約 1-3 分鐘）
python 股東持有比例差.py

# 應該產生檔案：
# - YYYY-MM-DD_YYYY-MM-DD大戶持有比例差.csv
```

**檢查項目：**
- [ ] 腳本執行無錯誤
- [ ] CSV 檔案成功產生
- [ ] 開啟 CSV 檔案，確認資料正確且有內容

### 5. 測試前端讀取資料

將產生的 CSV 檔案移動到前端：
```bash
# 創建測試資料目錄
mkdir -p public/data/latest

# 移動檔案（簡化檔名）
mv python/*_外資大量買超.csv public/data/latest/外資大量買超.csv
mv python/*_投信連續買超.csv public/data/latest/投信連續買超.csv
mv python/*_強勢股篩選.csv public/data/latest/強勢股篩選.csv
mv python/*_盤整突破.csv public/data/latest/盤整突破.csv
mv python/*_族群個股資料.csv public/data/latest/族群個股資料.csv
mv python/*_族群排名.csv public/data/latest/族群排名.csv
mv python/*大戶持有比例差.csv public/data/latest/大戶持有比例差.csv
```

重新整理瀏覽器（http://localhost:3000）：

**檢查項目：**
- [ ] 外資大量買超頁面顯示資料表格
- [ ] 投信連續買超頁面顯示資料表格
- [ ] 強勢股篩選頁面顯示資料表格
- [ ] 盤整突破頁面顯示資料表格
- [ ] 族群個股資料頁面顯示資料表格
- [ ] 族群排名頁面顯示資料表格
- [ ] 大戶持有比例差頁面顯示資料表格

### 6. 測試表格功能

在任一資料頁面：
- [ ] 搜尋框輸入股票代碼或公司名稱，能正確篩選
- [ ] 點擊表格標題，能正確排序（升序/降序）
- [ ] 分頁功能正常（如果資料超過20筆）
- [ ] 數字格式正確顯示千分位
- [ ] 漲跌幅顯示正確顏色（紅漲綠跌）

### 7. 測試建置

```bash
npm run build
npm run start
```

**檢查項目：**
- [ ] 建置成功，無錯誤
- [ ] 生產環境啟動成功
- [ ] 所有頁面正常運作

## 🐙 GitHub 測試

### 1. Git 設置
```bash
# 確認 .gitignore 正確
cat .gitignore | grep token  # 應該有 "python/token" 和 "token"

# 確認 token 不會被提交
git status  # python/token 應該不在列表中
```

### 2. 推送到 GitHub
```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**檢查項目：**
- [ ] 代碼成功推送
- [ ] `python/token` 檔案**沒有**被推送（重要！）
- [ ] GitHub 可以看到所有檔案

### 3. 設置 GitHub Secrets
- [ ] 在 Settings → Secrets → Actions 設置 `FINMIND_TOKEN`

### 4. 測試 GitHub Actions

手動執行 Workflow：
- [ ] Actions → 股票綜合篩選 → Run workflow
- [ ] Actions → 股東持有比例差 → Run workflow

**檢查項目：**
- [ ] Workflow 執行成功（綠色勾勾）
- [ ] `data/latest/` 目錄出現 CSV 檔案
- [ ] CSV 檔案內容正確

## 🌍 Vercel 測試

### 1. 部署到 Vercel
- [ ] Import GitHub Repository
- [ ] 選擇 Next.js Framework
- [ ] 點擊 Deploy

### 2. 驗證部署
- [ ] 部署成功，無錯誤
- [ ] 訪問 Vercel 提供的網址
- [ ] 首頁正常顯示

### 3. 測試資料顯示

如果顯示「資料尚未準備」：
1. 回到 GitHub Actions 手動執行 workflow
2. 等待執行完成
3. Vercel 會自動重新部署
4. 重新整理網站

**檢查項目：**
- [ ] 所有7個策略頁面都能顯示資料
- [ ] 表格功能正常（搜尋、排序、分頁）
- [ ] 手機瀏覽器測試（響應式設計）
- [ ] 不同瀏覽器測試（Chrome, Safari, Firefox）

## 🔄 自動化測試

### 等待第一次自動執行

在部署後的隔天：
- [ ] 台北時間 10:00 後，檢查是否有新的 commit（股東持有比例差）
- [ ] 台北時間 18:00 後，檢查是否有新的 commit（股票綜合篩選）
- [ ] Vercel 是否自動重新部署
- [ ] 網站資料是否自動更新

## 📊 效能測試

使用 Lighthouse 測試（Chrome DevTools）：
- [ ] Performance > 80 分
- [ ] Accessibility > 90 分
- [ ] Best Practices > 90 分
- [ ] SEO > 90 分

## 🐛 錯誤處理測試

### 測試各種錯誤情況
- [ ] 刪除某個 CSV 檔案，該頁面應顯示「資料尚未準備」
- [ ] CSV 檔案格式錯誤，應有友善的錯誤提示
- [ ] 網路斷線時的行為

## ✅ 最終檢查清單

部署前最後確認：
- [ ] 所有功能都已測試
- [ ] README.md 完整且正確
- [ ] DEPLOYMENT.md 清楚易懂
- [ ] .gitignore 正確設置（token 不會被提交）
- [ ] GitHub Secrets 已設置
- [ ] GitHub Actions 測試成功
- [ ] Vercel 部署成功
- [ ] 網站可以正常訪問
- [ ] 所有資料頁面都能顯示

## 🎉 測試完成！

如果以上所有項目都打勾，恭喜您！專案已經準備好投入使用了。

---

**祝測試順利！** 🚀
