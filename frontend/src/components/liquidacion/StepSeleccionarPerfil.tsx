import { useEffect, useState } from 'react'
import axios from 'axios'
import { perfilesApi } from '../../api/perfiles'
import { contadorApi } from '../../api/contador'
import type { PerfilCreate, PerfilResponse, CIIUOption } from '../../api/perfiles'
import { HistorialLiquidaciones } from './HistorialLiquidaciones'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const EPS_COLOMBIA = [
  'Compensar EPS',
  'Sanitas EPS',
  'Nueva EPS',
  'Sura EPS',
  'Famisanar',
  'Salud Total EPS',
  'Coosalud EPS',
  'Mutual Ser EPS',
  'Capital Salud EPS',
  'Cajacopi EPS',
  'Comfenalco Valle EPS',
  'AIC EPS Indígena',
  'Asmet Salud EPS',
  'Emssanar EPS',
]

const AFP_COLOMBIA = [
  'Colpensiones',
  'Porvenir',
  'Protección',
  'Colfondos',
  'Skandia AFP',
]

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
  const [ciiuOpciones, setCiiuOpciones] = useState<CIIUOption[]>([])
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
      const [data, ciiu] = await Promise.all([
        perfilesApi.listar(),
        perfilesApi.listarCiiu(),
      ])
      setPerfiles(data)
      setCiiuOpciones(ciiu)
      setSelectedId((current) => current ?? data[0]?.id ?? null)
    } catch {
      setError('No se pudieron cargar los perfiles.')
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

  const handleEditarPerfil = (perfil: PerfilResponse) => {
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
    setIsCreating(true)
    setCreateError(null)
    setCreateWarning(null)
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
            `El CIIU seleccionado tiene costos presuntos del ${(Number(detail.pct_costos_presuntos) * 100).toFixed(2)}%. Debe confirmar.`
          )
          setNewPerfil((current) => ({ ...current, confirmar_ciiu_alto: true }))
          return
        }
      }
      setCreateError('Error al guardar perfil.')
    } finally {
      setCreating(false)
    }
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
      setShareMessage('No fue posible vincular el contador.')
    }
  }

  if (loading) {
    return <div className="text-center p-10 font-bold text-slate-400">Cargando perfiles...</div>
  }

  if (error) {
    return <div className="error-banner">{error}</div>
  }

  return (
    <div className="space-y-6 antialiased font-['Inter']">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#181c20] mb-2">Tu Perfil de Contratista</h1>
          <p className="text-[#434655] max-w-md">
            Seleccione o cree la identidad para la cual realizara el reporte de este mes.
          </p>
        </div>
        <button
          onClick={() => {
            resetFormState()
            setIsCreating(true)
          }}
          className="flex items-center gap-2 bg-[#004ac6] text-white px-6 py-2 rounded-lg font-bold text-sm shadow-md"
        >
          <span className="material-symbols-outlined text-lg">person_add</span>
          Nuevo Perfil
        </button>
      </div>

      {isCreating && (
        <div className="bg-white p-8 rounded-2xl shadow-xl border border-blue-50">
          <h3 className="text-xl font-bold mb-6 text-[#181c20]">
            {editingPerfilId ? 'Editar Perfil' : 'Crear Perfil'}
          </h3>
          <form onSubmit={handleCreateSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="tipo-documento">
                Tipo Documento
              </label>
              <select
                id="tipo-documento"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.tipo_documento}
                onChange={(e) => setNewPerfil({ ...newPerfil, tipo_documento: e.target.value })}
              >
                <option value="CC">Cedula de Ciudadania</option>
                <option value="CE">Cedula de Extranjeria</option>
                <option value="PEP">PEP</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="numero-documento">
                Numero Documento
              </label>
              <input
                id="numero-documento"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.numero_documento}
                onChange={(e) => setNewPerfil({ ...newPerfil, numero_documento: e.target.value })}
                required
              />
            </div>

            <div className="col-span-1 md:col-span-2">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="nombre-completo">
                Nombre Completo
              </label>
              <input
                id="nombre-completo"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.nombre_completo}
                onChange={(e) => setNewPerfil({ ...newPerfil, nombre_completo: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="ciiu-principal">
                CIIU Principal
              </label>
              <select
                id="ciiu-principal"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.ciiu_codigo}
                onChange={(e) => setNewPerfil({ ...newPerfil, ciiu_codigo: e.target.value, confirmar_ciiu_alto: false })}
                required
              >
                <option value="">Seleccione actividad CIIU...</option>
                {ciiuOpciones.map((c) => (
                  <option key={c.codigo} value={c.codigo}>
                    {c.codigo} — {c.descripcion}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="eps">
                EPS
              </label>
              <select
                id="eps"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.eps}
                onChange={(e) => setNewPerfil({ ...newPerfil, eps: e.target.value })}
                required
              >
                <option value="">Seleccione EPS...</option>
                {EPS_COLOMBIA.map((e) => (
                  <option key={e} value={e}>{e}</option>
                ))}
              </select>
            </div>

            <div className="col-span-1 md:col-span-2">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1" htmlFor="afp">
                AFP / Fondo de Pensiones
              </label>
              <select
                id="afp"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg"
                value={newPerfil.afp}
                onChange={(e) => setNewPerfil({ ...newPerfil, afp: e.target.value })}
                required
              >
                <option value="">Seleccione AFP...</option>
                {AFP_COLOMBIA.map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>

            <div className="col-span-1 md:col-span-2 space-y-2">
              {createWarning && (
                <div className="p-3 bg-amber-50 text-amber-700 text-xs rounded-lg border border-amber-100">
                  {createWarning}
                </div>
              )}
              {createError && (
                <div className="p-3 bg-red-50 text-red-600 text-xs rounded-lg border border-red-100">
                  {createError}
                </div>
              )}
            </div>

            <div className="col-span-1 md:col-span-2 flex gap-4 mt-4">
              <button type="submit" disabled={creating} className="bg-[#004ac6] text-white px-10 py-3 rounded-xl font-bold">
                {creating ? 'Guardando...' : 'Guardar Perfil'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsCreating(false)
                  resetFormState()
                }}
                className="bg-slate-100 text-slate-600 px-10 py-3 rounded-xl font-bold"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {perfiles.map((perfil) => (
          <div
            key={perfil.id}
            onClick={() => setSelectedId(perfil.id)}
            className={`cursor-pointer p-6 rounded-2xl border-2 transition-all ${
              selectedId === perfil.id ? 'border-[#004ac6] bg-blue-50/30' : 'border-slate-100 bg-white hover:border-slate-200'
            }`}
          >
            <div className="flex justify-between items-start mb-4">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  selectedId === perfil.id ? 'bg-[#004ac6] text-white' : 'bg-slate-100 text-slate-400'
                }`}
              >
                <span className="material-symbols-outlined">person</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="text-slate-500 hover:text-[#004ac6]"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleEditarPerfil(perfil)
                  }}
                  aria-label={`Editar perfil ${perfil.nombre_completo}`}
                >
                  <span className="material-symbols-outlined">edit</span>
                </button>
                {selectedId === perfil.id && (
                  <span className="text-[#004ac6] material-symbols-outlined">check_circle</span>
                )}
              </div>
            </div>
            <h4 className="font-bold text-lg text-[#181c20]">{perfil.nombre_completo}</h4>
            <div className="text-sm text-slate-500 mt-2 space-y-1">
              <p>
                {perfil.tipo_documento}: {perfil.numero_documento}
              </p>
              <p>
                Actividad CIIU: <span className="font-bold text-slate-700">{perfil.ciiu_codigo}</span>
              </p>
              <p>
                EPS: {perfil.eps} | AFP: {perfil.afp}
              </p>
            </div>
          </div>
        ))}
      </div>

      {selectedId && (
        <div className="flex justify-between items-center pt-6">
          <div className="flex gap-2">
            <input
              className="p-3 bg-white border border-slate-200 rounded-lg text-sm w-64"
              placeholder="Vincular email del contador"
              value={contadorEmail}
              onChange={(e) => setContadorEmail(e.target.value)}
            />
            <button
              onClick={() => void handleCompartirConContador()}
              className="bg-slate-100 text-slate-600 px-4 rounded-lg font-bold text-sm"
            >
              Vincular
            </button>
          </div>
          <button
            onClick={() => {
              setPeriodo(selectedId, anio, mes)
              avanzarPaso()
            }}
            className="bg-[#004ac6] text-white px-10 py-3 rounded-xl font-bold shadow-lg shadow-blue-100 hover:scale-105 transition-all flex items-center gap-2"
          >
            Continuar
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      )}

      {shareMessage && <p className="text-xs text-blue-600 font-medium">{shareMessage}</p>}

      {selectedId && (
        <div className="mt-10 pt-10 border-t border-slate-100">
          <HistorialLiquidaciones perfilId={selectedId} />
        </div>
      )}
    </div>
  )
}
