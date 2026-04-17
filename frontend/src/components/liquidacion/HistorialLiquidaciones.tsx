import { useEffect, useState } from 'react'
import { contadorApi } from '../../api/contador'
import { liquidacionesApi } from '../../api/liquidaciones'
import type { HistorialItem, LiquidacionDetalle } from '../../api/liquidaciones'
import { useAuthStore } from '../../store/authStore'
import { ComparacionPeriodos } from './ComparacionPeriodos'

interface HistorialLiquidacionesProps {
  perfilId: string
}

function formatCOP(valor: string): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(valor))
}

function formatPct(valor: string): string {
  return `${(Number(valor) * 100).toFixed(2)}%`
}

function labelEstado(estado: string): string {
  switch (estado) {
    case 'CONFIRMADA':
      return 'Confirmada'
    case 'REVISADA':
      return 'Revisada'
    case 'PENDIENTE_REVISION':
      return 'Pendiente revision'
    case 'PENDIENTE_CONFIRMACION':
      return 'Pendiente confirmacion'
    default:
      return estado
  }
}

export function HistorialLiquidaciones({ perfilId }: HistorialLiquidacionesProps) {
  const rol = useAuthStore((s) => s.rol)
  const [historial, setHistorial] = useState<HistorialItem[]>([])
  const [detalle, setDetalle] = useState<LiquidacionDetalle | null>(null)
  const [loading, setLoading] = useState(true)
  const [detalleLoading, setDetalleLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notaRevision, setNotaRevision] = useState('')
  const [aprobada, setAprobada] = useState(true)
  const [reviewMessage, setReviewMessage] = useState<string | null>(null)
  const [confirmando, setConfirmando] = useState(false)

  useEffect(() => {
    let active = true

    const cargar = async () => {
      setLoading(true)
      setError(null)
      setDetalle(null)
      try {
        const data = await liquidacionesApi.historial(perfilId)
        if (!active) return
        setHistorial(data)
      } catch {
        if (!active) return
        setError('No se pudo cargar el historial de liquidaciones.')
      } finally {
        if (active) setLoading(false)
      }
    }

    void cargar()
    return () => {
      active = false
    }
  }, [perfilId])

  const abrirDetalle = async (liquidacionId: string) => {
    setDetalleLoading(true)
    setError(null)
    setReviewMessage(null)
    try {
      const data = await liquidacionesApi.obtenerDetalle(liquidacionId)
      setDetalle(data)
      setNotaRevision(data.revision?.nota ?? '')
      setAprobada(data.revision?.aprobada ?? true)
    } catch {
      setError('No se pudo cargar el detalle historico de la liquidacion.')
    } finally {
      setDetalleLoading(false)
    }
  }

  const guardarRevision = async () => {
    if (!detalle) return
    setReviewMessage(null)
    try {
      const response = await contadorApi.revisarLiquidacion({
        liquidacion_id: detalle.id,
        nota: notaRevision,
        aprobada,
      })
      setReviewMessage(response.message)
      await abrirDetalle(detalle.id)
    } catch {
      setReviewMessage('No se pudo guardar la revision del contador.')
    }
  }

  const confirmarLiquidacion = async () => {
    if (!detalle) return
    setConfirmando(true)
    setReviewMessage(null)
    try {
      const response = await liquidacionesApi.confirmar(detalle.id)
      setReviewMessage(response.message)
      await abrirDetalle(detalle.id)
    } catch {
      setReviewMessage('No se pudo confirmar la liquidacion.')
    } finally {
      setConfirmando(false)
    }
  }

  return (
    <section className="historial-panel">
      <h3>Historial del perfil</h3>
      {loading ? (
        <div className="loading-state">Cargando historial...</div>
      ) : historial.length === 0 ? (
        <p className="nota-neto">Este perfil todavia no tiene liquidaciones registradas.</p>
      ) : (
        <div className="historial-lista">
          {historial.map((item) => (
            <button
              key={item.id}
              type="button"
              className="card historial-item"
              onClick={() => void abrirDetalle(item.id)}
            >
              <strong>{item.periodo}</strong>
              <span className={`estado-badge estado-${item.estado_proceso.toLowerCase()}`}>
                {labelEstado(item.estado_proceso)}
              </span>
              <span>IBC: {formatCOP(item.ibc)}</span>
              <span>Aportes: {formatCOP(item.total_aportes)}</span>
              <span>Retencion: {formatCOP(item.retencion_fuente)}</span>
            </button>
          ))}
        </div>
      )}

      {historial.length >= 2 && (
        <ComparacionPeriodos
          perfilId={perfilId}
          periodos={historial.map((l) => l.periodo)}
        />
      )}

      {error && <div className="error-banner">{error}</div>}

      {detalleLoading && <div className="loading-state">Cargando detalle historico...</div>}

      {detalle && !detalleLoading && (
        <div className="detalle-historico">
          <h4>Detalle de {detalle.periodo}</h4>
          <div className={`estado-badge estado-${detalle.estado_proceso.toLowerCase()}`}>
            {labelEstado(detalle.estado_proceso)}
          </div>
          <div className="resumen-tabla-wrapper">
            <table className="resumen-tabla">
              <tbody>
                <tr>
                  <td>Ingreso bruto total</td>
                  <td className="valor">{formatCOP(detalle.ingreso_bruto_total)}</td>
                </tr>
                <tr>
                  <td>Costos presuntos</td>
                  <td className="valor">{formatCOP(detalle.costos_presuntos)}</td>
                </tr>
                <tr>
                  <td>Porcentaje costos presuntos</td>
                  <td className="valor">{formatPct(detalle.pct_costos_presuntos)}</td>
                </tr>
                <tr>
                  <td>Base 40%</td>
                  <td className="valor">{formatCOP(detalle.base_40_pct)}</td>
                </tr>
                <tr>
                  <td>IBC</td>
                  <td className="valor">{formatCOP(detalle.ibc)}</td>
                </tr>
                <tr>
                  <td>Total aportes</td>
                  <td className="valor">{formatCOP(detalle.total_aportes)}</td>
                </tr>
                <tr>
                  <td>Retencion</td>
                  <td className="valor">{formatCOP(detalle.retencion_fuente)}</td>
                </tr>
                <tr>
                  <td>Neto estimado</td>
                  <td className="valor">{formatCOP(detalle.neto_estimado)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="snapshot-grid">
            <div className="snapshot-card">
              <h5>Snapshot normativo</h5>
              <p>Vigencia: {detalle.snapshot_normativo.vigencia_anio}</p>
              <p>SMMLV: {formatCOP(detalle.snapshot_normativo.smmlv)}</p>
              <p>UVT: {formatCOP(detalle.snapshot_normativo.uvt)}</p>
              <p>Salud: {formatPct(detalle.snapshot_normativo.pct_salud)}</p>
              <p>Pension: {formatPct(detalle.snapshot_normativo.pct_pension)}</p>
            </div>
            <div className="snapshot-card">
              <h5>Tarifas y trazabilidad</h5>
              <p>ARL aplicada: Nivel {detalle.nivel_arl_aplicado}</p>
              <p>Generado en: {new Date(detalle.generado_en).toLocaleString('es-CO')}</p>
              <p>Piso: {detalle.opcion_piso_proteccion}</p>
              <p>Tarifa ARL I: {formatPct(detalle.snapshot_normativo.tarifas_arl.I ?? '0')}</p>
              <p>Tarifa ARL V: {formatPct(detalle.snapshot_normativo.tarifas_arl.V ?? '0')}</p>
            </div>
          </div>

          {detalle.revision && (
            <div className="snapshot-card review-card">
              <h5>Revision registrada</h5>
              <p>Estado: {detalle.revision.aprobada ? 'Aprobada' : 'Con observaciones'}</p>
              <p>Nota: {detalle.revision.nota}</p>
              <p>Fecha: {new Date(detalle.revision.revisado_en).toLocaleString('es-CO')}</p>
            </div>
          )}

          {rol !== 'CONTADOR' && (
            <div className="snapshot-card review-card">
              <h5>Confirmacion del contratista</h5>
              {detalle.confirmacion ? (
                <p>Confirmada el {new Date(detalle.confirmacion.confirmado_en).toLocaleString('es-CO')}</p>
              ) : detalle.puede_confirmar ? (
                <>
                  <p>La liquidacion ya puede ser confirmada por el contratista.</p>
                  <div className="wizard-actions">
                    <button
                      className="btn-secondary"
                      onClick={() => void confirmarLiquidacion()}
                      disabled={confirmando}
                    >
                      {confirmando ? 'Confirmando...' : 'Confirmar liquidacion'}
                    </button>
                  </div>
                </>
              ) : (
                <p>La liquidacion esta pendiente de revision del contador antes de la confirmacion final.</p>
              )}
            </div>
          )}

          {rol === 'CONTADOR' && (
            <div className="snapshot-card review-card">
              <h5>Registrar revision</h5>
              <textarea
                className="review-textarea"
                value={notaRevision}
                onChange={(e) => setNotaRevision(e.target.value)}
                placeholder="Escriba la observacion o aprobacion de la liquidacion"
              />
              <label className="checkbox-inline">
                <input
                  type="checkbox"
                  checked={aprobada}
                  onChange={(e) => setAprobada(e.target.checked)}
                />
                Marcar como aprobada
              </label>
              <div className="wizard-actions">
                <button className="btn-secondary" onClick={() => void guardarRevision()}>
                  Guardar revision
                </button>
              </div>
              {reviewMessage && <div className="aviso-tope">{reviewMessage}</div>}
            </div>
          )}
        </div>
      )}
    </section>
  )
}
