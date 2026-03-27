import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../../api/axios"
import Sidebar from "../../components/Sidebar"
import toast from "react-hot-toast"
import {
  FiHome, FiUsers, FiFileText, FiLink, FiActivity,
  FiTag, FiPlusCircle, FiTrash2, FiEdit2, FiX, FiCheck
} from "react-icons/fi"

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

const emptyForm = { name: "", description: "" }

export default function SuperCategories() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [editForm, setEditForm] = useState(emptyForm)

  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/documents/categories/").then(r => r.data)
  })

  const createMutation = useMutation({
    mutationFn: (data) => api.post("/documents/categories/", data),
    onSuccess: () => {
      toast.success("Categorie creee avec succes")
      qc.invalidateQueries(["categories"])
      setForm(emptyForm)
      setShowForm(false)
    },
    onError: () => toast.error("Erreur lors de la creation")
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => api.patch(`/documents/categories/${id}/`, data),
    onSuccess: () => {
      toast.success("Categorie mise a jour")
      qc.invalidateQueries(["categories"])
      setEditingId(null)
    },
    onError: () => toast.error("Erreur lors de la modification")
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/documents/categories/${id}/`),
    onSuccess: () => {
      toast.success("Categorie supprimee")
      qc.invalidateQueries(["categories"])
    },
    onError: () => toast.error("Impossible de supprimer (des documents sont lies a cette categorie)")
  })

  const startEdit = (cat) => {
    setEditingId(cat.id)
    setEditForm({ name: cat.name, description: cat.description || "" })
  }

  const cancelEdit = () => setEditingId(null)

  const confirmDelete = (cat) => {
    if (window.confirm(`Supprimer la categorie "${cat.name}" ?\nAttention : impossible si des documents y sont lies.`)) {
      deleteMutation.mutate(cat.id)
    }
  }

  // Sans pagination : l'API retourne directement un tableau
  const list = Array.isArray(categories) ? categories : (categories?.results ?? [])

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Categories de documents</h1>
            <p className="text-gray-500 text-sm mt-1">
              {list.length} categorie(s) disponible(s) pour les admins partenaires
            </p>
          </div>
          <button onClick={() => { setShowForm(true); setForm(emptyForm) }} className="btn-primary flex items-center gap-2">
            <FiPlusCircle /> Nouvelle categorie
          </button>
        </div>

        {/* Tableau CRUD */}
        <div className="card overflow-x-auto">
          {isLoading ? (
            <div className="py-10 text-center text-gray-400">Chargement...</div>
          ) : list.length === 0 ? (
            <div className="py-10 text-center text-gray-400">
              <FiTag className="text-4xl mx-auto mb-2 opacity-30" />
              <p>Aucune categorie. Cliquez sur "Nouvelle categorie" pour commencer.</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4 font-medium">#</th>
                  <th className="pb-3 pr-4 font-medium">Nom de la categorie</th>
                  <th className="pb-3 pr-4 font-medium">Description</th>
                  <th className="pb-3 pr-4 font-medium">Cree par</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {list.map((cat, idx) => (
                  <tr key={cat.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 pr-4 text-gray-400 text-xs">{idx + 1}</td>

                    {editingId === cat.id ? (
                      <>
                        <td className="py-2 pr-4">
                          <input
                            type="text"
                            className="input-field text-sm py-1.5"
                            value={editForm.name}
                            onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                            autoFocus
                          />
                        </td>
                        <td className="py-2 pr-4">
                          <input
                            type="text"
                            className="input-field text-sm py-1.5"
                            value={editForm.description}
                            onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                            placeholder="Description (optionnel)"
                          />
                        </td>
                        <td className="py-2 pr-4 text-gray-400 text-xs">—</td>
                        <td className="py-2 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => updateMutation.mutate({ id: cat.id, data: editForm })}
                              disabled={updateMutation.isPending || !editForm.name.trim()}
                              className="flex items-center gap-1 bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-50"
                            >
                              <FiCheck /> Sauvegarder
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="flex items-center gap-1 bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1.5 rounded-lg text-xs font-medium"
                            >
                              <FiX /> Annuler
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-3 pr-4">
                          <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-primary/10 rounded-lg">
                              <FiTag className="text-primary text-sm" />
                            </div>
                            <span className="font-medium text-gray-800">{cat.name}</span>
                          </div>
                        </td>
                        <td className="py-3 pr-4 text-gray-500 text-xs">
                          {cat.description || <span className="italic text-gray-300">Aucune description</span>}
                        </td>
                        <td className="py-3 pr-4 text-gray-400 text-xs">
                          {cat.created_by ? `Admin #${cat.created_by}` : "Systeme"}
                        </td>
                        <td className="py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => startEdit(cat)}
                              className="flex items-center gap-1 text-primary hover:bg-primary/10 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors"
                            >
                              <FiEdit2 /> Modifier
                            </button>
                            <button
                              onClick={() => confirmDelete(cat)}
                              disabled={deleteMutation.isPending}
                              className="flex items-center gap-1 text-red-500 hover:bg-red-50 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                            >
                              <FiTrash2 /> Supprimer
                            </button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Modal création */}
        {showForm && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-lg">Nouvelle categorie</h2>
                <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
                  <FiX className="text-xl" />
                </button>
              </div>
              <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form) }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom de la categorie <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="Ex: Diplome universitaire"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    required
                    autoFocus
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    className="input-field"
                    rows={3}
                    placeholder="Description optionnelle..."
                    value={form.description}
                    onChange={e => setForm({ ...form, description: e.target.value })}
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">
                    Annuler
                  </button>
                  <button type="submit" disabled={createMutation.isPending || !form.name.trim()} className="btn-primary flex-1">
                    {createMutation.isPending ? "Creation..." : "Creer la categorie"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
