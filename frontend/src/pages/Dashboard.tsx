import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Monitor } from '../api/monitors'
import { getMonitors } from '../api/monitors'

function Dashboard() {
  const [monitors, setMonitors] = useState<Monitor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getMonitors()
      .then((data) => {
        setMonitors(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      <h1>Dashboard</h1>
      {monitors.length === 0 ? (
        <p>No monitors yet.</p>
      ) : (
        <ul>
          {monitors.map((monitor) => (
            <li key={monitor.id}>
              <Link to={`/monitors/${monitor.id}`}>
                {monitor.name}
              </Link>
              {' - '}
              {monitor.is_active ? 'Active' : 'Paused'}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Dashboard
