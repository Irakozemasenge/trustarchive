import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import StatusBadge from '../../components/StatusBadge'
import QRDownload from '../../components/QRDownload'
import { FiHome, FiFileText, FiInbox, FiPlusCircle, FiGrid } from 'react-icons/fi'

const links = [
  { to: '/admin', icon: FiHome, label: 'Tableau de bord' },
  { to: '/admin/documents', icon: FiFileText, label: 'Documents' },
  { to: '/admin/documents/add', icon: FiPlusCircle, label: 'Ajouter document' },
  { to: '/admin/qrcodes', icon: FiGrid, label: 'QR Codes' },
  { to: '/admin/requests', icon: FiInbox, label: 'Demandes' },
]

export default function AdminDocuments() {
  const { data: docs, isLoading } = useQuery({
    queryKey: ['myDocs'],
    queryFn: () => api.get('/documents/').then(r => r.data)
  })
  const list = docs?.results ?? docs ?? []

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Mes Documents</h1>
          <Link to="/admin/documents/add" className="btn-primary flex items-center gap-2">
            <FiPlusCircle /> Ajouter un document
          </Link>
        </div>

        <div className="card overflow-x-auto">
          {isLoading ? (
            <p className="text-gray-400 py-4">Chargement...</p>
          ) : list.length === 0 ? (
            <div className="py-10 text-center text-gray-400">
              <FiFileText className="text-4xl mx-auto mb-2 opacity-30" />
              <p>Aucun document enregistre.</p>
              <Link to="/admin/documents/add" className="text-primary hover:underline text-sm mt-2 inline-block">
                Enregistrer votre premier document
              </Link>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4 font-medium">Numero unique</th>
                  <th className="pb-3 pr-4 font-medium">Titre</th>
                  <th className="pb-3 pr-4 font-medium">Delivre a</th>
                  <th className="pb-3 pr-4 font-medium">Date</th>
                  <th className="pb-3 pr-4 font-medium">Statut</th>
                  <th className="pb-3 font-medium">QR Code</th>
                </tr>
              </thead>
              <tbody>
                {list.map(doc => (
                  <tr key={doc.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 pr-4 font-mono text-xs text-primary font-bold">{doc.unique_number}</td>
                    <td className="py-3 pr-4">{doc.title}</td>
                    <td className="py-3 pr-4">{doc.issued_to}</td>
                    <td className="py-3 pr-4">{doc.issued_date}</td>
                    <td className="py-3 pr-4"><StatusBadge status={doc.status} /></td>
                    <td className="py-3">
                      <QRDownload
                        url={doc.qr_code_url}
                        filename={`QR_${doc.unique_number}.png`}
                        size="sm"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}
