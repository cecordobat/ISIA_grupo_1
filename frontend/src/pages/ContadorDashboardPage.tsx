import { useEffect, useState } from 'react'
import { contadorApi } from '../api/contador'
import type { ClienteContador } from '../api/contador'
import { MFASetupModal } from '../components/auth/MFASetupModal'
import { HistorialLiquidaciones } from '../components/liquidacion/HistorialLiquidaciones'
import { useAuthStore } from '../store/authStore'

export function ContadorDashboardPage() {
  const logout = useAuthStore((s) => s.logout)
  const [clientes, setClientes] = useState<ClienteContador[]>([])
  const [seleccionado, setSeleccionado] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showMFASetup, setShowMFASetup] = useState(false)

  useEffect(() => {
    let activo = true
    const cargar = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await contadorApi.listarClientes()
        if (!activo) return
        setClientes(data)
        setSeleccionado(data[0]?.perfil_id ?? null)
      } catch {
        if (!activo) return
        setError('No se pudieron cargar los clientes autorizados.')
      } finally {
        if (activo) setLoading(false)
      }
    }
    void cargar()
    return () => {
      activo = false
    }
  }, [])

  return (
    <div className="wizard-container">
      <div className="wizard-header">
        <h1>Portal Contador</h1>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={() => setShowMFASetup(true)}>
            Configurar MFA
          </button>
          <button className="btn-logout" onClick={logout}>
            Cerrar sesion
          </button>
        </div>
      </div>

      {showMFASetup && (
        <MFASetupModal
          onComplete={() => setShowMFASetup(false)}
          onCancel={() => setShowMFASetup(false)}
        />
      )}

      <div className="wizard-step">
        <h2>Clientes autorizados</h2>
        {loading ? (
          <div className="loading-state">Cargando clientes...</div>
        ) : error ? (
          <div className="error-banner">{error}</div>
        ) : clientes.length === 0 ? (
          <div className="aviso-requerido">
            Aun no tiene contratistas vinculados. Cada contratista debe autorizar su acceso desde su perfil.
          </div>
        ) : (
          <div className="historial-lista">
            {clientes.map((cliente) => (
              <button
                key={cliente.perfil_id}
                type="button"
                className={`card historial-item ${seleccionado === cliente.perfil_id ? 'selected' : ''}`}
                onClick={() => setSeleccionado(cliente.perfil_id)}
              >
                <strong>{cliente.nombre_contratista}</strong>
                <span>Documento: {cliente.numero_documento}</span>
                <span>CIIU: {cliente.ciiu_codigo}</span>
                <span>Email: {cliente.contratista_email}</span>
              </button>
            ))}
          </div>
        )}

        {seleccionado && <HistorialLiquidaciones perfilId={seleccionado} />}
      </div>
    </div>
  )
}
