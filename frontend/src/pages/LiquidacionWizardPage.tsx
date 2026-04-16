/**
 * Página principal del wizard de liquidación.
 * Orquesta los 5 pasos: perfil → período → piso → calculando → resultado.
 * Ref: HU-01 a HU-07, RF-01 a RF-08
 */
import { useState } from 'react'
import axios from 'axios'
import { useLiquidacionStore } from '../store/liquidacionStore'
import { useAuthStore } from '../store/authStore'
import { liquidacionesApi } from '../api/liquidaciones'
import { StepSeleccionarPerfil } from '../components/liquidacion/StepSeleccionarPerfil'
import { StepSeleccionarPeriodo } from '../components/liquidacion/StepSeleccionarPeriodo'
import { StepPisoProteccion } from '../components/liquidacion/StepPisoProteccion'
import { ResumenLiquidacion } from '../components/liquidacion/ResumenLiquidacion'
import '../styles/wizard.css'

const NOMBRES_PASO: Record<number, string> = {
  1: 'Seleccionar perfil',
  2: 'Elegir período',
  3: 'Piso de Protección Social',
  4: 'Calculando...',
  5: 'Resultado',
}

const TOTAL_PASOS = 5

export function LiquidacionWizardPage() {
  const { paso, perfilId, anio, mes, opcionPiso, resultado, setOpcionPiso, setResultado, avanzarPaso, resetear } =
    useLiquidacionStore()
  const logout = useAuthStore((s) => s.logout)

  const [pisoCargando, setPisoCargando] = useState(false)
  const [pisoError, setPisoError] = useState<string | null>(null)

  const handleConfirmarPiso = async () => {
    if (!perfilId || !opcionPiso) return
    setPisoError(null)
    setPisoCargando(true)

    try {
      const resultado = await liquidacionesApi.calcular({
        perfil_id: perfilId,
        anio,
        mes,
        opcion_piso: opcionPiso,
      })
      setResultado(resultado)
      avanzarPaso() // → paso 4
      avanzarPaso() // → paso 5
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response) {
        const detail = err.response.data?.detail
        const msg = typeof detail === 'string'
          ? detail
          : detail?.message ?? 'Error al calcular la liquidación. Intente nuevamente.'
        setPisoError(msg)
      } else {
        setPisoError('Error al conectar con el servidor. Verifique su conexión e intente nuevamente.')
      }
    } finally {
      setPisoCargando(false)
    }
  }

  const renderPaso = () => {
    switch (paso) {
      case 1:
        return <StepSeleccionarPerfil />

      case 2:
        return <StepSeleccionarPeriodo />

      case 3:
        return (
          <div>
            {pisoError && <div className="error-banner">{pisoError}</div>}
            <StepPisoProteccion
              opcionSeleccionada={opcionPiso}
              onSelectOpcion={(o) => {
                setPisoError(null)
                setOpcionPiso(o)
              }}
              onConfirmar={handleConfirmarPiso}
            />
            {pisoCargando && (
              <div className="loading-state" style={{ marginTop: '1rem' }}>
                Calculando aportes...
              </div>
            )}
          </div>
        )

      case 4:
        return (
          <div className="wizard-step calculando-state">
            <div className="spinner" />
            <p>Procesando su liquidación, por favor espere...</p>
          </div>
        )

      case 5:
        if (!resultado) {
          return (
            <div className="wizard-step">
              <div className="error-banner">
                No se encontró el resultado de la liquidación. Por favor, inicie una nueva liquidación.
              </div>
              <button className="btn-primary" onClick={resetear}>
                Nueva Liquidación
              </button>
            </div>
          )
        }
        return <ResumenLiquidacion resultado={resultado} onNuevaLiquidacion={resetear} />

      default:
        return null
    }
  }

  return (
    <div className="wizard-container">
      <div className="wizard-header">
        <h1>Motor de Cumplimiento — Colombia</h1>
        <button className="btn-logout" onClick={logout}>
          Cerrar sesión
        </button>
      </div>

      <div className="step-indicator">
        <strong>Paso {paso} de {TOTAL_PASOS}</strong> — {NOMBRES_PASO[paso]}
      </div>

      {renderPaso()}
    </div>
  )
}
