import { useParams } from 'react-router-dom'                                                                              
                                                                                                                            
function MonitorDetail() {                                                                                                
  const { id } = useParams()                                                                                              
                                                                                                                          
  return (                                                                                                                
    <div>                                                                                                                 
      <h1>Monitor Detail</h1>                                                                                             
      <p>Viewing monitor #{id}</p>                                                                                        
    </div>                                                                                                                
  )                                                                                                                       
}                                                                                                                         
                                                                                                                          
export default MonitorDetail