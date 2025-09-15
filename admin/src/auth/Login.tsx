import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (!(username && password)) throw new Error('Enter username and password')

      // Try backend login (works for seeded users: admin/admin123#, test/test123#)
      try {
        const res = await api.post('/auth/login', { userId: username, password })
        if (res?.data?.access_token) {
          localStorage.setItem('access_token', res.data.access_token)
        }
      } catch (err: any) {
        // Allow seed admin bypass to enter portal even if backend unavailable
        if (!(username === 'admin' && password === 'admin123#')) {
          throw new Error(err?.response?.data?.detail || 'Invalid credentials')
        }
      }

      localStorage.setItem('admin_authed', 'true')
      navigate('/', { replace: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-sm bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-primary text-center mb-6">Admin Login</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Username</label>
            <input
              className="w-full border rounded px-3 py-2 outline-primary"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              className="w-full border rounded px-3 py-2 outline-primary"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="admin123#"
            />
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white py-2 rounded hover:opacity-95 disabled:opacity-60"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
          <p className="text-xs text-gray-500 mt-2">Seed users: admin/admin123# • test/test123#</p>
        </form>
      </div>
    </div>
  )
}


