import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 強制使用客戶端渲染，避免 SSR 快取
  output: 'export',
}

export default nextConfig;

