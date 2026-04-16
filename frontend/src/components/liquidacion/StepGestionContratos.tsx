import { useEffect, useState } from 'react'
import { contratosApi } from '../../api/contratos'
import type { ContratoCreate, ContratoResponse, NivelARL } from '../../api/contratos'
import { useLiquidacionStore } from '../../store/liquidacionStore'

const NIVELES_ARL: NivelARL[] = ['I', 'II', 'III', 'IV', 'V']

function formatCOP(valor: string): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(valor))
}

export function StepGestionContratos() {
  const perfilId = useLiquidacionStore((s) => s.perfilId)
  const avanzarPaso = useLiquidacionStore((s) => s.avanzarPaso)
  const retrocederPaso = useLiquidacionStore((s) => s.retrocederPaso)

  const [contratos, setContratos] = useState<ContratoResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingContratoId, setEditingContratoId] = useState<string | null>(null)
  const [form, setForm] = useState<ContratoCreate>({
    perfil_id: perfilId ?? '',
    entidad_contratante: '',
    valor_bruto_mensual: '',
    nivel_arl: 'I',
    fecha_inicio: '',
    fecha_fin: '',
  })

  const resetForm = () => {
    setEditingContratoId(null)
    setForm({
      perfil_id: perfilId ?? '',
      entidad_contratante: '',
      valor_bruto_mensual: '',
      nivel_arl: 'I',
      fecha_inicio: '',
      fecha_fin: '',
    })
  }

  const cargarContratos = async () => {
    if (!perfilId) {
      setLoading(false)
      setError('No se encontro el perfil seleccionado. Regrese al paso anterior.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const data = await contratosApi.listar(perfilId)
      setContratos(data)
    } catch {
      setError('No se pudieron cargar los contratos del perfil. Intente nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setForm((current) => ({ ...current, perfil_id: perfilId ?? '' }))
    void cargarContratos()
  }, [perfilId])

  const handleGuardarContrato = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!perfilId) return

    setSaving(true)
    setError(null)
    try {
      const payload: ContratoCreate = {
        ...form,
        perfil_id: perfilId,
        fecha_fin: form.fecha_fin || undefined,
      }

      if (editingContratoId) {
        await contratosApi.actualizar(editingContratoId, {
          entidad_contratante: payload.entidad_contratante,
          valor_bruto_mensual: payload.valor_bruto_mensual,
          nivel_arl: payload.nivel_arl,
          fecha_inicio: payload.fecha_inicio,
          fecha_fin: payload.fecha_fin,
        })
      } else {
        await contratosApi.crear(payload)
      }

      resetForm()
      await cargarContratos()
    } catch {
      setError('No fue posible guardar el contrato. Verifique fechas, valor mensual y nivel ARL.')
    } finally {
      setSaving(false)
    }
  }

  const handleEliminarContrato = async (contratoId: string) => {
    setError(null)
    try {
      await contratosApi.eliminar(contratoId)
      await cargarContratos()
    } catch {
      setError('No fue posible eliminar el contrato. Intente nuevamente.')
    }
  }

  const handleEditarContrato = (contrato: ContratoResponse) => {
    setEditingContratoId(contrato.id)
    setError(null)
    setForm({
      perfil_id: contrato.perfil_id,
      entidad_contratante: contrato.entidad_contratante,
      valor_bruto_mensual: contrato.valor_bruto_mensual,
      nivel_arl: contrato.nivel_arl,
      fecha_inicio: contrato.fecha_inicio,
      fecha_fin: contrato.fecha_fin ?? '',
    })
  }

  const hayProporcionalidad = form.fecha_inicio && !form.fecha_inicio.endsWith('-01')
  const valorNumerico = Number(form.valor_bruto_mensual)
  const advertirTope = Number.isFinite(valorNumerico) && valorNumerico > 0 && valorNumerico >= 35_587_500

  return (
    <div className="wizard-step">
      <h2>Registrar Contratos</h2>
      <p className="step-description">
        Ingrese todos los contratos activos del periodo. El motor consolidara los ingresos y tomara el nivel ARL mas alto para la liquidacion.
      </p>
      <p className="nota-neto">
        Las fechas deben reflejar la vigencia real del contrato. Pueden cruzar varios anos; la liquidacion solo tomara los dias que correspondan al periodo elegido.
      </p>

      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleGuardarContrato} className="contrato-form">
        <div className="field field-wide">
          <label htmlFor="entidad">Entidad contratante</label>
          <input
            id="entidad"
            value={form.entidad_contratante}
            onChange={(e) => setForm({ ...form, entidad_contratante: e.target.value })}
            required
          />
        </div>

        <div className="field">
          <label htmlFor="valor">Valor bruto mensual</label>
          <input
            id="valor"
            type="number"
            min="1"
            step="0.01"
            value={form.valor_bruto_mensual}
            onChange={(e) => setForm({ ...form, valor_bruto_mensual: e.target.value })}
            required
          />
        </div>

        <div className="field">
          <label htmlFor="arl">Nivel ARL</label>
          <select
            id="arl"
            value={form.nivel_arl}
            onChange={(e) => setForm({ ...form, nivel_arl: e.target.value as NivelARL })}
          >
            {NIVELES_ARL.map((nivel) => (
              <option key={nivel} value={nivel}>
                {nivel}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="inicio">Fecha de inicio</label>
          <input
            id="inicio"
            type="date"
            value={form.fecha_inicio}
            onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })}
            required
          />
        </div>

        <div className="field">
          <label htmlFor="fin">Fecha de fin</label>
          <input
            id="fin"
            type="date"
            value={form.fecha_fin}
            onChange={(e) => setForm({ ...form, fecha_fin: e.target.value })}
          />
        </div>

        <div className="wizard-actions">
          <button type="submit" className="btn-primary" disabled={saving || !perfilId}>
            {saving ? 'Guardando...' : editingContratoId ? 'Guardar cambios' : 'Agregar contrato'}
          </button>
          {editingContratoId && (
            <button type="button" className="btn-secondary" onClick={resetForm}>
              Cancelar edicion
            </button>
          )}
        </div>
      </form>

      {hayProporcionalidad && (
        <div className="aviso-requerido">
          La fecha de inicio no coincide con el dia 1. El sistema aplicara proporcionalidad por dias.
        </div>
      )}

      {advertirTope && (
        <div className="aviso-tope">
          Este contrato supera aproximadamente 25 SMMLV mensuales. El IBC final podria ser topado.
        </div>
      )}

      <section className="contratos-lista">
        <h3>Contratos registrados</h3>
        {loading ? (
          <div className="loading-state">Cargando contratos...</div>
        ) : contratos.length === 0 ? (
          <div className="aviso-requerido">
            Debe registrar al menos un contrato para calcular la liquidacion.
          </div>
        ) : (
          contratos.map((contrato) => (
            <div key={contrato.id} className="card contrato-card">
              <div>
                <strong>{contrato.entidad_contratante}</strong>
                <div className="perfil-detalles contrato-detalles">
                  <span>Valor: {formatCOP(contrato.valor_bruto_mensual)}</span>
                  <span>ARL: {contrato.nivel_arl}</span>
                  <span>Inicio: {contrato.fecha_inicio}</span>
                  <span>Fin: {contrato.fecha_fin ?? 'Abierto'}</span>
                </div>
              </div>
              <div className="wizard-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => handleEditarContrato(contrato)}
                >
                  Editar
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => void handleEliminarContrato(contrato.id)}
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))
        )}
      </section>

      <div className="wizard-actions">
        <button className="btn-secondary" onClick={retrocederPaso}>
          Atras
        </button>
        <button
          className="btn-primary"
          onClick={avanzarPaso}
          disabled={loading || contratos.length === 0}
        >
          Continuar al periodo
        </button>
      </div>
    </div>
  )
}
