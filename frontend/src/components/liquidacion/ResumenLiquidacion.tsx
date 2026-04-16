import { useState } from 'react'
import { liquidacionesApi } from '../../api/liquidaciones'
import type { LiquidacionResponse } from '../../api/liquidaciones'

interface ResumenLiquidacionProps {
  resultado: LiquidacionResponse
  onNuevaLiquidacion: () => void
}

function formatCOP(valor: string): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(parseFloat(valor))
}

function formatPct(valor: string): string {
  return `${(Number(valor) * 100).toFixed(2)}%`
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
      setMensaje('Debe confirmar la liquidacion antes de descargar el PDF.')
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
      setMensaje(
        resultado.requiere_revision_contador
          ? 'Esta liquidacion requiere revision del contador antes de ser confirmada.'
          : 'No fue posible confirmar la liquidacion.'
      )
    } finally {
      setConfirmando(false)
    }
  }

  return (
    <div className="wizard-step resumen">
      <h2>Pre-Liquidacion - {resultado.periodo}</h2>

      {resultado.ajustado_por_tope && (
        <div className="aviso-tope">
          Su IBC fue ajustado automaticamente por el tope legal [1 SMMLV - 25 SMMLV].
        </div>
      )}

      {resultado.requiere_revision_contador && !resultado.revision && !confirmada && (
        <div className="aviso-requerido">
          Este perfil tiene contador vinculado. La liquidacion queda pendiente de revision antes de la confirmacion final del contratista.
        </div>
      )}

      {confirmada && (
        <div className="aviso-tope">
          La liquidacion ya fue confirmada por el contratista.
        </div>
      )}

      <section className="resumen-seccion">
        <h3>1. Detalle del IBC</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Ingreso bruto total del periodo</td>
              <td className="valor">{formatCOP(resultado.ingreso_bruto_total)}</td>
            </tr>
            <tr>
              <td>Costos presuntos aplicados</td>
              <td className="valor">{formatCOP(resultado.costos_presuntos)}</td>
            </tr>
            <tr>
              <td>Porcentaje de costos presuntos (CIIU)</td>
              <td className="valor">{formatPct(resultado.pct_costos_presuntos)}</td>
            </tr>
            <tr>
              <td>Base despues de costos y regla del 40%</td>
              <td className="valor">{formatCOP(resultado.base_40_pct)}</td>
            </tr>
            <tr className="fila-destacada">
              <td><strong>IBC resultante</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.ibc)}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="resumen-seccion">
        <h3>2. Contratos considerados</h3>
        <div className="historial-lista">
          {resultado.contratos_considerados.map((contrato) => (
            <div key={contrato.contrato_id} className="card historial-item static-card">
              <strong>{contrato.entidad_contratante}</strong>
              <span>Valor mensual: {formatCOP(contrato.valor_bruto_mensual)}</span>
              <span>Dias cotizados: {contrato.dias_cotizados}</span>
              <span>Ingreso proporcional: {formatCOP(contrato.ingreso_bruto_proporcional)}</span>
              <span>ARL: {contrato.nivel_arl}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="resumen-seccion">
        <h3>3. Aportes al Sistema de Seguridad Social</h3>
        {esBEPS ? (
          <div className="beps-aviso">
            Usted eligio el Piso de Proteccion Social (BEPS). El aporte del 15% va a ahorro programado
            y no acumula semanas de pension.
          </div>
        ) : null}
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Salud {esBEPS ? '(no aplica en BEPS)' : '(12.5% del IBC)'}</td>
              <td className="valor">{formatCOP(resultado.aporte_salud)}</td>
            </tr>
            <tr>
              <td>{esBEPS ? 'BEPS (15% del ingreso bruto)' : 'Pension (16% del IBC)'}</td>
              <td className="valor">{formatCOP(resultado.aporte_pension)}</td>
            </tr>
            <tr>
              <td>ARL - Nivel {resultado.nivel_arl_aplicado}</td>
              <td className="valor">{formatCOP(resultado.aporte_arl)}</td>
            </tr>
            <tr>
              <td>Tarifa ARL aplicada</td>
              <td className="valor">{formatPct(resultado.tarifa_arl_aplicada)}</td>
            </tr>
            <tr className="fila-total">
              <td><strong>Total aportes</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.total_aportes)}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="resumen-seccion">
        <h3>4. Retencion en la Fuente</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Base gravable depurada</td>
              <td className="valor">{formatCOP(resultado.base_gravable_retencion)}</td>
            </tr>
            <tr className="fila-total">
              <td><strong>Retencion estimada</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.retencion_fuente)}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="resumen-seccion neto-section">
        <h3>5. Neto Estimado a Recibir</h3>
        <div className="neto-valor">{formatCOP(resultado.neto_estimado)}</div>
      </section>

      <section className="resumen-seccion">
        <h3>6. Snapshot normativo usado</h3>
        <div className="snapshot-grid">
          <div className="snapshot-card">
            <p>Vigencia: {resultado.snapshot_normativo.vigencia_anio}</p>
            <p>SMMLV: {formatCOP(resultado.snapshot_normativo.smmlv)}</p>
            <p>UVT: {formatCOP(resultado.snapshot_normativo.uvt)}</p>
          </div>
          <div className="snapshot-card">
            <p>Salud: {formatPct(resultado.snapshot_normativo.pct_salud)}</p>
            <p>Pension: {formatPct(resultado.snapshot_normativo.pct_pension)}</p>
            <p>Costos presuntos CIIU: {formatPct(resultado.snapshot_normativo.pct_costos_presuntos)}</p>
          </div>
        </div>
      </section>

      {resultado.revision && (
        <section className="resumen-seccion">
          <h3>7. Revision del contador</h3>
          <div className="snapshot-card">
            <p>Estado: {resultado.revision.aprobada ? 'Aprobada' : 'Con observaciones'}</p>
            <p>Nota: {resultado.revision.nota}</p>
          </div>
        </section>
      )}

      <div className="acciones-resumen">
        <button className="btn-secondary" onClick={() => void handleDescargarPdf()} disabled={!confirmada}>
          Descargar PDF
        </button>
        <button
          className="btn-secondary"
          onClick={() => void handleConfirmar()}
          disabled={confirmada || !resultado.puede_confirmar || confirmando}
        >
          {confirmada ? 'Liquidacion confirmada' : confirmando ? 'Confirmando...' : 'Confirmar liquidacion'}
        </button>
        <button className="btn-primary" onClick={onNuevaLiquidacion}>
          Nueva Liquidacion
        </button>
      </div>

      {mensaje && <div className="aviso-tope">{mensaje}</div>}

      <div className="disclaimer-legal">
        <strong>Aviso legal:</strong> Esta pre-liquidacion es una herramienta de asistencia.
        Los valores calculados deben ser verificados y transcritos manualmente por usted en su operador PILA.
      </div>
    </div>
  )
}
