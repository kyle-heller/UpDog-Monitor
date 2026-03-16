// API base URL - empty for local dev (uses proxy), full URL for production
const API_BASE = import.meta.env.VITE_API_URL || ''

import { getToken } from './auth'

function authHeaders(): Record<string, string> {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface Monitor {                                                                                                
  id: number                                                                                                              
  name: string                                                                                                            
  url: string                                                                                                             
  interval_seconds: number                                                                                                
  is_active: boolean                                                                                                      
  created_at: string                                                                                                      
  updated_at: string                                                                                                      
}                                                                                                                         
                                                                                                                          
export interface CheckResult {                                                                                            
  id: number                                                                                                              
  monitor_id: number                                                                                                      
  status_code: number | null                                                                                              
  response_time_ms: number | null                                                                                         
  is_up: boolean                                                                                                          
  checked_at: string                                                                                                      
  error_message: string | null                                                                                            
}                                                                                                                         
                                                                                                                          
export async function getMonitors(): Promise<Monitor[]> {                                                                 
  const response = await fetch(`${API_BASE}/api/monitors`)                                                                           
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch monitors')                                                                           
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
export async function getMonitor(id: string): Promise<Monitor> {                                                          
  const response = await fetch(`${API_BASE}/api/monitors/${id}`)                                                                     
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch monitor')                                                                            
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
export async function getMonitorResults(id: string, limit = 20): Promise<CheckResult[]> {                                 
  const response = await fetch(`${API_BASE}/api/monitors/${id}/results?limit=${limit}`)                                              
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch results')                                                                            
  }                                                                                                                       
  return response.json()                                                                                                  
}

export async function createMonitor(data: {
  name: string
  url: string
  interval_seconds?: number
}): Promise<Monitor> {
  const response = await fetch(`${API_BASE}/api/monitors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error('Failed to create monitor')
  }
  return response.json()
}                                                                                                                         
                                                                                                                            
export async function updateMonitor(                                                                                      
  id: string,                                                                                                             
  data: {                                                                                                                 
    name?: string                                                                                                         
    url?: string                                                                                                          
    interval_seconds?: number                                                                                             
    is_active?: boolean                                                                                                   
  }                                                                                                                       
): Promise<Monitor> {                                                                                                     
  const response = await fetch(`${API_BASE}/api/monitors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),                                                                                           
  })                                                                                                                      
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to update monitor')                                                                           
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
export async function deleteMonitor(id: string): Promise<void> {                                                          
  const response = await fetch(`${API_BASE}/api/monitors/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })                                                                                                                      
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to delete monitor')                                                                           
  }                                                                                                                       
}
