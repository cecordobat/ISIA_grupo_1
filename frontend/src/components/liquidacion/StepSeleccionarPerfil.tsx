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
          setCreateWarning(`El CIIU seleccionado tiene costos presuntos del ${(Number(detail.pct_costos_presuntos) * 100).toFixed(2)}%. Debe confirmar.`)
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
      const respuesta = await contadorApi.vincular({ perfil_id: selectedId, contador_email: contadorEmail })
      setShareMessage(respuesta.message)
      setContadorEmail('')
    } catch {
      setShareMessage('No fue posible vincular el contador.')
    }
  }

  if (loading) return <div className="text-center p-10 font-bold text-slate-400">Cargando perfiles...</div>

  return (
    <div className="space-y-6 antialiased font-['Inter']">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#181c20] mb-2">Tu Perfil de Contratista</h1>
          <p className="text-[#434655] max-w-md">Seleccione o cree la identidad para la cual realizará el reporte de este mes.</p>
        </div>
        <button 
          onClick={() => { resetFormState(); setIsCreating(true); }}
          className="flex items-center gap-2 bg-[#004ac6] text-white px-6 py-2 rounded-lg font-bold text-sm shadow-md"
        >
          <span className="material-symbols-outlined text-lg">person_add</span>
          Nuevo Perfil
        </button>
      </div>

      {isCreating && (
        <div className="bg-white p-8 rounded-2xl shadow-xl border border-blue-50">
          <h3 className="text-xl font-bold mb-6 text-[#181c20]">{editingPerfilId ? 'Editar Perfil' : 'Crear Perfil'}</h3>
          <form onSubmit={handleCreateSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="col-span-1">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Tipo Documento</label>
              <select className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg" value={newPerfil.tipo_documento} onChange={e => setNewPerfil({...newPerfil, tipo_documento: e.target.value})}>
                <option value="CC">Cédula de Ciudadanía</option>
                <option value="CE">Cédula de Extranjería</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Número Documento</label>
              <input className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg" value={newPerfil.numero_documento} onChange={e => setNewPerfil({...newPerfil, numero_documento: e.target.value})} required/>
            </div>
            <div className="col-span-1 md:col-span-2">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Nombre Completo</label>
              <input className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg" value={newPerfil.nombre_completo} onChange={e => setNewPerfil({...newPerfil, nombre_completo: e.target.value})} required/>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">CIIU Principal</label>
              <input className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg" placeholder="e.g. 6201" value={newPerfil.ciiu_codigo} onChange={e => setNewPerfil({...newPerfil, ciiu_codigo: e.target.value})} required/>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">EPS / Fondo de Salud</label>
              <input className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg" value={newPerfil.eps} onChange={e => setNewPerfil({...newPerfil, eps: e.target.value})} required/>
            </div>
            <div className="col-span-1 md:col-span-2 space-y-2">
              {createWarning && <div className="p-3 bg-amber-50 text-amber-700 text-xs rounded-lg border border-amber-100">{createWarning}</div>}
              {createError && <div className="p-3 bg-red-50 text-red-600 text-xs rounded-lg border border-red-100">{createError}</div>}
            </div>
            <div className="col-span-1 md:col-span-2 flex gap-4 mt-4">
              <button type="submit" disabled={creating} className="bg-[#004ac6] text-white px-10 py-3 rounded-xl font-bold">{creating ? 'Guardando...' : 'Guardar Perfil'}</button>
              <button type="button" onClick={() => setIsCreating(false)} className="bg-slate-100 text-slate-600 px-10 py-3 rounded-xl font-bold">Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {perfiles.map(p => (
          <div 
            key={p.id}
            onClick={() => setSelectedId(p.id)}
            className={`cursor-pointer p-6 rounded-2xl border-2 transition-all ${selectedId === p.id ? 'border-[#004ac6] bg-blue-50/30' : 'border-slate-100 bg-white hover:border-slate-200'}`}
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${selectedId === p.id ? 'bg-[#004ac6] text-white' : 'bg-slate-100 text-slate-400'}`}>
                <span className="material-symbols-outlined">person</span>
              </div>
              {selectedId === p.id && <span className="text-[#004ac6] material-symbols-outlined">check_circle</span>}
            </div>
            <h4 className="font-bold text-lg text-[#181c20]">{p.nombre_completo}</h4>
            <div className="text-sm text-slate-500 mt-2 space-y-1">
              <p>{p.tipo_documento}: {p.numero_documento}</p>
              <p>Actividad CIIU: <span className="font-bold text-slate-700">{p.ciiu_codigo}</span></p>
              <p>EPS: {p.eps} | AFP: {p.afp}</p>
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
              onChange={e => setContadorEmail(e.target.value)}
            />
            <button onClick={() => void handleCompartirConContador()} className="bg-slate-100 text-slate-600 px-4 rounded-lg font-bold text-sm">Vincular</button>
          </div>
          <button 
            onClick={() => { setPeriodo(selectedId, anio, mes); avanzarPaso(); }}
            className="bg-[#004ac6] text-white px-10 py-3 rounded-xl font-bold shadow-lg shadow-blue-100 hover:scale-105 transition-all flex items-center gap-2"
          >
            Continuar
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      )}
      
      {shareMessage && <p className="text-xs text-blue-600 font-medium">{shareMessage}</p>}
      
      {selectedId && <div className="mt-10 pt-10 border-t border-slate-100"><HistorialLiquidaciones perfilId={selectedId} /></div>}
    </div>
  )
}
