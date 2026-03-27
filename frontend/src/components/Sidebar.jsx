import { NavLink } from 'react-router-dom'
import { FiShield } from 'react-icons/fi'

export default function Sidebar({ links }) {
  return (
    <aside className="w-64 min-h-screen bg-primary text-white flex flex-col">
      <div className="flex items-center gap-2 px-6 py-5 border-b border-primary-600">
        <FiShield className="text-accent text-2xl" />
        <span className="font-bold text-lg">TrustArchive<span className="text-accent">.bi</span></span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-accent text-white font-medium' : 'hover:bg-primary-600'
              }`
            }
          >
            <Icon className="text-lg" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
