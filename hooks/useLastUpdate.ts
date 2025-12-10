'use client'

import { useState, useEffect } from 'react'

interface UpdateInfo {
  updated_at: string
  trade_date?: string
  start_date?: string
  end_date?: string
  timezone: string
}

interface LastUpdateData {
  stock_analysis?: UpdateInfo
  shareholder?: UpdateInfo
}

export function useLastUpdate() {
  const [updateData, setUpdateData] = useState<LastUpdateData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchUpdateInfo() {
      try {
        const response = await fetch('/last_update.json')
        if (response.ok) {
          const data = await response.json()
          setUpdateData(data)
        }
      } catch (error) {
        console.error('Failed to fetch update info:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchUpdateInfo()
  }, [])

  return { updateData, loading }
}
