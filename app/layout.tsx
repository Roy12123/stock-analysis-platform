import type { Metadata } from "next";
import { Noto_Sans_TC } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";

const notoSansTC = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-noto-sans-tc",
});

export const metadata: Metadata = {
  title: "台股分析平台",
  description: "自動化台股篩選分析系統 - 外資買超、投信買超、強勢股、盤整突破、族群分析、大戶持股",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW">
      <body className={`${notoSansTC.variable} antialiased bg-gray-50`}>
        <Navigation />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-t border-gray-700 py-8 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">📊</span>
                <div className="text-left">
                  <p className="font-bold text-white text-lg bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                    台股分析平台
                  </p>
                  <p className="text-xs text-gray-400">Stock Analysis Platform</p>
                </div>
              </div>
              <div className="text-center md:text-right">
                <div className="flex items-center gap-2 justify-center md:justify-end mb-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  <p className="text-sm text-gray-300 font-medium">
                    資料每日自動更新 | 台北時間 10:00 & 18:00
                  </p>
                </div>
                <p className="text-xs text-gray-400 mb-1">
                  聯絡信箱：<a href="mailto:roy851130@gmail.com" className="text-blue-400 hover:text-blue-300 hover:underline">roy851130@gmail.com</a>
                </p>
                <p className="text-xs text-gray-400">
                  © {new Date().getFullYear()} 台股分析平台. All rights reserved.
                </p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
