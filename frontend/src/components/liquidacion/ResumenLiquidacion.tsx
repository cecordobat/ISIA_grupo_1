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

export function ResumenLiquidacion({ resultado, onNuevaLiquidacion }: ResumenLiquidacionProps) {
  const esBEPS = resultado.opcion_piso_proteccion === 'BEPS'

  const handleDescargarPdf = async () => {
    const blob = await liquidacionesApi.descargarPdf(resultado.liquidacion_id)
    const url = window.URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `liquidacion_${resultado.periodo}.pdf`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="wizard-step resumen">
      <h2>Pre-Liquidacion - {resultado.periodo}</h2>

      {resultado.ajustado_por_tope && (
        <div className="aviso-tope">
          Su IBC fue ajustado automaticamente por el tope legal [1 SMMLV - 25 SMMLV].
          Ref: Art. 244 Ley 1955/2019.
        </div>
      )}

      <section className="resumen-seccion">
        <h3>1. Ingreso Base de Cotizacion (IBC)</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Ingreso bruto total del periodo</td>
              <td className="valor">{formatCOP(resultado.ingreso_bruto_total)}</td>
            </tr>
            <tr>
              <td>Regla del 40% aplicada sobre ingreso neto (despues de costos presuntos CIIU)</td>
              <td className="valor label-calculo">ver detalle</td>
            </tr>
            <tr className="fila-destacada">
              <td>
                <strong>IBC resultante</strong>
              </td>
              <td className="valor">
                <strong>{formatCOP(resultado.ibc)}</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="resumen-seccion">
        <h3>2. Aportes al Sistema de Seguridad Social</h3>
        {esBEPS ? (
          <div className="beps-aviso">
            Usted eligio el Piso de Proteccion Social (BEPS). El aporte del 15% va a ahorro
            programado y no acumula semanas de pension.
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
              <td>ARL - Nivel {resultado.nivel_arl_aplicado} {esBEPS ? '(no aplica en BEPS)' : ''}</td>
              <td className="valor">{formatCOP(resultado.aporte_arl)}</td>
            </tr>
            <tr className="fila-total">
              <td>
                <strong>Total aportes</strong>
              </td>
              <td className="valor">
                <strong>{formatCOP(resultado.total_aportes)}</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="resumen-seccion">
        <h3>3. Retencion en la Fuente (Art. 383 E.T.)</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Ingreso bruto</td>
              <td className="valor">{formatCOP(resultado.ingreso_bruto_total)}</td>
            </tr>
            <tr>
              <td>Menos: Salud + Pension (Art. 126-1 E.T.)</td>
              <td className="valor deduccion">
                - {formatCOP(String(parseFloat(resultado.aporte_salud) + parseFloat(resultado.aporte_pension)))}
              </td>
            </tr>
            <tr className="fila-destacada">
              <td>Base gravable de retencion</td>
              <td className="valor">{formatCOP(resultado.base_gravable_retencion)}</td>
            </tr>
            <tr className="fila-total">
              <td>
                <strong>Retencion estimada por su contratante</strong>
              </td>
              <td className="valor">
                <strong>{formatCOP(resultado.retencion_fuente)}</strong>
              </td>
            </tr>
          </tbody>
        </table>
        {resultado.retencion_fuente === '0.00' && (
          <p className="nota-retencion">
            Su base gravable no supera el umbral minimo de retencion. No aplica retencion este periodo.
          </p>
        )}
      </section>

      <section className="resumen-seccion neto-section">
        <h3>4. Neto Estimado a Recibir</h3>
        <div className="neto-valor">{formatCOP(resultado.neto_estimado)}</div>
        <p className="nota-neto">
          Este valor es estimado. El neto real depende de los acuerdos contractuales y del
          calendario de pago de su contratante.
        </p>
      </section>

      <div className="acciones-resumen">
        <button className="btn-secondary" onClick={() => void handleDescargarPdf()}>
          Descargar PDF
        </button>
        <button className="btn-primary" onClick={onNuevaLiquidacion}>
          Nueva Liquidacion
        </button>
      </div>

      <div className="disclaimer-legal">
        <strong>Aviso legal:</strong> Esta pre-liquidacion es una herramienta de asistencia.
        Los valores calculados deben ser verificados y transcritos manualmente por usted en su
        operador PILA. Esta herramienta no reemplaza el criterio de un asesor contable o
        tributario certificado.
      </div>
    </div>
  )
}
