import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Login() {
  const navigate = useNavigate()
  const { login, register } = useAuth()
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      if (isRegister) {
        await register(username, password)
      } else {
        await login(username, password)
      }
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setSubmitting(false)
    }
  }

  return (
    <div>
      <Link to="/">← Back to Dashboard</Link>
      <h1>{isRegister ? 'Create Account' : 'Log In'}</h1>

      {error && <p style={{ color: '#f87171' }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Username:</label><br />
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div style={{ marginTop: '1rem' }}>
          <label htmlFor="password">Password:</label><br />
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            required
          />
        </div>

        <button type="submit" disabled={submitting} style={{ marginTop: '1rem' }}>
          {submitting
            ? (isRegister ? 'Creating...' : 'Logging in...')
            : (isRegister ? 'Create Account' : 'Log In')}
        </button>
      </form>

      <p style={{ marginTop: '1.5rem' }}>
        {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault()
            setIsRegister(!isRegister)
            setError(null)
          }}
        >
          {isRegister ? 'Log in' : 'Create one'}
        </a>
      </p>
    </div>
  )
}

export default Login
