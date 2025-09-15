import axios from 'axios'

export const api = axios.create({
  baseURL: 'https://server.bindassgrand.com/api',
})

// Simple admin header injection if you later add real auth
api.interceptors.request.use((config) => {
  config.headers = config.headers || {}
  // Admin key to satisfy admin guard
  config.headers['X-Admin-Key'] = 'bindass-admin'
  // Optional bearer token if present
  const token = localStorage.getItem('access_token')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

export type AdminDashboard = {
  users: { total: number; active: number }
  contests: { total: number; active: number }
  transactions: { total: number }
  withdrawals: { pending: number }
  prizeMoney: { totalDistributed: number }
}


