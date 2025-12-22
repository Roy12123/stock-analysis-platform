import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), 'data/latest/隔日衝_篩選結果.csv');

    // 檢查檔案是否存在
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({
        success: false,
        error: '篩選結果尚未產生，請等待今日 13:20 後再查看',
        data: [],
      }, { status: 404 });
    }

    const fileContent = fs.readFileSync(filePath, 'utf-8');

    const parsed = Papa.parse(fileContent, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true, // 自動轉換數字型態
    });

    const stats = fs.statSync(filePath);

    return NextResponse.json({
      success: true,
      data: parsed.data,
      timestamp: stats.mtime,
      count: parsed.data.length,
      updateTime: stats.mtime.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }),
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({
      success: false,
      error: '無法讀取資料',
      details: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
  }
}
