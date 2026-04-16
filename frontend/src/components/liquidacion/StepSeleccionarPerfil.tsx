import { useEffect, useState } from 'react'
import axios from 'axios'
import { perfilesApi } from '../../api/perfiles'
import { contadorApi } from '../../api/contador'
import type { PerfilCreate, PerfilResponse } from '../../api/perfiles'
import { HistorialLiquidaciones } from './HistorialLiquidaciones'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const emptyPerfilForm: PerfilCreate = {
  tipo_documento: 'CC',
  numero_documento: '',
  nombre_completo: '',
  eps: '',
  afp: '',
  ciiu_codigo: '',
  confirmar_ciiu_alto: false,
}

export function StepSeleccionarPerfil() {
  const [perfiles, setPerfiles] = useState<PerfilResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [editingPerfilId, setEditingPerfilId] = useState<string | null>(null)
  const [contadorEmail, setContadorEmail] = useState('')
  const [shareMessage, setShareMessage] = useState<string | null>(null)
  const [newPerfil, setNewPerfil] = useState<PerfilCreate>(emptyPerfilForm)
  const [createError, setCreateError] = useState<string | null>(null)
  const [createWarning, setCreateWarning] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const { anio, mes, setPeriodo, avanzarPaso } = useLiquidacionStore()

  const cargarPerfiles = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await perfilesApi.listar()
      setPerfiles(data)
      setSelectedId((current) => current ?? data[0]?.id ?? null)
    } catch {
      setError('No se pudieron cargar los perfiles. Verifique su conexion e intente nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void cargarPerfiles()
  }, [])

  const resetFormState = () => {
    setEditingPerfilId(null)
    setNewPerfil(emptyPerfilForm)
    setCreateError(null)
    setCreateWarning(null)
  }

  const handleContinuar = () => {
    if (!selectedId) return
    setPeriodo(selectedId, anio, mes)
    avanzarPaso()
  }

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreateError(null)
    setCreateWarning(null)
    setCreating(true)
    try {
      if (editingPerfilId) {
        await perfilesApi.actualizar(editingPerfilId, newPerfil)
      } else {
        await perfilesApi.crear(newPerfil)
      }
      setIsCreating(false)
      resetFormState()
      await cargarPerfiles()
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        const detail = err.response.data?.detail
        if (detail?.requires_ciiu_confirmation) {
          setCreateWarning(
            `El CIIU seleccionado tiene costos presuntos de ${(Number(detail.pct_costos_presuntos) * 100).toFixed(2)}%. Debe confirmar expresamente antes de guardar el perfil.`
          )
          return
        }
      }
      setCreateError(
        editingPerfilId
          ? 'Error al actualizar el perfil. Asegurese de que el CIIU sea valido.'
          : 'Error al crear perfil. Asegurese de que el CIIU sea valido.'
      )
    } finally {
      setCreating(false)
    }
  }

  const handleEditarPerfil = () => {
    const perfil = perfiles.find((item) => item.id === selectedId)
    if (!perfil) return
    setEditingPerfilId(perfil.id)
    setNewPerfil({
      tipo_documento: perfil.tipo_documento,
      numero_documento: perfil.numero_documento,
      nombre_completo: perfil.nombre_completo,
      eps: perfil.eps,
      afp: perfil.afp,
      ciiu_codigo: perfil.ciiu_codigo,
      confirmar_ciiu_alto: false,
    })
    setCreateError(null)
    setCreateWarning(null)
    setIsCreating(true)
  }

  const handleCompartirConContador = async () => {
    if (!selectedId || !contadorEmail) return
    setShareMessage(null)
    try {
      const respuesta = await contadorApi.vincular({
        perfil_id: selectedId,
        contador_email: contadorEmail,
      })
      setShareMessage(respuesta.message)
      setContadorEmail('')
    } catch {
      setShareMessage(
        'No fue posible vincular el contador. Verifique que exista una cuenta con tipo Contador y ese email.'
      )
    }
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

  if (isCreating) {
    return (
      <div className="wizard-step">
        <h2>{editingPerfilId ? 'Editar Perfil' : 'Crear Nuevo Perfil'}</h2>
        <form onSubmit={handleCreateSubmit} className="perfil-form">
          <div className="field">
            <label htmlFor="perfil-tipo-documento">Tipo Documento</label>
            <select
              id="perfil-tipo-documento"
              value={newPerfil.tipo_documento}
              onChange={(e) => setNewPerfil({ ...newPerfil, tipo_documento: e.target.value })}
            >
              <option value="CC">CC</option>
              <option value="CE">CE</option>
              <option value="PEP">PEP</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="perfil-numero-documento">Numero Documento</label>
            <input
              id="perfil-numero-documento"
              required
              value={newPerfil.numero_documento}
              onChange={(e) => setNewPerfil({ ...newPerfil, numero_documento: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="perfil-nombre-completo">Nombre Completo</label>
            <input
              id="perfil-nombre-completo"
              required
              value={newPerfil.nombre_completo}
              onChange={(e) => setNewPerfil({ ...newPerfil, nombre_completo: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="perfil-eps">EPS</label>
            <input
              id="perfil-eps"
              required
              value={newPerfil.eps}
              onChange={(e) => setNewPerfil({ ...newPerfil, eps: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="perfil-afp">AFP</label>
            <input
              id="perfil-afp"
              required
              value={newPerfil.afp}
              onChange={(e) => setNewPerfil({ ...newPerfil, afp: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="perfil-ciiu">Codigo CIIU</label>
            <input
              id="perfil-ciiu"
              required
              value={newPerfil.ciiu_codigo}
              onChange={(e) => setNewPerfil({ ...newPerfil, ciiu_codigo: e.target.value })}
            />
          </div>
          {createWarning && <div className="aviso-requerido">{createWarning}</div>}
          {createWarning && (
            <label className="checkbox-inline">
              <input
                type="checkbox"
                checked={newPerfil.confirmar_ciiu_alto ?? false}
                onChange={(e) =>
                  setNewPerfil({ ...newPerfil, confirmar_ciiu_alto: e.target.checked })
                }
              />
              Confirmo que este CIIU corresponde exactamente a mi actividad economica.
            </label>
          )}
          {createError && <div className="error-banner">{createError}</div>}
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? 'Guardando...' : editingPerfilId ? 'Guardar cambios' : 'Guardar Perfil'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false)
                resetFormState()
              }}
              className="btn-secondary"
            >
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
        <button
          className="btn-primary"
          onClick={() => {
            resetFormState()
            setIsCreating(true)
          }}
          style={{ marginTop: '1rem' }}
        >
          Crear Nuevo Perfil
        </button>
      </div>
    )
  }

  return (
    <div className="wizard-step">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Seleccionar Perfil</h2>
        <div className="wizard-actions">
          {selectedId && (
            <button className="btn-secondary" onClick={handleEditarPerfil}>
              Editar perfil
            </button>
          )}
          <button
            className="btn-secondary"
            onClick={() => {
              resetFormState()
              setIsCreating(true)
            }}
          >
            Crear Perfil
          </button>
        </div>
      </div>
      <p className="step-description">
        Seleccione el perfil de contratista para el cual desea realizar la liquidacion:
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
              <span>
                {perfil.tipo_documento}: {perfil.numero_documento}
              </span>
              <span>CIIU: {perfil.ciiu_codigo}</span>
              {perfil.pct_costos_presuntos && (
                <span>
                  Costos presuntos: {(Number(perfil.pct_costos_presuntos) * 100).toFixed(2)}%
                </span>
              )}
              <span>
                EPS: {perfil.eps} | AFP: {perfil.afp}
              </span>
              {perfil.pct_costos_presuntos && Number(perfil.pct_costos_presuntos) > 0.6 && (
                <span className="perfil-estado-inactivo">
                  Requiere validacion especial: costos presuntos superiores al 60%.
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="wizard-actions">
        <button className="btn-primary" onClick={handleContinuar} disabled={selectedId === null}>
          Continuar
        </button>
      </div>

      {selectedId && (
        <div className="share-panel">
          <h3>Autorizar contador</h3>
          <p className="step-description">
            Ingrese el email de un contador registrado para darle acceso de lectura a este perfil y su historial.
          </p>
          <p className="nota-neto">
            El contador debe haberse registrado antes con tipo de cuenta Contador y luego ingresar desde la pantalla normal de login.
          </p>
          <div className="wizard-actions">
            <input
              className="share-input"
              type="email"
              placeholder="contador@correo.com"
              value={contadorEmail}
              onChange={(e) => setContadorEmail(e.target.value)}
            />
            <button className="btn-secondary" onClick={() => void handleCompartirConContador()}>
              Vincular contador
            </button>
          </div>
          {shareMessage && <div className="aviso-tope">{shareMessage}</div>}
        </div>
      )}

      {selectedId && <HistorialLiquidaciones perfilId={selectedId} />}
    </div>
  )
}
