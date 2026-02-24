import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, MessageSquare, Package, DollarSign, 
  Calendar as CalendarIcon, Building2, TrendingUp, Wallet, 
  FileText, Settings, Clock, Users, BarChart3
} from 'lucide-react'

const Sidebar = () => {
  const links = [
    { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/app/chat', icon: MessageSquare, label: 'AI Assistant' },
    { to: '/app/materials', icon: Package, label: 'Material Estimator' },
    { to: '/app/cost', icon: DollarSign, label: 'Cost Planner' },
    { to: '/app/scheduling', icon: Clock, label: 'Scheduling' },
    { to: '/app/architecture', icon: Building2, label: 'Architecture' },
    { to: '/app/progress', icon: TrendingUp, label: 'Progress Tracker' },
    { to: '/app/finance', icon: Wallet, label: 'Finance' },
    { to: '/app/reports', icon: FileText, label: 'Reports' },
    { to: '/app/team', icon: Users, label: 'Team' },
    { to: '/app/calendar', icon: CalendarIcon, label: 'Calendar' },
    { to: '/app/documents', icon: FileText, label: 'Documents' },
    { to: '/app/material-prices', icon: BarChart3, label: 'Live Material Rates' },
    { to: '/app/settings', icon: Settings, label: 'Settings' }
  ]

  return (
    <aside className="w-64 bg-gradient-to-b from-blue-900 to-blue-800 text-white flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold">BuildWise</h1>
        <p className="text-blue-200 text-sm">AI Construction Platform</p>
      </div>
      
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-700 text-white'
                  : 'text-blue-100 hover:bg-blue-800'
              }`
            }
          >
            <link.icon size={20} />
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
