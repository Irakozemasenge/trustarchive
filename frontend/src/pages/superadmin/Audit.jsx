import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../../api/axios"
import Sidebar from "../../components/Sidebar"
import { FiHome, FiUsers, FiFileText, FiLink, FiActivity, FiAlertTriangle, FiCheckCircle, FiTag, FiChevronLeft, FiChevronRight } from "react-icons/fi"

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

const levelColor = {
  INFO: "bg-blue-100 text-blue-700",
  WARNING: "bg-yellow-100 text-yellow-700",
  ERROR: "bg-red-100 text-red-700",
  CRITICAL: "bg-red-200 text-red-900"
}
const severityColor = {
  low: "bg-gray-100 text-gray-600",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700"
}

function Pagination({ page, setPage, data }) {
  if (!data) return null
  const totalPages = Math.ceil(data.count / 20)
  if (totalPages <= 1) return null
  return (
    <div className="flex items-center justify-between mt-4 pt-4 border-t">
      <p className="text-xs text-gray-500">
        {data.count} entrée(s) — Page {page} / {totalPages}
      </p>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={!data.previous}
          className="p-1.5 rounded-lg border hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <FiChevronLeft />
        </button>
        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
          const n = Math.max(1, Math.min(page - 2, totalPages - 4)) + i
          return (
            <button
              key={n}
              onClick={() => setPage(n)}
              className={`w-8 h-8 rounded-lg text-xs font-medium ${n === page ? "bg-primary text-white" : "border hover:bg-gray-50"}`}
            >
              {n}
            </button>
          )
        })}
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={!data.next}
          className="p-1.5 rounded-lg border hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <FiChevronRight />
        </button>
      </div>
    </div>
  )
}

export default function SuperAudit() {
  const qc = useQueryClient()
  const [tab, setTab] = useState("logs")
  const [actionFilter, setActionFilter] = useState("")
  const [levelFilter, setLevelFilter] = useState("")
  const [logsPage, setLogsPage] = useState(1)
  const [errorsPage, setErrorsPage] = useState(1)

  const { data: stats } = useQuery({
    queryKey: ["auditStats"],
    queryFn: () => api.get("/audit/stats/").then(r => r.data)
  })

  const { data: logs, isLoading: logsLoading } = useQuery({
    queryKey: ["auditLogs", actionFilter, levelFilter, logsPage],
    queryFn: () => {
      const params = new URLSearchParams()
      if (actionFilter) params.append("action", actionFilter)
      if (levelFilter) params.append("level", levelFilter)
      params.append("page", logsPage)
      return api.get(`/audit/logs/?${params.toString()}`).then(r => r.data)
    },
    keepPreviousData: true,
  })

  const { data: errors, isLoading: errorsLoading } = useQuery({
    queryKey: ["sysErrors", errorsPage],
    queryFn: () => api.get(`/audit/errors/?page=${errorsPage}`).then(r => r.data),
    keepPreviousData: true,
  })

  const resolveMutation = useMutation({
    mutationFn: (id) => api.patch(`/audit/errors/${id}/resolve/`),
    onSuccess: () => qc.invalidateQueries(["sysErrors"])
  })

  const handleFilterChange = (setter) => (e) => {
    setter(e.target.value)
    setLogsPage(1)
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <h1 className="text-2xl font-bold text-gray-800 mb-1">Journal d audit</h1>
        <p className="text-gray-500 text-sm mb-6">Suivi complet de toutes les actions et erreurs de la plateforme</p>

        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Total logs", value: stats?.total_logs ?? "...", color: "text-blue-600 bg-blue-50", icon: FiActivity },
            { label: "Erreurs aujourd hui", value: stats?.errors_today ?? "...", color: "text-red-600 bg-red-50", icon: FiAlertTriangle },
            { label: "Erreurs non resolues", value: stats?.unresolved_errors ?? "...", color: "text-orange-600 bg-orange-50", icon: FiAlertTriangle },
            { label: "Erreurs critiques", value: stats?.critical_errors ?? "...", color: "text-red-700 bg-red-100", icon: FiAlertTriangle },
            { label: "Connexions aujourd hui", value: stats?.logins_today ?? "...", color: "text-green-600 bg-green-50", icon: FiCheckCircle },
            { label: "Verifications aujourd hui", value: stats?.verifications_today ?? "...", color: "text-purple-600 bg-purple-50", icon: FiCheckCircle },
          ].map(({ label, value, color, icon: Icon }) => (
            <div key={label} className="card flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${color}`}><Icon className="text-xl" /></div>
              <div>
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-xl font-bold">{value}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("logs")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "logs" ? "bg-primary text-white" : "bg-white text-gray-600 hover:bg-gray-100"}`}
          >
            Journal d actions {logs?.count > 0 && <span className="ml-1 text-xs opacity-70">({logs.count})</span>}
          </button>
          <button
            onClick={() => setTab("errors")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "errors" ? "bg-primary text-white" : "bg-white text-gray-600 hover:bg-gray-100"}`}
          >
            Erreurs systeme
            {stats?.unresolved_errors > 0 && (
              <span className="ml-1.5 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">{stats.unresolved_errors}</span>
            )}
          </button>
        </div>

        {tab === "logs" && (
          <div className="card">
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <select className="input-field w-44" value={actionFilter} onChange={handleFilterChange(setActionFilter)}>
                <option value="">Toutes les actions</option>
                <option value="LOGIN">Connexion</option>
                <option value="CREATE">Creation</option>
                <option value="UPDATE">Modification</option>
                <option value="VERIFY">Verification</option>
                <option value="REVOKE">Revocation</option>
                <option value="REGISTER_BLOCKCHAIN">Blockchain</option>
                <option value="ERROR">Erreur</option>
              </select>
              <select className="input-field w-36" value={levelFilter} onChange={handleFilterChange(setLevelFilter)}>
                <option value="">Tous les niveaux</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
              {(actionFilter || levelFilter) && (
                <button onClick={() => { setActionFilter(""); setLevelFilter(""); setLogsPage(1) }}
                  className="text-xs text-gray-400 hover:text-red-500 underline">
                  Effacer filtres
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              {logsLoading ? (
                <div className="py-8 text-center text-gray-400">Chargement...</div>
              ) : logs?.results?.length === 0 ? (
                <div className="py-8 text-center text-gray-400">Aucun log trouve</div>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b text-left text-gray-500">
                      <th className="pb-3 pr-3 font-medium">Date</th>
                      <th className="pb-3 pr-3 font-medium">Utilisateur</th>
                      <th className="pb-3 pr-3 font-medium">Action</th>
                      <th className="pb-3 pr-3 font-medium">Niveau</th>
                      <th className="pb-3 pr-3 font-medium">Description</th>
                      <th className="pb-3 pr-3 font-medium">Methode</th>
                      <th className="pb-3 font-medium">IP</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs?.results?.map(log => (
                      <tr key={log.id} className="border-b hover:bg-gray-50">
                        <td className="py-2 pr-3 text-gray-400 whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString("fr-FR")}
                        </td>
                        <td className="py-2 pr-3 font-medium">{log.user_email || "Anonyme"}</td>
                        <td className="py-2 pr-3">
                          <span className="font-mono font-semibold text-primary">{log.action}</span>
                        </td>
                        <td className="py-2 pr-3">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${levelColor[log.level] || "bg-gray-100"}`}>
                            {log.level}
                          </span>
                        </td>
                        <td className="py-2 pr-3 max-w-xs">
                          <span className="block truncate" title={log.description}>{log.description}</span>
                        </td>
                        <td className="py-2 pr-3 text-gray-400">{log.method}</td>
                        <td className="py-2 text-gray-400">{log.ip_address}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <Pagination page={logsPage} setPage={setLogsPage} data={logs} />
          </div>
        )}

        {tab === "errors" && (
          <div className="card">
            <div className="overflow-x-auto">
              {errorsLoading ? (
                <div className="py-8 text-center text-gray-400">Chargement...</div>
              ) : errors?.results?.length === 0 ? (
                <div className="py-8 text-center text-gray-400">Aucune erreur enregistree</div>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b text-left text-gray-500">
                      <th className="pb-3 pr-3 font-medium">Date</th>
                      <th className="pb-3 pr-3 font-medium">Type</th>
                      <th className="pb-3 pr-3 font-medium">Message</th>
                      <th className="pb-3 pr-3 font-medium">Severite</th>
                      <th className="pb-3 pr-3 font-medium">Endpoint</th>
                      <th className="pb-3 pr-3 font-medium">Statut</th>
                      <th className="pb-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {errors?.results?.map(err => (
                      <tr key={err.id} className="border-b hover:bg-gray-50">
                        <td className="py-2 pr-3 text-gray-400 whitespace-nowrap">
                          {new Date(err.created_at).toLocaleString("fr-FR")}
                        </td>
                        <td className="py-2 pr-3 font-mono font-semibold text-red-600">{err.error_type}</td>
                        <td className="py-2 pr-3 max-w-xs">
                          <span className="block truncate" title={err.message}>{err.message}</span>
                        </td>
                        <td className="py-2 pr-3">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityColor[err.severity] || ""}`}>
                            {err.severity}
                          </span>
                        </td>
                        <td className="py-2 pr-3 text-gray-500 font-mono">{err.endpoint}</td>
                        <td className="py-2 pr-3">
                          {err.resolved
                            ? <span className="text-green-600 flex items-center gap-1"><FiCheckCircle /> Resolu</span>
                            : <span className="text-red-500 font-medium">Non resolu</span>}
                        </td>
                        <td className="py-2">
                          {!err.resolved && (
                            <button
                              onClick={() => resolveMutation.mutate(err.id)}
                              className="text-primary hover:underline font-medium"
                            >
                              Resoudre
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <Pagination page={errorsPage} setPage={setErrorsPage} data={errors} />
          </div>
        )}
      </main>
    </div>
  )
}
