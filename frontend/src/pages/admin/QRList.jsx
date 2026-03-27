import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import { downloadQR } from '../../components/QRDownload'
import { FiHome, FiFileText, FiInbox, FiPlusCircle, FiGrid, FiDownload, FiPrinter, FiCheckSquare, FiSquare } from 'react-icons/fi'
import StatusBadge from '../../components/StatusBadge'

const links = [
  { to: '/admin', icon: FiHome, label: 'Tableau de bord' },
  { to: '/admin/documents', icon: FiFileText, label: 'Documents' },
  { to: '/admin/documents/add', icon: FiPlusCircle, label: 'Ajouter document' },
  { to: '/admin/qrcodes', icon: FiGrid, label: 'QR Codes' },
  { to: '/admin/requests', icon: FiInbox, label: 'Demandes' },
]

export default function AdminQRList() {
  const [selected, setSelected] = useState(new Set())
  const [view, setView] = useState('grid') // grid | table

  const { data: docs, isLoading } = useQuery({
    queryKey: ['myDocsQR'],
    queryFn: () => api.get('/documents/?page_size=100').then(r => r.data)
  })
  const list = (docs?.results ?? docs ?? []).filter(d => d.qr_code_url)

  const toggleSelect = (id) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const toggleAll = () => {
    if (selected.size === list.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(list.map(d => d.id)))
    }
  }

  const selectedDocs = list.filter(d => selected.has(d.id))

  const downloadSelected = () => {
    selectedDocs.forEach((doc, i) => {
      setTimeout(() => {
        downloadQR(doc.qr_code_url, `QR_${doc.unique_number}.png`)
      }, i * 300)
    })
  }

  const printSelected = () => {
    const docs = selected.size > 0 ? selectedDocs : list
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>QR Codes - TrustArchive.bi</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #1e3a5f; padding-bottom: 15px; }
          .header h1 { color: #1e3a5f; margin: 0; font-size: 22px; }
          .header p { color: #666; margin: 5px 0 0; font-size: 12px; }
          .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
          .card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; page-break-inside: avoid; }
          .card img { width: 120px; height: 120px; }
          .card .num { font-family: monospace; font-size: 11px; color: #1e3a5f; font-weight: bold; margin: 8px 0 4px; }
          .card .title { font-size: 12px; color: #333; margin: 0 0 3px; }
          .card .person { font-size: 11px; color: #666; margin: 0; }
          .footer { text-align: center; margin-top: 30px; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
          @media print { .no-print { display: none; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>TrustArchive.bi — QR Codes</h1>
          <p>Genere le ${new Date().toLocaleDateString('fr-FR')} — ${docs.length} document(s)</p>
        </div>
        <div class="grid">
          ${docs.map(doc => `
            <div class="card">
              <img src="${doc.qr_code_url}" alt="QR ${doc.unique_number}" />
              <p class="num">${doc.unique_number}</p>
              <p class="title">${doc.title}</p>
              <p class="person">${doc.issued_to}</p>
            </div>
          `).join('')}
        </div>
        <div class="footer">
          Plateforme TrustArchive.bi — Formation des formateurs BuruDigi — Verifiez sur trustarchive.bi/verify
        </div>
      </body>
      </html>
    `
    const win = window.open('', '_blank')
    win.document.write(html)
    win.document.close()
    win.focus()
    setTimeout(() => win.print(), 500)
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">QR Codes</h1>
            <p className="text-gray-500 text-sm">{list.length} QR code(s) disponible(s)</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setView(v => v === 'grid' ? 'table' : 'grid')}
              className="btn-secondary flex items-center gap-2 text-sm"
            >
              <FiGrid /> {view === 'grid' ? 'Vue tableau' : 'Vue grille'}
            </button>
            {selected.size > 0 && (
              <button onClick={downloadSelected} className="btn-secondary flex items-center gap-2 text-sm">
                <FiDownload /> Telecharger ({selected.size})
              </button>
            )}
            <button onClick={printSelected} className="btn-primary flex items-center gap-2 text-sm">
              <FiPrinter /> {selected.size > 0 ? `Imprimer (${selected.size})` : 'Imprimer tout'}
            </button>
          </div>
        </div>

        {/* Barre de sélection */}
        {list.length > 0 && (
          <div className="flex items-center gap-3 mb-4 bg-white rounded-lg px-4 py-2.5 border text-sm">
            <button onClick={toggleAll} className="flex items-center gap-2 text-gray-600 hover:text-primary">
              {selected.size === list.length
                ? <FiCheckSquare className="text-primary text-lg" />
                : <FiSquare className="text-gray-400 text-lg" />}
              {selected.size === list.length ? 'Tout deselectionner' : 'Tout selectionner'}
            </button>
            {selected.size > 0 && (
              <span className="text-primary font-medium">{selected.size} selectionne(s)</span>
            )}
          </div>
        )}

        {isLoading ? (
          <div className="card py-10 text-center text-gray-400">Chargement...</div>
        ) : list.length === 0 ? (
          <div className="card py-10 text-center text-gray-400">
            <FiGrid className="text-4xl mx-auto mb-2 opacity-30" />
            <p>Aucun QR code disponible. Enregistrez des documents d abord.</p>
          </div>
        ) : view === 'grid' ? (
          /* Vue grille */
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {list.map(doc => (
              <div
                key={doc.id}
                onClick={() => toggleSelect(doc.id)}
                className={`card cursor-pointer transition-all text-center p-4 ${
                  selected.has(doc.id)
                    ? 'ring-2 ring-primary bg-primary/5'
                    : 'hover:shadow-md'
                }`}
              >
                <div className="relative mb-3">
                  <img
                    src={doc.qr_code_url}
                    alt={`QR ${doc.unique_number}`}
                    className="w-28 h-28 mx-auto rounded"
                  />
                  {selected.has(doc.id) && (
                    <div className="absolute top-0 right-0 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                      <FiCheckSquare className="text-white text-xs" />
                    </div>
                  )}
                </div>
                <p className="font-mono text-xs text-primary font-bold truncate">{doc.unique_number}</p>
                <p className="text-xs text-gray-600 truncate mt-0.5">{doc.title}</p>
                <p className="text-xs text-gray-400 truncate">{doc.issued_to}</p>
                <div className="mt-2 flex items-center justify-center gap-2">
                  <StatusBadge status={doc.status} />
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); downloadQR(doc.qr_code_url, `QR_${doc.unique_number}.png`) }}
                  className="mt-2 w-full flex items-center justify-center gap-1 text-xs text-primary hover:bg-primary/10 py-1 rounded transition-colors"
                >
                  <FiDownload /> Telecharger
                </button>
              </div>
            ))}
          </div>
        ) : (
          /* Vue tableau */
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-3 w-8">
                    <button onClick={toggleAll}>
                      {selected.size === list.length
                        ? <FiCheckSquare className="text-primary text-lg" />
                        : <FiSquare className="text-gray-400 text-lg" />}
                    </button>
                  </th>
                  <th className="pb-3 pr-4 font-medium">QR Code</th>
                  <th className="pb-3 pr-4 font-medium">Numero unique</th>
                  <th className="pb-3 pr-4 font-medium">Titre</th>
                  <th className="pb-3 pr-4 font-medium">Delivre a</th>
                  <th className="pb-3 pr-4 font-medium">Date</th>
                  <th className="pb-3 pr-4 font-medium">Statut</th>
                  <th className="pb-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {list.map(doc => (
                  <tr
                    key={doc.id}
                    className={`border-b cursor-pointer ${selected.has(doc.id) ? 'bg-primary/5' : 'hover:bg-gray-50'}`}
                    onClick={() => toggleSelect(doc.id)}
                  >
                    <td className="py-3 pr-3">
                      {selected.has(doc.id)
                        ? <FiCheckSquare className="text-primary text-lg" />
                        : <FiSquare className="text-gray-300 text-lg" />}
                    </td>
                    <td className="py-3 pr-4">
                      <img src={doc.qr_code_url} alt="QR" className="w-12 h-12 rounded border" />
                    </td>
                    <td className="py-3 pr-4 font-mono text-xs text-primary font-bold">{doc.unique_number}</td>
                    <td className="py-3 pr-4">{doc.title}</td>
                    <td className="py-3 pr-4">{doc.issued_to}</td>
                    <td className="py-3 pr-4 text-gray-500">{doc.issued_date}</td>
                    <td className="py-3 pr-4"><StatusBadge status={doc.status} /></td>
                    <td className="py-3">
                      <button
                        onClick={(e) => { e.stopPropagation(); downloadQR(doc.qr_code_url, `QR_${doc.unique_number}.png`) }}
                        className="flex items-center gap-1 text-primary hover:bg-primary/10 px-2 py-1 rounded text-xs"
                      >
                        <FiDownload /> Telecharger
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
