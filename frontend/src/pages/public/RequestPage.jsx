import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import api from "../../api/axios"
import Navbar from "../../components/Navbar"
import toast from "react-hot-toast"
import { FiFileText, FiUsers } from "react-icons/fi"

const PARTNER_LABELS = { notaire: "Notaire", universite: "Universite", entreprise: "Entreprise", gouvernement: "Gouvernement", autre: "Autre" }

export default function RequestPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ document_title: "", request_type: "new", description: "", target_admin: "" })
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)

  const { data: partners } = useQuery({
    queryKey: ["partners"],
    queryFn: () => api.get("/auth/partners/").then(r => r.data)
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.target_admin) return toast.error("Veuillez choisir une organisation")
    setLoading(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => { if (v) fd.append(k, v) })
      if (file) fd.append("supporting_file", file)
      await api.post("/requests/", fd, { headers: { "Content-Type": "multipart/form-data" } })
      toast.success("Demande soumise avec succes")
      navigate("/")
    } catch {
      toast.error("Erreur lors de la soumission")
    } finally {
      setLoading(false)
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const grouped = (partners || []).reduce((acc, p) => {
    const type = p.partner_type || "autre"
    if (!acc[type]) acc[type] = []
    acc[type].push(p)
    return acc
  }, {})

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-xl mx-auto px-4 py-16">
        <div className="text-center mb-8">
          <FiFileText className="text-primary text-5xl mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-gray-800">Faire une demande de document</h1>
          <p className="text-gray-500 text-sm mt-1">Choisissez l organisation et decrivez votre besoin</p>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organisation destinataire <span className="text-red-500">*</span>
              </label>
              <select className="input-field" value={form.target_admin} onChange={set("target_admin")} required>
                <option value="">-- Choisir une organisation --</option>
                {Object.entries(grouped).map(([type, list]) => (
                  <optgroup key={type} label={PARTNER_LABELS[type] || type}>
                    {list.map(p => (
                      <option key={p.id} value={p.id}>{p.organization_name || p.full_name}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
              {form.target_admin && (
                <p className="text-xs text-green-600 mt-1">Votre demande sera envoyee directement a cette organisation.</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type de demande</label>
              <select className="input-field" value={form.request_type} onChange={set("request_type")}>
                <option value="new">Nouveau document</option>
                <option value="copy">Copie certifiee</option>
                <option value="verification">Verification officielle</option>
                <option value="correction">Correction</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Titre du document <span className="text-red-500">*</span></label>
              <input type="text" className="input-field" placeholder="Ex: Diplome de licence..." value={form.document_title} onChange={set("document_title")} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description <span className="text-red-500">*</span></label>
              <textarea className="input-field" rows={4} placeholder="Decrivez votre demande en detail..." value={form.description} onChange={set("description")} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fichier justificatif (optionnel)</label>
              <input type="file" className="input-field" onChange={e => setFile(e.target.files[0])} />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
              {loading ? "Envoi en cours..." : "Soumettre la demande"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
