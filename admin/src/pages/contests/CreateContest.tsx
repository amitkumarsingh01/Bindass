import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../../lib/api'

export default function CreateContest() {
  const nav = useNavigate()
  const [form, setForm] = useState({
    contestName: '',
    totalPrizeMoney: '',
    ticketPrice: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/admin/contests', {
        contestName: form.contestName,
        totalPrizeMoney: Number(form.totalPrizeMoney),
        ticketPrice: Number(form.ticketPrice),
      })
      nav('/contests', { replace: true })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create contest')
    } finally {
      setLoading(false)
    }
  }

  const set = (k: string, v: string) => setForm((p) => ({ ...p, [k]: v }))

  const calculateRevenue = () => {
    const ticketPrice = Number(form.ticketPrice) || 0
    const totalSeats = 10000 // Fixed total seats
    return ticketPrice * totalSeats
  }

  const calculateProfit = () => {
    const revenue = calculateRevenue()
    const prizeMoney = Number(form.totalPrizeMoney) || 0
    return revenue - prizeMoney
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          to="/contests" 
          className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-all duration-200"
        >
          <span className="text-xl">←</span>
        </Link>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Create New Contest
          </h1>
          <p className="text-gray-600 mt-1">Set up a new lottery contest with prizes and categories</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
                <span className="text-3xl">🎯</span>
                Contest Details
              </h2>
              <p className="text-gray-600">Fill in the basic information for your new lottery contest</p>
            </div>
            
            <form onSubmit={submit} className="space-y-8">
              <div className="space-y-8">
                <Field 
                  label="Contest Name" 
                  description="Give your contest a memorable and attractive name"
                  required
                >
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🎪</span>
                    <input 
                      className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                      placeholder="e.g., Mega Lottery 2024, Golden Jackpot Contest"
                      value={form.contestName} 
                      onChange={(e) => set('contestName', e.target.value)} 
                      required
                    />
                  </div>
                </Field>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <Field 
                    label="Total Prize Money (₹)" 
                    description="Total amount to be distributed as prizes"
                    required
                  >
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl">💰</span>
                      <input 
                        className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                        type="number" 
                        placeholder="1000000"
                        value={form.totalPrizeMoney} 
                        onChange={(e) => set('totalPrizeMoney', e.target.value)} 
                        required
                        min="1000"
                      />
                    </div>
                  </Field>

                  <Field 
                    label="Ticket Price (₹)" 
                    description="Price per seat/ticket"
                    required
                  >
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-xl">🎫</span>
                      <input 
                        className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                        type="number" 
                        placeholder="100"
                        value={form.ticketPrice} 
                        onChange={(e) => set('ticketPrice', e.target.value)} 
                        required
                        min="1"
                      />
                    </div>
                  </Field>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="flex items-center gap-2">
                    <span className="text-red-500 text-xl">⚠️</span>
                    <p className="text-red-700 font-medium">{error}</p>
                  </div>
                </div>
              )}

              <div className="flex gap-4 pt-6">
                <button 
                  type="button"
                  onClick={() => nav('/contests')}
                  className="flex-1 px-6 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={loading || !form.contestName || !form.totalPrizeMoney || !form.ticketPrice}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Creating Contest...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-xl">🎯</span>
                      Create Contest
                    </div>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Preview & Info */}
        <div className="space-y-6">
          {/* Contest Preview */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">👁️</span>
              Live Preview
            </h3>
            <div className="space-y-6">
              <div className="relative overflow-hidden rounded-2xl">
                <div className="bg-gradient-to-r from-primary to-yellow-500 p-6 text-white">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">🎯</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-xl">{form.contestName || 'Contest Name'}</h4>
                      <p className="text-sm opacity-75">Lottery Contest</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/20 rounded-lg p-3">
                      <p className="text-sm opacity-75">Ticket Price</p>
                      <p className="text-2xl font-bold">₹{form.ticketPrice || '0'}</p>
                    </div>
                    <div className="bg-white/20 rounded-lg p-3">
                      <p className="text-sm opacity-75">Total Prize</p>
                      <p className="text-2xl font-bold">₹{Number(form.totalPrizeMoney || 0).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600 flex items-center gap-2">
                    <span className="text-lg">🎫</span>
                    Total Seats
                  </span>
                  <span className="font-bold text-gray-800">10,000</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600 flex items-center gap-2">
                    <span className="text-lg">📋</span>
                    Categories
                  </span>
                  <span className="font-bold text-gray-800">10 (Auto-created)</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600 flex items-center gap-2">
                    <span className="text-lg">⏰</span>
                    Duration
                  </span>
                  <span className="font-bold text-gray-800">7 days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Financial Summary */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">💰</span>
              Financial Analysis
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-blue-700 font-medium">Potential Revenue</span>
                  <span className="text-2xl font-bold text-blue-800">₹{calculateRevenue().toLocaleString()}</span>
                </div>
                <p className="text-xs text-blue-600">10,000 seats × ₹{form.ticketPrice || '0'}</p>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-green-700 font-medium">Prize Money</span>
                  <span className="text-2xl font-bold text-green-800">₹{Number(form.totalPrizeMoney || 0).toLocaleString()}</span>
                </div>
                <p className="text-xs text-green-600">Total prize distribution</p>
              </div>
              
              <div className={`p-4 rounded-xl border ${
                calculateProfit() >= 0 
                  ? 'bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200' 
                  : 'bg-gradient-to-r from-red-50 to-red-100 border-red-200'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className={`font-medium ${calculateProfit() >= 0 ? 'text-purple-700' : 'text-red-700'}`}>
                    Net Profit
                  </span>
                  <span className={`text-2xl font-bold ${calculateProfit() >= 0 ? 'text-purple-800' : 'text-red-800'}`}>
                    ₹{calculateProfit().toLocaleString()}
                  </span>
                </div>
                <p className={`text-xs ${calculateProfit() >= 0 ? 'text-purple-600' : 'text-red-600'}`}>
                  {calculateProfit() >= 0 ? 'Revenue - Prize Money' : 'Loss: Prize exceeds revenue'}
                </p>
              </div>
            </div>
          </div>

          {/* Auto-Generated Features */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">⚙️</span>
              Auto-Generated Features
            </h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <span className="font-medium text-green-800">10 Categories</span>
                  <p className="text-xs text-green-600">Bike, Auto, Car, etc.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <span className="font-medium text-green-800">10,000 Total Seats</span>
                  <p className="text-xs text-green-600">1,000 seats per category</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <span className="font-medium text-green-800">7-day Contest Duration</span>
                  <p className="text-xs text-green-600">Automatic start/end dates</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <span className="font-medium text-green-800">Active Status</span>
                  <p className="text-xs text-green-600">Ready for participants</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Field({ label, description, children, required }: { 
  label: string
  description?: string
  children: React.ReactNode
  required?: boolean
}) {
  return (
    <label className="block">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg font-semibold text-gray-800">{label}</span>
        {required && (
          <span className="px-2 py-1 bg-red-100 text-red-600 rounded-full text-xs font-medium">
            Required
          </span>
        )}
      </div>
      {description && (
        <p className="text-sm text-gray-600 mb-4 leading-relaxed">{description}</p>
      )}
      {children}
    </label>
  )
}


