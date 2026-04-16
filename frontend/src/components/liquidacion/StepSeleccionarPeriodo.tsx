import { useEffect, useState } from 'react'
import axios from 'axios'
import { liquidacionesApi } from '../../api/liquidaciones'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const MESES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
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
    let activo = true
    const cargarAnios = async () => {
      setLoadingAnios(true)
      try {
        const anios = await liquidacionesApi.aniosDisponibles()
        if (!activo) return
        setAniosDisponibles(anios)
        if (anios.length > 0 && !anios.includes(anioLocal)) {
          setAnioLocal(anios[0])
        }
      } catch {
        if (!activo) return
        setError('No fue posible cargar los periodos disponibles para liquidacion.')
      } finally {
        if (activo) setLoadingAnios(false)
      }
    }
    void cargarAnios()
    return () => {
      activo = false
    }
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
      avanzarPaso()
      avanzarPaso()
      avanzarPaso()
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        const detail = err.response.data?.detail
        if (detail?.requires_piso_decision === true) {
          setRequiereDecisionPiso(true)
          avanzarPaso()
          return
        }
        const msg = detail?.message ?? detail ?? 'Error de validacion en los datos ingresados.'
        setError(typeof msg === 'string' ? msg : 'Error de validacion en los datos ingresados.')
      } else if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError('Ya existe una liquidacion para este periodo. Seleccione un periodo diferente.')
      } else if (axios.isAxiosError(err) && err.response?.status === 404) {
        setError('El perfil seleccionado no fue encontrado. Regrese al paso anterior.')
      } else if (axios.isAxiosError(err) && err.response?.status === 400) {
        const detail = err.response.data?.detail
        setError(typeof detail === 'string' ? detail : 'No hay parametros normativos para el periodo seleccionado.')
      } else {
        setError('Error al conectar con el servidor. Verifique su conexion e intente nuevamente.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wizard-step">
      <h2>Elegir Periodo</h2>
      <p className="step-description">
        Seleccione el ano y mes para el cual desea calcular la liquidacion:
      </p>

      <div className="periodo-form">
        <div className="field">
          <label htmlFor="anio">Ano</label>
          <select
            id="anio"
            value={anioLocal}
            onChange={(e) => setAnioLocal(Number(e.target.value))}
            disabled={loading || loadingAnios || aniosDisponibles.length === 0}
          >
            {aniosDisponibles.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="mes">Mes</label>
          <select
            id="mes"
            value={mesLocal}
            onChange={(e) => setMesLocal(Number(e.target.value))}
            disabled={loading}
          >
            {MESES.map((nombre, idx) => (
              <option key={idx + 1} value={idx + 1}>
                {nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="wizard-actions">
        <button className="btn-secondary" onClick={retrocederPaso} disabled={loading}>
          Atras
        </button>
        <button
          className="btn-primary"
          onClick={handleCalcular}
          disabled={loading || loadingAnios || aniosDisponibles.length === 0}
        >
          {loading ? 'Calculando...' : 'Calcular'}
        </button>
      </div>
    </div>
  )
}
