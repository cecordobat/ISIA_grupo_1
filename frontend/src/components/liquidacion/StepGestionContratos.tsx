import React, { useEffect, useState } from 'react'
import { contratosApi } from '../../api/contratos'
import type { ContratoCreate, ContratoResponse, NivelARL } from '../../api/contratos'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const NIVELES_ARL: NivelARL[] = ['I', 'II', 'III', 'IV', 'V']

function formatCOP(valor: string): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(valor))
}

export function StepGestionContratos() {
  const perfilId = useLiquidacionStore((s) => s.perfilId)
  const avanzarPaso = useLiquidacionStore((s) => s.avanzarPaso)
  const retrocederPaso = useLiquidacionStore((s) => s.retrocederPaso)

  const [contratos, setContratos] = useState<ContratoResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingContratoId, setEditingContratoId] = useState<string | null>(null)
  const [form, setForm] = useState<ContratoCreate>({
    perfil_id: perfilId ?? '',
    entidad_contratante: '',
    valor_bruto_mensual: '',
    nivel_arl: 'I',
    fecha_inicio: '',
    fecha_fin: '',
  })

  const resetForm = () => {
    setEditingContratoId(null)
    setShowForm(false)
    setForm({
      perfil_id: perfilId ?? '',
      entidad_contratante: '',
      valor_bruto_mensual: '',
      nivel_arl: 'I',
      fecha_inicio: '',
      fecha_fin: '',
    })
  }

  const cargarContratos = async () => {
    if (!perfilId) return
    setLoading(true)
    try {
      const data = await contratosApi.listar(perfilId)
      setContratos(data)
    } catch {
      setError('Error al cargar contratos.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void cargarContratos()
  }, [perfilId])

  const handleGuardarContrato = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!perfilId) return
    setSaving(true)
    try {
      const payload = { ...form, perfil_id: perfilId, fecha_fin: form.fecha_fin || undefined }
      if (editingContratoId) {
        await contratosApi.actualizar(editingContratoId, payload)
      } else {
        await contratosApi.crear(payload)
      }
      resetForm()
      await cargarContratos()
    } catch {
      setError('Error al guardar contrato.')
    } finally {
      setSaving(false)
    }
  }

  const handleEliminarContrato = async (id: string) => {
    try {
      await contratosApi.eliminar(id)
      await cargarContratos()
    } catch {
      setError('Error al eliminar.')
    }
  }

  const handleEditarContrato = (contrato: ContratoResponse) => {
    setEditingContratoId(contrato.id)
    setForm({ ...contrato, fecha_fin: contrato.fecha_fin ?? '' })
    setShowForm(true)
  }

  const totalBruto = contratos.reduce((acc, c) => acc + Number(c.valor_bruto_mensual), 0)

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#181c20] mb-2 font-['Inter'] antialiased">Relación de Contratos</h1>
          <p className="text-[#434655] max-w-md antialiased">Registre todos sus vínculos contractuales activos para determinar el Ingreso Base de Cotización (IBC).</p>
        </div>
        <button 
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white px-6 py-3 rounded-xl font-bold text-sm shadow-lg shadow-blue-200 hover:scale-105 active:scale-95 transition-all"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          Agregar Contrato
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.1)] border border-blue-50">
          <h3 className="text-lg font-bold mb-4">{editingContratoId ? 'Editar Contrato' : 'Nuevo Contrato'}</h3>
          <form onSubmit={handleGuardarContrato} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="col-span-1 md:col-span-2">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Entidad contratante</label>
              <input 
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.entidad_contratante}
                onChange={e => setForm({...form, entidad_contratante: e.target.value})}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Valor bruto mensual</label>
              <input 
                type="number"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.valor_bruto_mensual}
                onChange={e => setForm({...form, valor_bruto_mensual: e.target.value})}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Nivel ARL</label>
              <select 
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.nivel_arl}
                onChange={e => setForm({...form, nivel_arl: e.target.value as NivelARL})}
              >
                {NIVELES_ARL.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Fecha inicio</label>
              <input 
                type="date"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.fecha_inicio}
                onChange={e => setForm({...form, fecha_inicio: e.target.value})}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Fecha fin (opcional)</label>
              <input 
                type="date"
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.fecha_fin}
                onChange={e => setForm({...form, fecha_fin: e.target.value})}
              />
            </div>
            <div className="col-span-1 md:col-span-2 flex gap-3 mt-2">
              <button type="submit" disabled={saving} className="bg-[#004ac6] text-white px-6 py-2 rounded-lg font-bold text-sm">
                Guardar
              </button>
              <button type="button" onClick={resetForm} className="bg-slate-200 text-slate-600 px-6 py-2 rounded-lg font-bold text-sm">
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {error && <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-lg border border-red-100">{error}</div>}

      {/* Table Card */}
      <div className="bg-white rounded-xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-blue-50/30 border-b border-slate-100">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[#434655]">Entidad</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[#434655]">Valor Bruto (COP)</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[#434655] text-center">Nivel ARL</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-[#434655] text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-6 py-10 text-center text-slate-400 font-bold animate-pulse">Cargando contratos...</td>
                </tr>
              ) : contratos.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-10 text-center text-slate-400 font-medium">No hay contratos registrados.</td>
                </tr>
              ) : (
                contratos.map((c) => (
                  <tr key={c.id} className="hover:bg-blue-50/10 transition-colors">
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                          <span className="material-symbols-outlined text-[#495c95] text-sm">business</span>
                        </div>
                        <span className="font-semibold text-[#181c20]">{c.entidad_contratante}</span>
                      </div>
                    </td>
                    <td className="px-6 py-5 font-medium text-[#181c20]">{formatCOP(c.valor_bruto_mensual)}</td>
                    <td className="px-6 py-5 text-center">
                      <span className="px-3 py-1 rounded-full bg-blue-100 text-[#004ac6] text-xs font-bold uppercase">Nivel {c.nivel_arl}</span>
                    </td>
                    <td className="px-6 py-5 text-right">
                      <button onClick={() => handleEditarContrato(c)} className="material-symbols-outlined text-slate-400 hover:text-[#004ac6] transition-colors p-1">edit</button>
                      <button onClick={() => void handleEliminarContrato(c.id)} className="material-symbols-outlined text-slate-400 hover:text-red-600 transition-colors p-1 ml-2">delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="p-6 bg-slate-50/50 flex justify-between items-center border-t border-slate-100">
          <span className="text-xs font-bold text-[#434655]">TOTAL BRUTO ACUMULADO</span>
          <span className="text-lg font-extrabold text-[#004ac6]">{formatCOP(totalBruto.toString())} COP</span>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4">
        <button onClick={retrocederPaso} className="text-slate-500 font-bold hover:text-slate-700 transition-colors flex items-center gap-2">
          <span className="material-symbols-outlined">arrow_back</span>
          Regresar
        </button>
        <button 
          onClick={avanzarPaso} 
          disabled={contratos.length === 0}
          className="bg-[#004ac6] text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-100 hover:bg-blue-700 disabled:opacity-50 transition-all flex items-center gap-2"
        >
          Continuar
          <span className="material-symbols-outlined">arrow_forward</span>
        </button>
      </div>
    </div>
  )
}
