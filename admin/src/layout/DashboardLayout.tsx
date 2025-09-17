import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'

const nav = [
  { to: '/', label: 'Dashboard', icon: '📊', description: 'Overview & Analytics' },
  { to: '/users', label: 'Users', icon: '👥', description: 'User Management' },
  { to: '/contests', label: 'Contests', icon: '🎯', description: 'Contest Control' },
  { to: '/withdrawals', label: 'Withdrawals', icon: '💰', description: 'Payment Requests' },
  { to: '/sliders', label: 'Home Sliders', icon: '🖼️', description: 'Banner Management' },
]

export default function DashboardLayout() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('admin_authed')
    localStorage.removeItem('admin_userId')
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="grid grid-cols-[280px_1fr] min-h-screen">
        <aside className="bg-white shadow-2xl border-r border-gray-200">
          <div className="p-6">
            <Link to="/" className="flex items-center gap-3 mb-8 group">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-yellow-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300">
                <span className="text-white font-bold text-xl">B</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                  BINDASS Admin
                </h1>
                <p className="text-sm text-gray-500">Lottery Management</p>
              </div>
            </Link>
            
            <nav className="space-y-2">
              {nav.map((n) => (
                <NavLink
                  key={n.to}
                  to={n.to}
                  end={n.to === '/'}
                  className={({ isActive }) => 
                    `group flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 ${
                      isActive 
                        ? 'bg-gradient-to-r from-primary to-yellow-500 text-white shadow-lg transform scale-105' 
                        : 'hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 hover:shadow-md hover:transform hover:scale-102 text-gray-700'
                    }`
                  }
                >
                  <span className="text-2xl group-hover:scale-110 transition-transform duration-200">
                    {n.icon}
                  </span>
                  <div className="flex-1">
                    <div className="font-semibold">{n.label}</div>
                    <div className={`text-xs ${nav.find(nav => nav.to === n.to)?.to === '/' ? 'text-white/80' : 'text-gray-500'}`}>
                      {n.description}
                    </div>
                  </div>
                </NavLink>
              ))}
            </nav>
            
            <div className="mt-8 pt-6 border-t border-gray-200">
              <button 
                onClick={logout} 
                className="w-full flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-red-50 to-red-100 hover:from-red-100 hover:to-red-200 text-red-700 rounded-2xl transition-all duration-200 hover:shadow-md group"
              >
                <span className="text-xl">🚪</span>
                <span className="font-medium">Logout</span>
              </button>
            </div>
          </div>
        </aside>
        
        <main className="overflow-auto">
          <div className="p-8">
            <TopBar />
            <div className="mt-6">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function TopBar() {
  const [val, setVal] = useState(localStorage.getItem('admin_userId') || 'admin')
  const [showImpersonate] = useState(false)
  
  const apply = () => {
    localStorage.setItem('admin_userId', val || 'admin')
    window.location.reload()
  }
  
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Welcome Back! 👋
        </h2>
        <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          System Online
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative">
          
          {showImpersonate && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-gray-200 p-4 z-50">
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Switch to User ID
                  </label>
                  <div className="flex gap-2">
                    <input 
                      className="flex-1 border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                      value={val} 
                      onChange={e => setVal(e.target.value)} 
                      placeholder="Enter user ID (e.g., test, admin)" 
                    />
                    <button 
                      onClick={apply}
                      className="px-4 py-2 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-lg hover:shadow-lg transition-all duration-200 font-medium"
                    >
                      Apply
                    </button>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Currently impersonating: <span className="font-medium text-primary">{val}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="w-10 h-10 bg-gradient-to-br from-primary to-yellow-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
          A
        </div>
      </div>
    </div>
  )
}


