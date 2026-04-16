/**
 * Paso 5 del wizard: Resumen final de la pre-liquidación.
 * Muestra el desglose completo: IBC → aportes → retención → neto.
 * Ref: RF-08, HU-07
 */
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

  return (
    <div className="wizard-step resumen">
      <h2>Pre-Liquidación — {resultado.periodo}</h2>

      {resultado.ajustado_por_tope && (
        <div className="aviso-tope">
          ℹ️ Su IBC fue ajustado automáticamente por el tope legal [1 SMMLV – 25 SMMLV].
          Ref: Art. 244 Ley 1955/2019.
        </div>
      )}

      {/* Bloque 1: Derivación del IBC */}
      <section className="resumen-seccion">
        <h3>1. Ingreso Base de Cotización (IBC)</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Ingreso bruto total del período</td>
              <td className="valor">{formatCOP(resultado.ingreso_bruto_total)}</td>
            </tr>
            <tr>
              <td>Regla del 40% aplicada sobre ingreso neto (después de costos presuntos CIIU)</td>
              <td className="valor label-calculo">ver detalle</td>
            </tr>
            <tr className="fila-destacada">
              <td><strong>IBC resultante</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.ibc)}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* Bloque 2: Aportes SGSSI */}
      <section className="resumen-seccion">
        <h3>2. Aportes al Sistema de Seguridad Social</h3>
        {esBEPS ? (
          <div className="beps-aviso">
            Usted eligió el Piso de Protección Social (BEPS).
            El aporte del 15% va a ahorro programado — NO acumula semanas de pensión.
          </div>
        ) : null}
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Salud {esBEPS ? '(no aplica en BEPS)' : '(12.5% del IBC)'}</td>
              <td className="valor">{formatCOP(resultado.aporte_salud)}</td>
            </tr>
            <tr>
              <td>{esBEPS ? 'BEPS (15% del ingreso bruto)' : 'Pensión (16% del IBC)'}</td>
              <td className="valor">{formatCOP(resultado.aporte_pension)}</td>
            </tr>
            <tr>
              <td>ARL — Nivel {resultado.nivel_arl_aplicado} {esBEPS ? '(no aplica en BEPS)' : ''}</td>
              <td className="valor">{formatCOP(resultado.aporte_arl)}</td>
            </tr>
            <tr className="fila-total">
              <td><strong>Total aportes</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.total_aportes)}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* Bloque 3: Retención en la fuente */}
      <section className="resumen-seccion">
        <h3>3. Retención en la Fuente (Art. 383 E.T.)</h3>
        <table className="resumen-tabla">
          <tbody>
            <tr>
              <td>Ingreso bruto</td>
              <td className="valor">{formatCOP(resultado.ingreso_bruto_total)}</td>
            </tr>
            <tr>
              <td>Menos: Salud + Pensión (Art. 126-1 E.T.)</td>
              <td className="valor deduccion">
                − {formatCOP(String(parseFloat(resultado.aporte_salud) + parseFloat(resultado.aporte_pension)))}
              </td>
            </tr>
            <tr className="fila-destacada">
              <td>Base gravable de retención</td>
              <td className="valor">{formatCOP(resultado.base_gravable_retencion)}</td>
            </tr>
            <tr className="fila-total">
              <td><strong>Retención estimada por su contratante</strong></td>
              <td className="valor"><strong>{formatCOP(resultado.retencion_fuente)}</strong></td>
            </tr>
          </tbody>
        </table>
        {resultado.retencion_fuente === '0.00' && (
          <p className="nota-retencion">
            Su base gravable no supera el umbral mínimo de retención. No aplica retención este período.
          </p>
        )}
      </section>

      {/* Bloque 4: Neto estimado */}
      <section className="resumen-seccion neto-section">
        <h3>4. Neto Estimado a Recibir</h3>
        <div className="neto-valor">{formatCOP(resultado.neto_estimado)}</div>
        <p className="nota-neto">
          Este valor es estimado. El neto real depende de los acuerdos contractuales
          y del calendario de pago de su contratante.
        </p>
      </section>

      <div className="acciones-resumen">
        <button className="btn-primary" onClick={onNuevaLiquidacion}>
          Nueva Liquidación
        </button>
      </div>

      <div className="disclaimer-legal">
        ⚠️ <strong>Aviso legal:</strong> Esta pre-liquidación es una herramienta de asistencia.
        Los valores calculados deben ser verificados y transcritos manualmente por usted en su
        operador PILA (SOI, Mi Planilla, Aportes en Línea, etc.). Esta herramienta no reemplaza
        el criterio de un asesor contable o tributario certificado. (RES-O03)
      </div>
    </div>
  )
}
