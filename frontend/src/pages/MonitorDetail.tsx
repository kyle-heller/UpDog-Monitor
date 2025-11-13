import { useEffect, useState } from 'react'                                                                               
  import { useParams, Link, useNavigate } from 'react-router-dom'                                                           
  import type { Monitor, CheckResult } from '../api/monitors'                                                               
  import { getMonitor, getMonitorResults, updateMonitor, deleteMonitor } from '../api/monitors'                             
                                                                                                                            
  function MonitorDetail() {                                                                                                
    const { id } = useParams()                                                                                              
    const navigate = useNavigate()                                                                                          
    const [monitor, setMonitor] = useState<Monitor | null>(null)                                                            
    const [results, setResults] = useState<CheckResult[]>([])                                                               
    const [loading, setLoading] = useState(true)                                                                            
    const [error, setError] = useState<string | null>(null)                                                                 
                                                                                                                            
    // Edit mode state                                                                                                      
    const [editing, setEditing] = useState(false)                                                                           
    const [editName, setEditName] = useState('')                                                                            
    const [editUrl, setEditUrl] = useState('')                                                                              
    const [editInterval, setEditInterval] = useState(60)                                                                    
                                                                                                                            
    useEffect(() => {                                                                                                       
      if (!id) return                                                                                                       
                                                                                                                            
      Promise.all([getMonitor(id), getMonitorResults(id)])                                                                  
        .then(([monitorData, resultsData]) => {                                                                             
          setMonitor(monitorData)                                                                                           
          setResults(resultsData)                                                                                           
          // Initialize edit form with current values                                                                       
          setEditName(monitorData.name)                                                                                     
          setEditUrl(monitorData.url)                                                                                       
          setEditInterval(monitorData.interval_seconds)                                                                     
          setLoading(false)                                                                                                 
        })                                                                                                                  
        .catch((err) => {                                                                                                   
          setError(err.message)                                                                                             
          setLoading(false)                                                                                                 
        })                                                                                                                  
    }, [id])                                                                                                                
                                                                                                                            
    const handleSave = async () => {                                                                                        
      if (!id) return                                                                                                       
      try {                                                                                                                 
        const updated = await updateMonitor(id, {                                                                           
          name: editName,                                                                                                   
          url: editUrl,                                                                                                     
          interval_seconds: editInterval,                                                                                   
        })                                                                                                                  
        setMonitor(updated)                                                                                                 
        setEditing(false)                                                                                                   
      } catch (err) {                                                                                                       
        setError(err instanceof Error ? err.message : 'Failed to update')                                                   
      }                                                                                                                     
    }                                                                                                                       
                                                                                                                            
    const handleDelete = async () => {                                                                                      
      if (!id) return                                                                                                       
      if (!confirm('Are you sure you want to delete this monitor?')) return                                                 
                                                                                                                            
      try {                                                                                                                 
        await deleteMonitor(id)                                                                                             
        navigate('/')                                                                                                       
      } catch (err) {                                                                                                       
        setError(err instanceof Error ? err.message : 'Failed to delete')                                                   
      }                                                                                                                     
    }                                                                                                                       
                                                                                                                            
    const handleToggleActive = async () => {                                                                                
      if (!id || !monitor) return                                                                                           
      try {                                                                                                                 
        const updated = await updateMonitor(id, { is_active: !monitor.is_active })                                          
        setMonitor(updated)                                                                                                 
      } catch (err) {                                                                                                       
        setError(err instanceof Error ? err.message : 'Failed to update')                                                   
      }                                                                                                                     
    }                                                                                                                       
                                                                                                                            
    if (loading) return <p>Loading...</p>                                                                                   
    if (error) return <p>Error: {error}</p>                                                                                 
    if (!monitor) return <p>Monitor not found</p>                                                                           
                                                                                                                            
    return (                                                                                                                
      <div>                                                                                                                 
        <Link to="/">← Back to Dashboard</Link>                                                                             
                                                                                                                            
        {editing ? (                                                                                                        
          <div>                                                                                                             
            <h1>Edit Monitor</h1>                                                                                           
            <div>                                                                                                           
              <label>Name:</label><br />                                                                                    
              <input value={editName} onChange={(e) => setEditName(e.target.value)} />                                      
            </div>                                                                                                          
            <div style={{ marginTop: '0.5rem' }}>                                                                           
              <label>URL:</label><br />                                                                                     
              <input value={editUrl} onChange={(e) => setEditUrl(e.target.value)} />                                        
            </div>                                                                                                          
            <div style={{ marginTop: '0.5rem' }}>                                                                           
              <label>Interval (seconds):</label><br />                                                                      
              <input                                                                                                        
                type="number"                                                                                               
                value={editInterval}                                                                                        
                onChange={(e) => setEditInterval(Number(e.target.value))}                                                   
              />                                                                                                            
            </div>                                                                                                          
            <div style={{ marginTop: '1rem' }}>                                                                             
              <button onClick={handleSave}>Save</button>{' '}                                                               
              <button onClick={() => setEditing(false)}>Cancel</button>                                                     
            </div>                                                                                                          
          </div>                                                                                                            
        ) : (                                                                                                               
          <div>                                                                                                             
            <h1>{monitor.name}</h1>                                                                                         
            <p>URL: {monitor.url}</p>                                                                                       
            <p>Status: {monitor.is_active ? 'Active' : 'Paused'}</p>                                                        
            <p>Check interval: {monitor.interval_seconds} seconds</p>                                                       
                                                                                                                            
            <div style={{ marginTop: '1rem' }}>                                                                             
              <button onClick={() => setEditing(true)}>Edit</button>{' '}                                                   
              <button onClick={handleToggleActive}>                                                                         
                {monitor.is_active ? 'Pause' : 'Resume'}                                                                    
              </button>{' '}                                                                                                
              <button onClick={handleDelete} style={{ color: 'red' }}>Delete</button>                                       
            </div>                                                                                                          
          </div>                                                                                                            
        )}                                                                                                                  
                                                                                                                            
        <h2 style={{ marginTop: '2rem' }}>Recent Checks</h2>                                                                
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