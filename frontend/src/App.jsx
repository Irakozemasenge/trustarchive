import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

// Public pages
import HomePage from './pages/public/HomePage'
import VerifyPage from './pages/public/VerifyPage'
import LoginPage from './pages/public/LoginPage'
import RegisterPage from './pages/public/RegisterPage'
import RequestPage from './pages/public/RequestPage'

// Admin pages
import AdminDashboard from './pages/admin/Dashboard'
import AdminDocuments from './pages/admin/Documents'
import AdminAddDocument from './pages/admin/AddDocument'
import AdminRequests from './pages/admin/Requests'
import AdminQRList from './pages/admin/QRList'

// SuperAdmin pages
import SuperDashboard from './pages/superadmin/Dashboard'
import SuperAdmins from './pages/superadmin/Admins'
import SuperDocuments from './pages/superadmin/Documents'
import SuperBlockchain from './pages/superadmin/Blockchain'
import SuperAudit from './pages/superadmin/Audit'
import SuperCategories from './pages/superadmin/Categories'

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen">Chargement...</div>
  if (!user) return <Navigate to="/login" />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/" element={<HomePage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/verify/:uniqueNumber" element={<VerifyPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/request" element={<ProtectedRoute roles={['public','admin','superadmin']}><RequestPage /></ProtectedRoute>} />

        {/* Admin Partner */}
        <Route path="/admin" element={<ProtectedRoute roles={['admin','superadmin']}><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/documents" element={<ProtectedRoute roles={['admin','superadmin']}><AdminDocuments /></ProtectedRoute>} />
        <Route path="/admin/documents/add" element={<ProtectedRoute roles={['admin','superadmin']}><AdminAddDocument /></ProtectedRoute>} />
        <Route path="/admin/qrcodes" element={<ProtectedRoute roles={['admin','superadmin']}><AdminQRList /></ProtectedRoute>} />
        <Route path="/admin/requests" element={<ProtectedRoute roles={['admin','superadmin']}><AdminRequests /></ProtectedRoute>} />

        {/* SuperAdmin */}
        <Route path="/superadmin" element={<ProtectedRoute roles={['superadmin']}><SuperDashboard /></ProtectedRoute>} />
        <Route path="/superadmin/admins" element={<ProtectedRoute roles={['superadmin']}><SuperAdmins /></ProtectedRoute>} />
        <Route path="/superadmin/documents" element={<ProtectedRoute roles={['superadmin']}><SuperDocuments /></ProtectedRoute>} />
        <Route path="/superadmin/blockchain" element={<ProtectedRoute roles={['superadmin']}><SuperBlockchain /></ProtectedRoute>} />
        <Route path="/superadmin/audit" element={<ProtectedRoute roles={['superadmin']}><SuperAudit /></ProtectedRoute>} />
        <Route path="/superadmin/categories" element={<ProtectedRoute roles={['superadmin']}><SuperCategories /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </AuthProvider>
  )
}
