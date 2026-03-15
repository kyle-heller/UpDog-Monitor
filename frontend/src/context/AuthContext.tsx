import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import {
  login as apiLogin,
  register as apiRegister,
  getToken,
  setToken,
  clearToken,
  parseUsername,
} from '../api/auth'

interface AuthContextType {
  user: string | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null)
  const [token, setTokenState] = useState<string | null>(null)

  useEffect(() => {
    const stored = getToken()
    if (stored) {
      const username = parseUsername(stored)
      if (username) {
        setTokenState(stored)
        setUser(username)
      } else {
        clearToken()
      }
    }
  }, [])

  const login = async (username: string, password: string) => {
    const res = await apiLogin(username, password)
    setToken(res.access_token)
    setTokenState(res.access_token)
    setUser(parseUsername(res.access_token))
  }

  const register = async (username: string, password: string) => {
    const res = await apiRegister(username, password)
    setToken(res.access_token)
    setTokenState(res.access_token)
    setUser(parseUsername(res.access_token))
  }

  const logout = () => {
    clearToken()
    setTokenState(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
