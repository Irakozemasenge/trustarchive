import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FiShield, FiLogOut, FiUser } from 'react-icons/fi'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/') }
  const dashboardLink = user?.role === 'superadmin' ? '/superadmin' : '/admin'

  return (
    <nav className="bg-primary text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl">
          <FiShield className="text-accent text-2xl" />
          TrustArchive<span className="text-accent">.bi</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/verify" className="hover:text-accent transition-colors text-sm">Vérifier</Link>
          {!user ? (
            <>
              <Link to="/login" className="hover:text-accent text-sm">Connexion</Link>
              <Link to="/register" className="bg-accent text-white px-3 py-1.5 rounded-lg text-sm hover:bg-accent-dark">S'inscrire</Link>
            </>
          ) : (
            <>
              <Link to={dashboardLink} className="flex items-center gap-1 hover:text-accent text-sm">
                <FiUser /> {user.full_name}
              </Link>
              <button onClick={handleLogout} className="flex items-center gap-1 hover:text-red-300 text-sm">
                <FiLogOut /> Déconnexion
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
