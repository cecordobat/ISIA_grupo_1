/**
 * Paso 1 del wizard: Selección del perfil de contratista a liquidar.
 * Carga los perfiles del usuario autenticado y permite seleccionar uno.
 * Ref: HU-01, RF-01
 */
import { useState, useEffect } from 'react'
import { perfilesApi } from '../../api/perfiles'
import type { PerfilResponse } from '../../api/perfiles'
import { useLiquidacionStore } from '../../store/liquidacionStore'

export function StepSeleccionarPerfil() {
  const [perfiles, setPerfiles] = useState<PerfilResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { anio, mes, setPeriodo, avanzarPaso } = useLiquidacionStore()

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    perfilesApi
      .listar()
      .then((data) => {
        if (!cancelled) {
          setPerfiles(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('No se pudieron cargar los perfiles. Verifique su conexión e intente nuevamente.')
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const handleContinuar = () => {
    if (!selectedId) return
    setPeriodo(selectedId, anio, mes)
    avanzarPaso()
  }

  if (loading) {
    return (
      <div className="wizard-step">
        <h2>Seleccionar Perfil</h2>
        <div className="loading-state">Cargando perfiles...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="wizard-step">
        <h2>Seleccionar Perfil</h2>
        <div className="error-banner">{error}</div>
      </div>
    )
  }

  if (perfiles.length === 0) {
    return (
      <div className="wizard-step">
        <h2>Seleccionar Perfil</h2>
        <div className="aviso-requerido">
          No tiene perfiles registrados. Contacte al administrador para crear un perfil de contratista.
        </div>
      </div>
    )
  }

  return (
    <div className="wizard-step">
      <h2>Seleccionar Perfil</h2>
      <p className="step-description">
        Seleccione el perfil de contratista para el cual desea realizar la liquidación:
      </p>

      <div className="perfiles-lista">
        {perfiles.map((perfil) => (
          <div
            key={perfil.id}
            className={`card ${selectedId === perfil.id ? 'selected' : ''}`}
            onClick={() => setSelectedId(perfil.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && setSelectedId(perfil.id)}
          >
            <div className="perfil-header">
              <input
                type="radio"
                name="perfil"
                id={`perfil-${perfil.id}`}
                checked={selectedId === perfil.id}
                onChange={() => setSelectedId(perfil.id)}
              />
              <label htmlFor={`perfil-${perfil.id}`}>
                <strong>{perfil.nombre_completo}</strong>
              </label>
            </div>
            <div className="perfil-detalles">
              <span>{perfil.tipo_documento}: {perfil.numero_documento}</span>
              <span>CIIU: {perfil.ciiu_codigo}</span>
              <span>EPS: {perfil.eps} | AFP: {perfil.afp}</span>
              {perfil.estado !== 'activo' && (
                <span className="perfil-estado-inactivo">Estado: {perfil.estado}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <button
        className="btn-primary"
        onClick={handleContinuar}
        disabled={selectedId === null}
      >
        Continuar
      </button>
    </div>
  )
}
