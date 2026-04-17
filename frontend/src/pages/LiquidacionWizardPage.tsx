import { useState } from 'react'
import axios from 'axios'
import { useLiquidacionStore } from '../store/liquidacionStore'
import { liquidacionesApi } from '../api/liquidaciones'
import { StepSeleccionarPerfil } from '../components/liquidacion/StepSeleccionarPerfil'
import { StepGestionContratos } from '../components/liquidacion/StepGestionContratos'
import { StepSeleccionarPeriodo } from '../components/liquidacion/StepSeleccionarPeriodo'
import { StepPisoProteccion } from '../components/liquidacion/StepPisoProteccion'
import { ResumenLiquidacion } from '../components/liquidacion/ResumenLiquidacion'
import { Layout } from '../components/layout/Layout'
import '../styles/wizard.css'

const STEP_LABELS = ['Perfil', 'Contratos', 'Periodo', 'Cálculo']

export function LiquidacionWizardPage() {
  const {
    paso,
    perfilId,
    anio,
    mes,
    opcionPiso,
    resultado,
    setOpcionPiso,
    setResultado,
    avanzarPaso,
    resetear,
  } = useLiquidacionStore()

  const [pisoCargando, setPisoCargando] = useState(false)
  const [pisoError, setPisoError] = useState<string | null>(null)

  // Map internal 6 steps to UI 4 steps
  const uiPaso = paso <= 3 ? paso : 4

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
      avanzarPaso() // To 5
      avanzarPaso() // To 6
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response) {
        const detail = err.response.data?.detail
        const msg = typeof detail === 'string' ? detail : detail?.message ?? 'Error al calcular'
        setPisoError(msg)
      } else {
        setPisoError('Error al conectar con el servidor.')
      }
    } finally {
      setPisoCargando(false)
    }
  }

  const renderPaso = () => {
    switch (paso) {
      case 1: return <StepSeleccionarPerfil />
      case 2: return <StepGestionContratos />
      case 3: return <StepSeleccionarPeriodo />
      case 4:
        return (
          <div className="premium-card">
            {pisoError && <div className="error-banner">{pisoError}</div>}
            <StepPisoProteccion
              opcionSeleccionada={opcionPiso}
              onSelectOpcion={(o) => { setPisoError(null); setOpcionPiso(o); }}
              onConfirmar={handleConfirmarPiso}
            />
            {pisoCargando && <div className="loading-state">Calculando aportes...</div>}
          </div>
        )
      case 5:
        return (
          <div className="premium-card calculando-state">
            <div className="spinner" />
            <p>Procesando su liquidación...</p>
          </div>
        )
      case 6:
        return resultado ? (
          <ResumenLiquidacion resultado={resultado} onNuevaLiquidacion={resetear} />
        ) : (
          <div className="premium-card">
            <p>Error en la liquidación.</p>
            <button className="btn-primary" onClick={resetear}>Reiniciar</button>
          </div>
        )
      default: return null
    }
  }

  return (
    <Layout currentStep={uiPaso} totalSteps={4} stepLabels={STEP_LABELS}>
      {renderPaso()}
    </Layout>
  )
}
