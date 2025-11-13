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
                                                                                                                          
export interface CheckResult {                                                                                            
  id: number                                                                                                              
  monitor_id: number                                                                                                      
  status_code: number | null                                                                                              
  response_time_ms: number | null                                                                                         
  is_up: boolean                                                                                                          
  checked_at: string                                                                                                      
  error_message: string | null                                                                                            
}                                                                                                                         
                                                                                                                          
// Fetch all monitors from the backend                                                                                    
export async function getMonitors(): Promise<Monitor[]> {                                                                 
  const response = await fetch('/api/monitors')                                                                           
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch monitors')                                                                           
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
// Fetch a single monitor by ID                                                                                           
export async function getMonitor(id: string): Promise<Monitor> {                                                          
  const response = await fetch(`/api/monitors/${id}`)                                                                     
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch monitor')                                                                            
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
// Fetch check results for a monitor                                                                                      
export async function getMonitorResults(id: string, limit = 20): Promise<CheckResult[]> {                                 
  const response = await fetch(`/api/monitors/${id}/results?limit=${limit}`)                                              
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to fetch results')                                                                            
  }                                                                                                                       
  return response.json()                                                                                                  
}

// Create a new monitor                                                                                                   
  export async function createMonitor(data: {                                                                               
    name: string                                                                                                            
    url: string                                                                                                             
    interval_seconds?: number                                                                                               
  }): Promise<Monitor> {                                                                                                    
    const response = await fetch('/api/monitors', {                                                                         
      method: 'POST',                                                                                                       
      headers: { 'Content-Type': 'application/json' },                                                                      
      body: JSON.stringify(data),                                                                                           
    })                                                                                                                      
    if (!response.ok) {                                                                                                     
      throw new Error('Failed to create monitor')                                                                           
    }                                                                                                                       
    return response.json()                                                                                                  
  }                                                                                                                         
                                                                                                                            
// Update a monitor                                                                                                       
export async function updateMonitor(                                                                                      
  id: string,                                                                                                             
  data: {                                                                                                                 
    name?: string                                                                                                         
    url?: string                                                                                                          
    interval_seconds?: number                                                                                             
    is_active?: boolean                                                                                                   
  }                                                                                                                       
): Promise<Monitor> {                                                                                                     
  const response = await fetch(`/api/monitors/${id}`, {                                                                   
    method: 'PUT',                                                                                                        
    headers: { 'Content-Type': 'application/json' },                                                                      
    body: JSON.stringify(data),                                                                                           
  })                                                                                                                      
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to update monitor')                                                                           
  }                                                                                                                       
  return response.json()                                                                                                  
}                                                                                                                         
                                                                                                                          
// Delete a monitor                                                                                                       
export async function deleteMonitor(id: string): Promise<void> {                                                          
  const response = await fetch(`/api/monitors/${id}`, {                                                                   
    method: 'DELETE',                                                                                                     
  })                                                                                                                      
  if (!response.ok) {                                                                                                     
    throw new Error('Failed to delete monitor')                                                                           
  }                                                                                                                       
}