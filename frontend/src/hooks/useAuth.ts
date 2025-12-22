import { useState, useEffect } from 'react'
import api from '../services/api'

interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
      setIsAuthenticated(true)
    } catch (error) {
      localStorage.removeItem('access_token')
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password })
    localStorage.setItem('access_token', response.data.access_token)
    await fetchUser()
    // Ensure state is updated - fetchUser sets isAuthenticated to true
    // Return a small delay to ensure React has processed the state update
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        resolve()
      }, 50)
    })
  }

  const register = async (email: string, password: string, firstName?: string, lastName?: string) => {
    await api.post('/api/auth/register', { email, password, first_name: firstName, last_name: lastName })
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    setIsAuthenticated(false)
  }

  return {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
  }
}

