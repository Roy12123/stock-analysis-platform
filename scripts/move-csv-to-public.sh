#!/bin/bash

# 移動 Python 產生的 CSV 到前端 public 目錄的腳本
# 用於本地測試

echo "📦 移動 CSV 檔案到 public/data/latest/"

# 創建目錄
mkdir -p public/data/latest

# 移動檔案
echo "  移動外資大量買超..."
mv python/*_外資大量買超.csv public/data/latest/外資大量買超.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動投信連續買超..."
mv python/*_投信連續買超.csv public/data/latest/投信連續買超.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動強勢股篩選..."
mv python/*_強勢股篩選.csv public/data/latest/強勢股篩選.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動盤整突破..."
mv python/*_盤整突破.csv public/data/latest/盤整突破.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動族群個股資料..."
mv python/*_族群個股資料.csv public/data/latest/族群個股資料.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動族群排名..."
mv python/*_族群排名.csv public/data/latest/族群排名.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo "  移動大戶持有比例差..."
mv python/*大戶持有比例差.csv public/data/latest/大戶持有比例差.csv 2>/dev/null || echo "  ⚠️  檔案不存在"

echo ""
echo "✅ 完成！查看結果："
ls -lh public/data/latest/

echo ""
echo "💡 提示：現在可以重新整理瀏覽器查看資料"
