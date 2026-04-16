import { apiClient } from './client'

export type OpcionPiso = 'BEPS' | 'SMMLV_COMPLETO' | 'NO_APLICA'
export type NivelARL = 'I' | 'II' | 'III' | 'IV' | 'V'

export interface LiquidacionRequest {
  perfil_id: string
  anio: number
  mes: number
  opcion_piso?: OpcionPiso
}

export interface ContratoConsiderado {
  contrato_id: string
  entidad_contratante: string
  valor_bruto_mensual: string
  dias_cotizados: number
  ingreso_bruto_proporcional: string
  nivel_arl: NivelARL
}

export interface SnapshotNormativo {
  smmlv: string
  uvt: string
  pct_salud: string
  pct_pension: string
  pct_costos_presuntos: string
  tarifas_arl: Record<string, string>
  vigencia_anio: number
}

export interface RevisionLiquidacion {
  contador_id: string
  nota: string
  aprobada: boolean
  revisado_en: string
}

export interface ConfirmacionLiquidacion {
  usuario_id: string
  confirmado_en: string
}

export interface LiquidacionResponse {
  liquidacion_id: string
  periodo: string
  ingreso_bruto_total: string
  costos_presuntos: string
  pct_costos_presuntos: string
  base_40_pct: string
  ibc: string
  aporte_salud: string
  aporte_pension: string
  aporte_arl: string
  nivel_arl_aplicado: NivelARL
  tarifa_arl_aplicada: string
  total_aportes: string
  base_gravable_retencion: string
  retencion_fuente: string
  opcion_piso_proteccion: OpcionPiso
  neto_estimado: string
  ajustado_por_tope: boolean
  contratos_considerados: ContratoConsiderado[]
  snapshot_normativo: SnapshotNormativo
  revision?: RevisionLiquidacion | null
  confirmacion?: ConfirmacionLiquidacion | null
  requiere_revision_contador: boolean
  puede_confirmar: boolean
}

export interface HistorialItem {
  id: string
  periodo: string
  ibc: string
  total_aportes: string
  retencion_fuente: string
  generado_en: string
  opcion_piso_proteccion: OpcionPiso
  estado_proceso: string
}

export interface AniosDisponiblesResponse {
  anios: number[]
}

export interface LiquidacionDetalle {
  id: string
  periodo: string
  ingreso_bruto_total: string
  costos_presuntos: string
  pct_costos_presuntos: string
  base_40_pct: string
  ibc: string
  aporte_salud: string
  aporte_pension: string
  aporte_arl: string
  nivel_arl_aplicado: NivelARL
  total_aportes: string
  base_gravable_retencion: string
  retencion_fuente: string
  neto_estimado: string
  opcion_piso_proteccion: OpcionPiso
  generado_en: string
  snapshot_normativo: SnapshotNormativo
  revision?: RevisionLiquidacion | null
  confirmacion?: ConfirmacionLiquidacion | null
  requiere_revision_contador: boolean
  puede_confirmar: boolean
  estado_proceso: string
}

export const liquidacionesApi = {
  calcular: async (body: LiquidacionRequest): Promise<LiquidacionResponse> => {
    const { data } = await apiClient.post<LiquidacionResponse>('/liquidaciones/calcular', body)
    return data
  },

  historial: async (perfilId: string): Promise<HistorialItem[]> => {
    const { data } = await apiClient.get<HistorialItem[]>(`/liquidaciones/historial/${perfilId}`)
    return data
  },

  aniosDisponibles: async (): Promise<number[]> => {
    const { data } = await apiClient.get<AniosDisponiblesResponse>('/liquidaciones/anios-disponibles')
    return data.anios
  },

  obtenerDetalle: async (liquidacionId: string): Promise<LiquidacionDetalle> => {
    const { data } = await apiClient.get<LiquidacionDetalle>(`/liquidaciones/${liquidacionId}`)
    return data
  },

  confirmar: async (liquidacionId: string): Promise<{ message: string }> => {
    const { data } = await apiClient.post<{ message: string }>(`/liquidaciones/${liquidacionId}/confirmar`)
    return data
  },

  descargarPdf: async (liquidacionId: string): Promise<Blob> => {
    const { data } = await apiClient.get(`/liquidaciones/${liquidacionId}/pdf`, {
      responseType: 'blob',
    })
    return data
  },
}
