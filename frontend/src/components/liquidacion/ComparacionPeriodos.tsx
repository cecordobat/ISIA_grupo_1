import { useState } from 'react'
import { liquidacionesApi } from '../../api/liquidaciones'
import type { ComparacionResponse } from '../../api/liquidaciones'

interface Props {
  perfilId: string
  periodos: string[]
}

const CAMPOS: Array<{ key: keyof Omit<ComparacionResponse['diferencias'], never>; label: string }> = [
  { key: 'ingreso_bruto_total', label: 'Ingreso bruto total' },
  { key: 'ibc', label: 'IBC' },
  { key: 'aporte_salud', label: 'Aporte salud' },
  { key: 'aporte_pension', label: 'Aporte pensión' },
  { key: 'aporte_arl', label: 'Aporte ARL' },
  { key: 'retencion_fuente', label: 'Retención en la fuente' },
  { key: 'base_gravable_retencion', label: 'Base gravable retención' },
]

function formatCOP(value: number): string {
  return value.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
}

export function ComparacionPeriodos({ perfilId, periodos }: Props) {
  const [periodoA, setPeriodoA] = useState('')
  const [periodoB, setPeriodoB] = useState('')
  const [resultado, setResultado] = useState<ComparacionResponse | null>(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function handleComparar(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setResultado(null)
    setCargando(true)
    try {
      const res = await liquidacionesApi.comparar(perfilId, periodoA, periodoB)
      setResultado(res)
    } catch {
      setError('No se encontraron las liquidaciones para los períodos seleccionados.')
    } finally {
      setCargando(false)
    }
  }

  if (periodos.length < 2) return null

  return (
    <div className="snapshot-card">
      <h4>Comparar períodos</h4>
      <form onSubmit={(e) => void handleComparar(e)} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <label>
          Período A:{' '}
          <select value={periodoA} onChange={(e) => setPeriodoA(e.target.value)}>
            <option value="">Selecciona</option>
            {periodos.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        <label>
          Período B:{' '}
          <select value={periodoB} onChange={(e) => setPeriodoB(e.target.value)}>
            <option value="">Selecciona</option>
            {periodos.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        <button
          type="submit"
          className="btn-secondary"
          disabled={!periodoA || !periodoB || periodoA === periodoB || cargando}
        >
          {cargando ? 'Comparando...' : 'Comparar'}
        </button>
      </form>

      {error && <div className="aviso-tope">{error}</div>}

      {resultado && (
        <div className="resumen-tabla-wrapper" style={{ marginTop: '1rem' }}>
          <table className="resumen-tabla">
            <thead>
              <tr>
                <th>Campo</th>
                <th>{resultado.periodo_a.periodo}</th>
                <th>{resultado.periodo_b.periodo}</th>
                <th>Diferencia</th>
              </tr>
            </thead>
            <tbody>
              {CAMPOS.map(({ key, label }) => {
                const valA = resultado.periodo_a[key as keyof typeof resultado.periodo_a] as number
                const valB = resultado.periodo_b[key as keyof typeof resultado.periodo_b] as number
                const diff = resultado.diferencias[key as keyof typeof resultado.diferencias] as number
                return (
                  <tr key={key}>
                    <td>{label}</td>
                    <td className="valor">{formatCOP(valA)}</td>
                    <td className="valor">{formatCOP(valB)}</td>
                    <td className="valor" style={{ color: diff > 0 ? 'var(--success)' : diff < 0 ? 'var(--error)' : 'inherit' }}>
                      {diff > 0 ? '+' : ''}{formatCOP(diff)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
