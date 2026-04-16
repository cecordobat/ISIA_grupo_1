/**
 * Paso 3 del wizard: Decisión sobre el Piso de Protección Social.
 * Solo se muestra cuando el ingreso neto < 1 SMMLV.
 * Ref: RN-06, HU-04, Decreto 1174/2020
 *
 * CRÍTICO: El usuario NO puede avanzar sin elegir una opción.
 */
import type { OpcionPiso } from '../../api/liquidaciones'

interface StepPisoProteccionProps {
  onSelectOpcion: (opcion: OpcionPiso) => void
  opcionSeleccionada: OpcionPiso | null
  onConfirmar: () => void
}

export function StepPisoProteccion({
  onSelectOpcion,
  opcionSeleccionada,
  onConfirmar,
}: StepPisoProteccionProps) {
  return (
    <div className="wizard-step">
      <h2>Piso de Protección Social</h2>
      <p className="step-description">
        Su ingreso neto es inferior a <strong>1 Salario Mínimo Mensual Legal Vigente (SMMLV)</strong>.
        La ley le ofrece dos opciones. Lea cuidadosamente antes de elegir:
      </p>

      <div className="piso-opciones">
        {/* Opción A: BEPS */}
        <div
          className={`opcion-card ${opcionSeleccionada === 'BEPS' ? 'selected' : ''}`}
          onClick={() => onSelectOpcion('BEPS')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onSelectOpcion('BEPS')}
        >
          <div className="opcion-header">
            <input
              type="radio"
              name="opcion_piso"
              checked={opcionSeleccionada === 'BEPS'}
              onChange={() => onSelectOpcion('BEPS')}
              id="beps"
            />
            <label htmlFor="beps">
              <strong>Opción A: Piso de Protección Social (BEPS)</strong>
            </label>
          </div>
          <ul className="opcion-detalles">
            <li>Aporte del <strong>15% de su ingreso bruto</strong> al fondo BEPS</li>
            <li>Menor carga mensual</li>
            <li className="advertencia">
              ⚠️ <strong>Esta opción NO acumula semanas de pensión en Colpensiones.</strong>
              Su cotización va a un ahorro programado, no al régimen pensional ordinario.
            </li>
          </ul>
          <p className="ref-legal">Ref: Decreto 1174 de 2020, Art. 193 Ley 1955/2019</p>
        </div>

        {/* Opción B: SMMLV Completo */}
        <div
          className={`opcion-card ${opcionSeleccionada === 'SMMLV_COMPLETO' ? 'selected' : ''}`}
          onClick={() => onSelectOpcion('SMMLV_COMPLETO')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onSelectOpcion('SMMLV_COMPLETO')}
        >
          <div className="opcion-header">
            <input
              type="radio"
              name="opcion_piso"
              checked={opcionSeleccionada === 'SMMLV_COMPLETO'}
              onChange={() => onSelectOpcion('SMMLV_COMPLETO')}
              id="smmlv"
            />
            <label htmlFor="smmlv">
              <strong>Opción B: Cotizar sobre 1 SMMLV completo</strong>
            </label>
          </div>
          <ul className="opcion-detalles">
            <li>Cotiza Salud (12.5%), Pensión (16%) y ARL sobre 1 SMMLV</li>
            <li>Mayor carga mensual, pero <strong>acumula semanas de pensión</strong></li>
            <li>Acceso completo al sistema de salud contributivo</li>
          </ul>
          <p className="ref-legal">Ref: Ley 100/1993, Art. 18</p>
        </div>
      </div>

      {opcionSeleccionada === null && (
        <div className="aviso-requerido">
          Debe seleccionar una opción para continuar con la liquidación.
        </div>
      )}

      <button
        className="btn-primary"
        onClick={onConfirmar}
        disabled={opcionSeleccionada === null}
      >
        Confirmar elección y calcular aportes
      </button>
    </div>
  )
}
