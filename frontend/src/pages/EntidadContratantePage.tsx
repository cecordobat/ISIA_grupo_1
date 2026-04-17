import { useState } from 'react'
import { entidadContratanteApi } from '../api/entidad_contratante'
import type { EstadoCumplimiento } from '../api/entidad_contratante'

const COLOR_ESTADO: Record<string, string> = {
  CONFIRMADA: '#22c55e',
  PENDIENTE_CONFIRMACION: '#f97316',
  SIN_LIQUIDACIONES: '#94a3b8',
}

export function EntidadContratantePage() {
  const [perfilId, setPerfilId] = useState('')
  const [resultado, setResultado] = useState<EstadoCumplimiento | null>(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function handleVerificar(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setResultado(null)
    setCargando(true)
    try {
      const res = await entidadContratanteApi.verificarCumplimiento(perfilId)
      setResultado(res)
    } catch {
      setError('No tienes acceso a este perfil o el perfil no existe.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="wizard-container">
      <h1>Verificación de Cumplimiento</h1>
      <p className="nota-neto">
        Consulta el estado de cumplimiento de un contratista que te ha autorizado el acceso.
      </p>

      <form onSubmit={(e) => void handleVerificar(e)} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <label>
          ID del perfil del contratista
          <input
            type="text"
            value={perfilId}
            onChange={(e) => setPerfilId(e.target.value)}
            placeholder="UUID del perfil"
            style={{ marginTop: '0.25rem' }}
          />
        </label>
        {error && <div className="aviso-tope">{error}</div>}
        <div className="wizard-actions">
          <button type="submit" className="btn-secondary" disabled={!perfilId || cargando}>
            {cargando ? 'Consultando...' : 'Verificar cumplimiento'}
          </button>
        </div>
      </form>

      {resultado && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h2>Estado de cumplimiento</h2>
          <table className="resumen-tabla">
            <tbody>
              <tr>
                <td>Contratista</td>
                <td className="valor">{resultado.nombre_contratista}</td>
              </tr>
              <tr>
                <td>Documento</td>
                <td className="valor">{resultado.documento}</td>
              </tr>
              <tr>
                <td>Período más reciente</td>
                <td className="valor">{resultado.periodo_reciente ?? 'Sin liquidaciones'}</td>
              </tr>
              <tr>
                <td>Estado</td>
                <td className="valor" style={{ color: COLOR_ESTADO[resultado.estado], fontWeight: 700 }}>
                  {resultado.estado.replace(/_/g, ' ')}
                </td>
              </tr>
            </tbody>
          </table>
          {resultado.tiene_liquidacion_confirmada && (
            <p style={{ color: COLOR_ESTADO.CONFIRMADA, marginTop: '0.75rem' }}>
              El contratista tiene una liquidación confirmada para el período más reciente.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
