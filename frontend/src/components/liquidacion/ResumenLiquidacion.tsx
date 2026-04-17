import { useState } from 'react'
import { liquidacionesApi } from '../../api/liquidaciones'
import type { LiquidacionResponse } from '../../api/liquidaciones'

interface ResumenLiquidacionProps {
  resultado: LiquidacionResponse
  onNuevaLiquidacion: () => void
}

function formatCOP(valor: string | number): string {
  const v = typeof valor === 'string' ? parseFloat(valor) : valor
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v)
}

function formatPct(valor: string | number): string {
  const v = typeof valor === 'string' ? parseFloat(valor) : valor
  return `${(v * 100).toFixed(2)}%`
}

export function ResumenLiquidacion({ resultado, onNuevaLiquidacion }: ResumenLiquidacionProps) {
  const esBEPS = resultado.opcion_piso_proteccion === 'BEPS'
  const [confirmada, setConfirmada] = useState(Boolean(resultado.confirmacion))
  const [mensaje, setMensaje] = useState<string | null>(null)
  const [confirmando, setConfirmando] = useState(false)

  const handleDescargarPdf = async () => {
    try {
      const blob = await liquidacionesApi.descargarPdf(resultado.liquidacion_id)
      const url = window.URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `liquidacion_${resultado.periodo}.pdf`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      setMensaje('Debe confirmar la liquidación antes de descargar el PDF.')
    }
  }

  const handleConfirmar = async () => {
    setConfirmando(true)
    setMensaje(null)
    try {
      const response = await liquidacionesApi.confirmar(resultado.liquidacion_id)
      setConfirmada(true)
      setMensaje(response.message)
    } catch {
      setMensaje('No fue posible confirmar la liquidación.')
    } finally {
      setConfirmando(false)
    }
  }

  return (
    <div className="space-y-8 pb-10 antialiased font-['Inter']">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#181c20]">Reporte de Liquidación</h1>
          <p className="text-[#434655]">Periodo: <span className="font-bold text-[#004ac6]">{resultado.periodo}</span></p>
        </div>
        <div className={`px-4 py-2 rounded-full font-bold text-xs uppercase tracking-widest ${confirmada ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
          {confirmada ? 'Confirmada ✅' : 'En Borrador ⏳'}
        </div>
      </div>

      {resultado.ajustado_por_tope && (
        <div className="bg-blue-50 border-l-4 border-blue-600 p-4 text-sm text-blue-800 flex items-center gap-3">
          <span className="material-symbols-outlined">info</span>
          Su IBC fue ajustado automáticamente por el tope legal [1 - 25 SMMLV].
        </div>
      )}

      {/* Main Result Card */}
      <div className="bg-gradient-to-br from-green-50/50 to-white p-8 rounded-2xl shadow-[0_20px_40px_-10px_rgba(22,101,52,0.08)] border border-green-100/50 text-center">
        <h3 className="text-xs font-bold text-green-800 uppercase tracking-widest mb-2">5. Neto Estimado a Recibir</h3>
        <div className="text-5xl md:text-6xl font-black text-green-700 tracking-tighter">
          {formatCOP(resultado.neto_estimado)}
        </div>
        <p className="text-slate-400 text-xs mt-4">Calculado según reglamentación vigente Decreto Nacional 1601 de 2022.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* IBC Details */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <h3 className="font-bold flex items-center gap-2 text-[#181c20] mb-4 border-b border-slate-50 pb-2">
            <span className="material-symbols-outlined text-[#004ac6] text-lg">finance_chip</span>
            Detalle del IBC
          </h3>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between"><span className="text-slate-500">Ingreso Bruto Total</span> <span className="font-semibold">{formatCOP(resultado.ingreso_bruto_total)}</span></li>
            <li className="flex justify-between"><span className="text-slate-500">Costos Presuntos ({formatPct(resultado.pct_costos_presuntos)})</span> <span className="font-semibold">{formatCOP(resultado.costos_presuntos)}</span></li>
            <li className="flex justify-between pt-2 border-t border-slate-50"><span className="font-bold text-[#181c20]">IBC Resultante</span> <span className="font-black text-[#004ac6]">{formatCOP(resultado.ibc)}</span></li>
          </ul>
        </div>

        {/* Security Social */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <h3 className="font-bold flex items-center gap-2 text-[#181c20] mb-4 border-b border-slate-50 pb-2">
            <span className="material-symbols-outlined text-[#004ac6] text-lg">safety_check</span>
            Seguridad Social
          </h3>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between">
              <span className="text-slate-500">{esBEPS ? 'Aporte BEPS (15%)' : 'Pensión (16%)'}</span> 
              <span className="font-semibold text-red-600">-{formatCOP(resultado.aporte_pension)}</span>
            </li>
            <li className="flex justify-between">
              <span className="text-slate-500">Salud (12.5%)</span> 
              <span className="font-semibold text-red-600">-{formatCOP(resultado.aporte_salud)}</span>
            </li>
            <li className="flex justify-between">
              <span className="text-slate-500">ARL (Nivel {resultado.nivel_arl_aplicado})</span> 
              <span className="font-semibold text-red-600">-{formatCOP(resultado.aporte_arl)}</span>
            </li>
            <li className="flex justify-between pt-2 border-t border-slate-50"><span className="font-bold">Total Aportes</span> <span className="font-black">-{formatCOP(resultado.total_aportes)}</span></li>
          </ul>
        </div>
      </div>

      {/* Snapshot and Disclaimer */}
      <div className="bg-slate-50 p-6 rounded-xl text-left">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">6. Datos de Referencia (Vigencia {resultado.snapshot_normativo.vigencia_anio})</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div><p className="text-slate-400">SMMLV</p><p className="font-bold">{formatCOP(resultado.snapshot_normativo.smmlv)}</p></div>
          <div><p className="text-slate-400">UVT</p><p className="font-bold">{formatCOP(resultado.snapshot_normativo.uvt)}</p></div>
          <div><p className="text-slate-400">% Salud</p><p className="font-bold">{formatPct(resultado.snapshot_normativo.pct_salud)}</p></div>
          <div><p className="text-slate-400">% Pensión</p><p className="font-bold">{formatPct(resultado.snapshot_normativo.pct_pension)}</p></div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 pt-4 border-t border-slate-100">
        <button 
          className="flex-grow md:flex-none px-8 py-3 bg-[#004ac6] text-white rounded-xl font-bold shadow-lg shadow-blue-100 hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
          onClick={onNuevaLiquidacion}
        >
          <span className="material-symbols-outlined">restart_alt</span>
          Nueva Liquidación
        </button>
        <button 
          className="flex-grow md:flex-none px-8 py-3 bg-white text-[#181c20] border border-slate-200 rounded-xl font-bold hover:bg-slate-50 disabled:opacity-50 transition-all"
          onClick={handleConfirmar}
          disabled={confirmada || confirmando}
        >
          {confirmada ? 'Confirmado' : 'Confirmar Liquidación'}
        </button>
        <button 
          className="flex-grow md:flex-none px-8 py-3 bg-white text-[#181c20] border border-slate-200 rounded-xl font-bold hover:bg-slate-50 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
          onClick={handleDescargarPdf}
          disabled={!confirmada}
        >
          <span className="material-symbols-outlined">picture_as_pdf</span>
          Descargar PDF
        </button>
      </div>

      {mensaje && <p className="text-center text-xs text-blue-600 font-medium">{mensaje}</p>}

      <p className="text-[10px] text-slate-400 text-center leading-relaxed max-w-2xl mx-auto">
        <strong>Aviso legal:</strong> Esta herramienta es de carácter informativo. Debe verificar estos valores en su operador PILA. 
        El "Motor de Cumplimiento" no sustituye la obligación de reporte ante las entidades de seguridad social.
      </p>
    </div>
  )
}
