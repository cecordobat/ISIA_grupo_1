import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { LiquidacionWizardPage } from './pages/LiquidacionWizardPage'
import { ContadorDashboardPage } from './pages/ContadorDashboardPage'
import { useAuthStore } from './store/authStore'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
})

function ProtectedRoute({
  children,
  requiredRole,
}: {
  children: React.ReactNode
  requiredRole?: 'CONTRATISTA' | 'CONTADOR'
}) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const rol = useAuthStore((s) => s.rol)

  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!rol) return <Navigate to="/login" replace />
  if (requiredRole && rol !== requiredRole) {
    return <Navigate to={rol === 'CONTADOR' ? '/contador' : '/liquidacion'} replace />
  }
  return <>{children}</>
}

function RootRedirect() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const rol = useAuthStore((s) => s.rol)
  if (!isAuthenticated || !rol) return <Navigate to="/login" replace />
  return <Navigate to={rol === 'CONTADOR' ? '/contador' : '/liquidacion'} replace />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/liquidacion"
            element={
              <ProtectedRoute requiredRole="CONTRATISTA">
                <LiquidacionWizardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/contador"
            element={
              <ProtectedRoute requiredRole="CONTADOR">
                <ContadorDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
)
