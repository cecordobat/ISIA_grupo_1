import { useEffect, useState } from 'react'
import axios from 'axios'
import { liquidacionesApi } from '../../api/liquidaciones'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

export function StepSeleccionarPeriodo() {
  const {
    perfilId,
    anio,
    mes,
    setPeriodo,
    setResultado,
    setRequiereDecisionPiso,
    avanzarPaso,
    retrocederPaso,
  } = useLiquidacionStore()

  const [anioLocal, setAnioLocal] = useState(anio)
  const [mesLocal, setMesLocal] = useState(mes)
  const [aniosDisponibles, setAniosDisponibles] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingAnios, setLoadingAnios] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const cargarAnios = async () => {
      setLoadingAnios(true)
      try {
        const anios = await liquidacionesApi.aniosDisponibles()
        setAniosDisponibles(anios)
        if (anios.length > 0 && !anios.includes(anioLocal)) {
          setAnioLocal(anios[0])
        }
      } catch {
        setError('Error al cargar periodos.')
      } finally {
        setLoadingAnios(false)
      }
    }
    void cargarAnios()
  }, [])

  const handleCalcular = async () => {
    if (!perfilId) return
    setError(null)
    setLoading(true)
    setPeriodo(perfilId, anioLocal, mesLocal)

    try {
      const resultado = await liquidacionesApi.calcular({
        perfil_id: perfilId,
        anio: anioLocal,
        mes: mesLocal,
        opcion_piso: 'NO_APLICA',
      })
      setResultado(resultado)
      avanzarPaso(); avanzarPaso(); avanzarPaso();
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        const detail = err.response.data?.detail
        if (detail?.requires_piso_decision === true) {
          setRequiereDecisionPiso(true)
          avanzarPaso()
          return
        }
        setError(detail?.message ?? 'Error de validación.')
      } else {
        setError('Error al conectar con el servidor.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 antialiased font-['Inter']">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-[#181c20] mb-2">Selección de Periodo</h1>
        <p className="text-[#434655]">Indique el mes y año que desea reportar ante la UGPP.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col md:flex-row gap-6">
        <div className="flex-grow">
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Año de Vigencia</label>
          <select 
            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-bold text-lg"
            value={anioLocal}
            onChange={e => setAnioLocal(Number(e.target.value))}
            disabled={loading || loadingAnios}
          >
            {aniosDisponibles.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div className="flex-grow">
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Mes de Liquidación</label>
          <select 
            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-bold text-lg"
            value={mesLocal}
            onChange={e => setMesLocal(Number(e.target.value))}
            disabled={loading}
          >
            {MESES.map((n, i) => <option key={i+1} value={i+1}>{n}</option>)}
          </select>
        </div>
      </div>

      {error && <p className="text-red-600 text-sm font-medium">{error}</p>}

      <div className="flex justify-between items-center pt-4">
        <button onClick={retrocederPaso} className="text-slate-500 font-bold hover:text-slate-700 transition-colors flex items-center gap-2">
          <span className="material-symbols-outlined">arrow_back</span>
          Regresar
        </button>
        <button 
          onClick={handleCalcular} 
          disabled={loading || loadingAnios || aniosDisponibles.length === 0}
          className="bg-[#004ac6] text-white px-10 py-3 rounded-xl font-bold shadow-lg shadow-blue-100 hover:bg-blue-700 disabled:opacity-50 transition-all flex items-center gap-2"
        >
          {loading ? 'Procesando...' : 'Iniciar Cálculo'}
          <span className="material-symbols-outlined">calculate</span>
        </button>
      </div>
    </div>
  )
}
