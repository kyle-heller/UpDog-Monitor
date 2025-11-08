// Types that match backend's Pydantic schemas
export interface Monitor {
  id: number
  name: string
  url: string
  interval_seconds: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// Fetch all monitors from the backend
export async function getMonitors(): Promise<Monitor[]> {
  const response = await fetch('/api/monitors')
  if (!response.ok) {
    throw new Error('Failed to fetch monitors')
  }
  return response.json()
}
