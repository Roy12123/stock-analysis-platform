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
        <footer className="bg-white border-t border-gray-200 py-6 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
            <p>台股分析平台 © {new Date().getFullYear()}</p>
            <p className="mt-1">資料每日自動更新 | 台北時間 10:00 & 18:00</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
