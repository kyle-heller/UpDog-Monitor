import { useState } from 'react'                                                                                          
import { useNavigate, Link } from 'react-router-dom'                                                                      
import { createMonitor } from '../api/monitors'                                                                           
                                                                                                                          
function AddMonitor() {                                                                                                   
  const navigate = useNavigate()                                                                                          
  const [name, setName] = useState('')                                                                                    
  const [url, setUrl] = useState('')                                                                                      
  const [intervalSeconds, setIntervalSeconds] = useState(60)                                                              
  const [error, setError] = useState<string | null>(null)                                                                 
  const [submitting, setSubmitting] = useState(false)                                                                     
                                                                                                                          
  const handleSubmit = async (e: React.FormEvent) => {                                                                    
    e.preventDefault()                                                                                                    
    setError(null)                                                                                                        
    setSubmitting(true)                                                                                                   
                                                                                                                          
    try {                                                                                                                 
      await createMonitor({ name, url, interval_seconds: intervalSeconds })                                               
      navigate('/')  // Go back to dashboard                                                                              
    } catch (err) {                                                                                                       
      setError(err instanceof Error ? err.message : 'Something went wrong')                                               
      setSubmitting(false)                                                                                                
    }                                                                                                                     
  }                                                                                                                       
                                                                                                                          
  return (                                                                                                                
    <div>                                                                                                                 
      <Link to="/">← Back to Dashboard</Link>                                                                             
      <h1>Add Monitor</h1>                                                                                                
                                                                                                                          
      {error && <p style={{ color: 'red' }}>{error}</p>}                                                                  
                                                                                                                          
      <form onSubmit={handleSubmit}>                                                                                      
        <div>                                                                                                             
          <label htmlFor="name">Name:</label><br />                                                                       
          <input                                                                                                          
            id="name"                                                                                                     
            type="text"                                                                                                   
            value={name}                                                                                                  
            onChange={(e) => setName(e.target.value)}                                                                     
            required                                                                                                      
          />                                                                                                              
        </div>                                                                                                            
                                                                                                                          
        <div style={{ marginTop: '1rem' }}>                                                                               
          <label htmlFor="url">URL:</label><br />                                                                         
          <input                                                                                                          
            id="url"                                                                                                      
            type="url"                                                                                                    
            value={url}                                                                                                   
            onChange={(e) => setUrl(e.target.value)}                                                                      
            placeholder="https://example.com"                                                                             
            required                                                                                                      
          />                                                                                                              
        </div>                                                                                                            
                                                                                                                          
        <div style={{ marginTop: '1rem' }}>                                                                               
          <label htmlFor="interval">Check interval (seconds):</label><br />                                               
          <input                                                                                                          
            id="interval"                                                                                                 
            type="number"                                                                                                 
            value={intervalSeconds}                                                                                       
            onChange={(e) => setIntervalSeconds(Number(e.target.value))}                                                  
            min={10}                                                                                                      
          />                                                                                                              
        </div>                                                                                                            
                                                                                                                          
        <button type="submit" disabled={submitting} style={{ marginTop: '1rem' }}>                                        
          {submitting ? 'Creating...' : 'Create Monitor'}                                                                 
        </button>                                                                                                         
      </form>                                                                                                             
    </div>                                                                                                                
  )                                                                                                                       
}                                                                                                                         
                                                                                                                          
export default AddMonitor  