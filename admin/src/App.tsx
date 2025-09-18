import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './auth/Login'
import DashboardLayout from './layout/DashboardLayout'
import Dashboard from './pages/Dashboard'
import Users from './pages/users/Users'
import UserDetail from './pages/users/UserDetail'
import Contests from './pages/contests/Contests'
import CreateContest from './pages/contests/CreateContest'
import ContestDetail from './pages/contests/ContestDetail'
import PrizeStructure from './pages/contests/PrizeStructure'
import PrizeSettings from './pages/contests/PrizeSettings'
import Draw from './pages/contests/Draw'
import Withdrawals from './pages/Withdrawals'
import Sliders from './pages/Sliders'
import Contact from './pages/Contact'
import HowToPlay from './pages/HowToPlay'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><DashboardLayout /></RequireAuth>}>
        <Route index element={<Dashboard />} />
        <Route path="users" element={<Users />} />
        <Route path="users/:id" element={<UserDetail />} />
        <Route path="contests" element={<Contests />} />
        <Route path="contests/create" element={<CreateContest />} />
        <Route path="contests/:id" element={<ContestDetail />} />
        <Route path="contests/:id/prize-structure" element={<PrizeStructure />} />
        <Route path="contests/:id/prize-settings" element={<PrizeSettings />} />
        <Route path="contests/:id/draw" element={<Draw />} />
        <Route path="withdrawals" element={<Withdrawals />} />
        <Route path="sliders" element={<Sliders />} />
        <Route path="contact" element={<Contact />} />
        <Route path="how-to-play" element={<HowToPlay />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const authed = localStorage.getItem('admin_authed') === 'true'
  if (!authed) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default App
