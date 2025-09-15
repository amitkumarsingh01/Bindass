import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/users', label: 'Users' },
  { to: '/contests', label: 'Contests' },
  { to: '/withdrawals', label: 'Withdrawals' },
  { to: '/sliders', label: 'Home Sliders' },
]

export default function DashboardLayout() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('admin_authed')
    localStorage.removeItem('admin_userId')
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <aside className="bg-white border-r p-4">
        <Link to="/" className="block text-xl font-bold text-primary mb-6">Bindass Admin</Link>
        <nav className="space-y-2">
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === '/'}
              className={({ isActive }) => `block px-3 py-2 rounded ${isActive ? 'bg-primary text-white' : 'hover:bg-gray-100'}`}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-6 space-y-2">
          <NavLink to="/contests/create" className="block px-3 py-2 rounded hover:bg-gray-100">Create Contest</NavLink>
        </div>
        <button onClick={logout} className="mt-8 w-full bg-gray-100 hover:bg-gray-200 rounded py-2">Logout</button>
      </aside>
      <main className="bg-gray-50 p-6">
        <TopBar />
        <Outlet />
      </main>
    </div>
  )
}

function TopBar() {
  const [val, setVal] = React.useState(localStorage.getItem('admin_userId') || 'admin')
  const apply = () => {
    localStorage.setItem('admin_userId', val || 'admin')
    window.location.reload()
  }
  return (
    <div className="flex items-center justify-between mb-4">
      <div />
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Impersonate userId</span>
        <input className="border rounded px-2 py-1" value={val} onChange={e=>setVal(e.target.value)} placeholder="userId" />
        <button onClick={apply} className="px-2 py-1 bg-primary text-white rounded">Apply</button>
      </div>
    </div>
  )
}


