import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import StatCard from '../../components/StatCard'
import { FiHome, FiUsers, FiFileText, FiLink, FiTag, FiActivity } from 'react-icons/fi'

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

export default function SuperDashboard() {
  const { data: docStats } = useQuery({ queryKey: ['superDocStats'], queryFn: () => api.get('/documents/stats/').then(r => r.data) })
  const { data: reqStats } = useQuery({ queryKey: ['superReqStats'], queryFn: () => api.get('/requests/stats/').then(r => r.data) })
  const { data: admins } = useQuery({ queryKey: ['admins'], queryFn: () => api.get('/auth/admins/').then(r => r.data) })
  const adminList = admins?.results ?? admins ?? []

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Super Administration</h1>
          <p className="text-gray-500">Vue globale de la plateforme TrustArchive.bi</p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total documents" value={docStats?.total ?? '...'} icon={FiFileText} color="blue" />
          <StatCard label="Verifies" value={docStats?.verified ?? '...'} icon={FiFileText} color="green" />
          <StatCard label="Revoques" value={docStats?.revoked ?? '...'} icon={FiFileText} color="red" />
          <StatCard label="Admins partenaires" value={adminList?.length ?? '...'} icon={FiUsers} color="yellow" />
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          <Link to="/superadmin/admins" className="card hover:shadow-md transition-shadow">
            <FiUsers className="text-primary text-3xl mb-2" />
            <p className="font-semibold">Gerer les admins</p>
            <p className="text-sm text-gray-500">Creer et gerer les partenaires</p>
          </Link>
          <Link to="/superadmin/documents" className="card hover:shadow-md transition-shadow">
            <FiFileText className="text-green-600 text-3xl mb-2" />
            <p className="font-semibold">Tous les documents</p>
            <p className="text-sm text-gray-500">{docStats?.total ?? 0} documents enregistres</p>
          </Link>
          <Link to="/superadmin/blockchain" className="card hover:shadow-md transition-shadow">
            <FiLink className="text-purple-600 text-3xl mb-2" />
            <p className="font-semibold">Integrite Blockchain</p>
            <p className="text-sm text-gray-500">Verifier la chaine de blocs</p>
          </Link>
        </div>
      </main>
    </div>
  )
}

