/**
 * Paso 2 del wizard: Selección del período (año y mes) de liquidación.
 * Llama al engine de cálculo. Si el ingreso requiere decisión de piso,
 * el backend responde con HTTP 422 y requires_piso_decision = true.
 * Ref: HU-02, RF-02, RN-06
 */
import { useState } from 'react'
import axios from 'axios'
import { liquidacionesApi } from '../../api/liquidaciones'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const ANIO_ACTUAL = new Date().getFullYear()
const ANIOS = [ANIO_ACTUAL - 1, ANIO_ACTUAL]

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
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCalcular = async () => {
    if (!perfilId) return
    setError(null)
    setLoading(true)

    // Actualizar el store con el período seleccionado
    setPeriodo(perfilId, anioLocal, mesLocal)

    try {
      const resultado = await liquidacionesApi.calcular({
        perfil_id: perfilId,
        anio: anioLocal,
        mes: mesLocal,
        opcion_piso: 'NO_APLICA',
      })
      // Cálculo exitoso — ir directo al resultado (paso 5)
      setResultado(resultado)
      // Avanzar hasta paso 5 (avanzar 3 pasos: de 2 a 5)
      avanzarPaso() // → 3
      avanzarPaso() // → 4
      avanzarPaso() // → 5
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        const detail = err.response.data?.detail
        // El backend retorna requires_piso_decision: true cuando el ingreso < SMMLV
        if (detail?.requires_piso_decision === true) {
          setRequiereDecisionPiso(true)
          avanzarPaso() // → paso 3 (Piso de Protección Social)
          return
        }
        // Otro error de validación de dominio
        const msg = detail?.message ?? detail ?? 'Error de validación en los datos ingresados.'
        setError(typeof msg === 'string' ? msg : 'Error de validación en los datos ingresados.')
      } else if (axios.isAxiosError(err) && err.response?.status === 409) {
        // Conflicto: liquidación duplicada
        setError('Ya existe una liquidación para este período. Seleccione un período diferente.')
      } else if (axios.isAxiosError(err) && err.response?.status === 404) {
        setError('El perfil seleccionado no fue encontrado. Regrese al paso anterior.')
      } else {
        setError('Error al conectar con el servidor. Verifique su conexión e intente nuevamente.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wizard-step">
      <h2>Elegir Período</h2>
      <p className="step-description">
        Seleccione el año y mes para el cual desea calcular la liquidación:
      </p>

      <div className="periodo-form">
        <div className="field">
          <label htmlFor="anio">Año</label>
          <select
            id="anio"
            value={anioLocal}
            onChange={(e) => setAnioLocal(Number(e.target.value))}
            disabled={loading}
          >
            {ANIOS.map((a) => (
              <option key={a} value={a}>{a}</option>
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
              <option key={idx + 1} value={idx + 1}>{nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="wizard-actions">
        <button
          className="btn-secondary"
          onClick={retrocederPaso}
          disabled={loading}
        >
          Atrás
        </button>
        <button
          className="btn-primary"
          onClick={handleCalcular}
          disabled={loading}
        >
          {loading ? 'Calculando...' : 'Calcular'}
        </button>
      </div>
    </div>
  )
}
