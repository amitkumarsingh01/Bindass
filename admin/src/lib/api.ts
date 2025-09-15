import axios from 'axios'

export const api = axios.create({
  baseURL: 'https://server.bindassgrand.com/api',
})

// Simple admin header injection if you later add real auth
api.interceptors.request.use((config) => {
  config.headers = config.headers || {}
  // Admin key to satisfy admin guard (no bearer required)
  config.headers['X-Admin-Key'] = 'bindass-admin'
  // Optionally pass user identity for non-admin endpoints (when needed)
  const userId = localStorage.getItem('admin_userId') || 'admin'
  config.headers['X-User-Id'] = userId
  return config
})

export type AdminDashboard = {
  users: { total: number; active: number }
  contests: { total: number; active: number }
  transactions: { total: number }
  withdrawals: { pending: number }
  prizeMoney: { totalDistributed: number }
}


