import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 強制使用客戶端渲染，避免 SSR 快取
  output: 'export',
  // GitHub Pages 需要設置 basePath
  basePath: process.env.NODE_ENV === 'production' ? '/stock-analysis-platform' : '',
  // 確保圖片和資源使用相對路徑
  images: {
    unoptimized: true,
  },
}

export default nextConfig;

