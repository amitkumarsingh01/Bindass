import axios from 'axios'

export const api = axios.create({
  baseURL: 'https://server.bindassgrand.com/api',
})

// Admin authentication removed - no headers needed
api.interceptors.request.use((config) => {
  config.headers = config.headers || {}
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


