import { BrowserRouter, Routes, Route } from 'react-router-dom'                                                           
import Dashboard from './pages/Dashboard'                                                                                 
import MonitorDetail from './pages/MonitorDetail'                                                                         
import AddMonitor from './pages/AddMonitor'                                                                               
import './App.css'                                                                                                        
                                                                                                                          
function App() {                                                                                                          
  return (                                                                                                                
    <BrowserRouter>                                                                                                       
      <Routes>                                                                                                            
        <Route path="/" element={<Dashboard />} />                                                                        
        <Route path="/monitors/new" element={<AddMonitor />} />                                                           
        <Route path="/monitors/:id" element={<MonitorDetail />} />                                                        
      </Routes>                                                                                                           
    </BrowserRouter>                                                                                                      
  )                                                                                                                       
}                                                                                                                         
                                                                                                                          
export default App                                                                                                        
                                                                                                                          