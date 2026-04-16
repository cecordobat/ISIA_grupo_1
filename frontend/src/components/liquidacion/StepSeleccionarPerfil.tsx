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
  const [isCreating, setIsCreating] = useState(false)
  const [newPerfil, setNewPerfil] = useState({
    tipo_documento: 'CC',
    numero_documento: '',
    nombre_completo: '',
    eps: '',
    afp: '',
    ciiu_codigo: '',
  })
  const [createError, setCreateError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const { anio, mes, setPeriodo, avanzarPaso } = useLiquidacionStore()

  const cargarPerfiles = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await perfilesApi.listar()
      setPerfiles(data)
    } catch {
      setError('No se pudieron cargar los perfiles. Verifique su conexión e intente nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    cargarPerfiles().then(() => {
      if (cancelled) return
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

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreateError(null)
    setCreating(true)
    try {
      await perfilesApi.crear(newPerfil)
      setIsCreating(false)
      cargarPerfiles()
    } catch {
      setCreateError('Error al crear perfil. Asegúrese de que el CIIU sea válido (ej. 6201, 6910, 6920, 7020).')
    } finally {
      setCreating(false)
    }
  }

  if (isCreating) {
    return (
      <div className="wizard-step">
        <h2>Crear Nuevo Perfil</h2>
        <form onSubmit={handleCreateSubmit} className="perfil-form">
          <div className="field">
            <label>Tipo Documento</label>
            <select
              value={newPerfil.tipo_documento}
              onChange={(e) => setNewPerfil({ ...newPerfil, tipo_documento: e.target.value })}
            >
              <option value="CC">CC</option>
              <option value="CE">CE</option>
              <option value="PEP">PEP</option>
            </select>
          </div>
          <div className="field">
            <label>Número Documento</label>
            <input
              required
              value={newPerfil.numero_documento}
              onChange={(e) => setNewPerfil({ ...newPerfil, numero_documento: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Nombre Completo</label>
            <input
              required
              value={newPerfil.nombre_completo}
              onChange={(e) => setNewPerfil({ ...newPerfil, nombre_completo: e.target.value })}
            />
          </div>
          <div className="field">
            <label>EPS</label>
            <input
              required
              value={newPerfil.eps}
              onChange={(e) => setNewPerfil({ ...newPerfil, eps: e.target.value })}
            />
          </div>
          <div className="field">
            <label>AFP</label>
            <input
              required
              value={newPerfil.afp}
              onChange={(e) => setNewPerfil({ ...newPerfil, afp: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Código CIIU (ej: 6201)</label>
            <input
              required
              value={newPerfil.ciiu_codigo}
              onChange={(e) => setNewPerfil({ ...newPerfil, ciiu_codigo: e.target.value })}
            />
          </div>
          {createError && <div className="error-banner">{createError}</div>}
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? 'Guardando...' : 'Guardar Perfil'}
            </button>
            <button type="button" onClick={() => setIsCreating(false)} className="btn-secondary">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    )
  }

  if (perfiles.length === 0) {
    return (
      <div className="wizard-step">
        <h2>Seleccionar Perfil</h2>
        <div className="aviso-requerido">
          No tiene perfiles registrados. Por favor, cree su perfil de contratista.
        </div>
        <button className="btn-primary" onClick={() => setIsCreating(true)} style={{ marginTop: '1rem' }}>
          Crear Nuevo Perfil
        </button>
      </div>
    )
  }





  return (
    <div className="wizard-step">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Seleccionar Perfil</h2>
        <button className="btn-secondary" onClick={() => setIsCreating(true)}>
          Crear Perfil
        </button>
      </div>
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
