import { useEffect, useState } from 'react'                                                                               
import { useParams, Link } from 'react-router-dom'                                                                        
import type { Monitor, CheckResult } from '../api/monitors'                                                               
import { getMonitor, getMonitorResults } from '../api/monitors'                                                           
                                                                                                                          
function MonitorDetail() {                                                                                                
  const { id } = useParams()                                                                                              
  const [monitor, setMonitor] = useState<Monitor | null>(null)                                                            
  const [results, setResults] = useState<CheckResult[]>([])                                                               
  const [loading, setLoading] = useState(true)                                                                            
  const [error, setError] = useState<string | null>(null)                                                                 
                                                                                                                          
  useEffect(() => {                                                                                                       
    if (!id) return                                                                                                       
                                                                                                                          
    Promise.all([getMonitor(id), getMonitorResults(id)])                                                                  
      .then(([monitorData, resultsData]) => {                                                                             
        setMonitor(monitorData)                                                                                           
        setResults(resultsData)                                                                                           
        setLoading(false)                                                                                                 
      })                                                                                                                  
      .catch((err) => {                                                                                                   
        setError(err.message)                                                                                             
        setLoading(false)                                                                                                 
      })                                                                                                                  
  }, [id])                                                                                                                
                                                                                                                          
  if (loading) return <p>Loading...</p>                                                                                   
  if (error) return <p>Error: {error}</p>                                                                                 
  if (!monitor) return <p>Monitor not found</p>                                                                           
                                                                                                                          
  return (                                                                                                                
    <div>                                                                                                                 
      <Link to="/">← Back to Dashboard</Link>                                                                             
                                                                                                                          
      <h1>{monitor.name}</h1>                                                                                             
      <p>URL: {monitor.url}</p>                                                                                           
      <p>Status: {monitor.is_active ? 'Active' : 'Paused'}</p>                                                            
      <p>Check interval: {monitor.interval_seconds} seconds</p>                                                           
                                                                                                                          
      <h2>Recent Checks</h2>                                                                                              
      {results.length === 0 ? (                                                                                           
        <p>No check results yet.</p>                                                                                      
      ) : (                                                                                                               
        <table>                                                                                                           
          <thead>                                                                                                         
            <tr>                                                                                                          
              <th>Time</th>                                                                                               
              <th>Status</th>                                                                                             
              <th>Response Time</th>                                                                                      
              <th>Error</th>                                                                                              
            </tr>                                                                                                         
          </thead>                                                                                                        
          <tbody>                                                                                                         
            {results.map((result) => (                                                                                    
              <tr key={result.id}>                                                                                        
                <td>{new Date(result.checked_at).toLocaleString()}</td>                                                   
                <td>{result.is_up ? '✓ Up' : '✗ Down'}</td>                                                               
                <td>{result.response_time_ms ? `${result.response_time_ms}ms` : '-'}</td>                                 
                <td>{result.error_message || '-'}</td>                                                                    
              </tr>                                                                                                       
            ))}                                                                                                           
          </tbody>                                                                                                        
        </table>                                                                                                          
      )}                                                                                                                  
    </div>                                                                                                                
  )                                                                                                                       
}                                                                                                                         
                                                                                                                          
export default MonitorDetail  