import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import MonitorDetail from './pages/MonitorDetail'
import AddMonitor from './pages/AddMonitor'
import Login from './pages/Login'
import { useAuth } from './context/AuthContext'

function Nav() {
  const { user, logout } = useAuth()

  return (
    <nav className="nav">
      <Link to="/" className="nav-brand">UpDog Monitor</Link>
      <div className="nav-auth">
        {user ? (
          <>
            <span>{user}</span>
            <button onClick={logout}>Log out</button>
          </>
        ) : (
          <Link to="/login">Log in</Link>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/monitors/new" element={<AddMonitor />} />
        <Route path="/monitors/:id" element={<MonitorDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App                                                                                                        
                                                                                                                          