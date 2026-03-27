import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import StatCard from '../../components/StatCard'
import { FiHome, FiFileText, FiInbox, FiPlusCircle, FiGrid } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext'

const links = [
  { to: '/admin', icon: FiHome, label: 'Tableau de bord' },
  { to: '/admin/documents', icon: FiFileText, label: 'Documents' },
  { to: '/admin/documents/add', icon: FiPlusCircle, label: 'Ajouter document' },
  { to: '/admin/qrcodes', icon: FiGrid, label: 'QR Codes' },
  { to: '/admin/requests', icon: FiInbox, label: 'Demandes' },
]

export default function AdminDashboard() {
  const { user } = useAuth()
  const { data: docStats } = useQuery({ queryKey: ['docStats'], queryFn: () => api.get('/documents/stats/').then(r => r.data) })
  const { data: reqStats } = useQuery({ queryKey: ['reqStats'], queryFn: () => api.get('/requests/stats/').then(r => r.data) })

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Tableau de bord</h1>
          <p className="text-gray-500">{user?.organization_name || user?.full_name}</p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total documents" value={docStats?.total ?? '...'} icon={FiFileText} color="blue" />
          <StatCard label="Verifies" value={docStats?.verified ?? '...'} icon={FiFileText} color="green" />
          <StatCard label="En attente" value={docStats?.pending ?? '...'} icon={FiFileText} color="yellow" />
          <StatCard label="Demandes" value={reqStats?.total ?? '...'} icon={FiInbox} color="blue" />
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <Link to="/admin/documents/add" className="card flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <FiPlusCircle className="text-primary text-3xl" />
            <div>
              <p className="font-semibold">Enregistrer un document</p>
              <p className="text-sm text-gray-500">Ajouter et generer un QR code</p>
            </div>
          </Link>
          <Link to="/admin/requests" className="card flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer">
            <FiInbox className="text-accent text-3xl" />
            <div>
              <p className="font-semibold">Traiter les demandes</p>
              <p className="text-sm text-gray-500">{reqStats?.pending ?? 0} demande(s) en attente</p>
            </div>
          </Link>
        </div>
      </main>
    </div>
  )
}

