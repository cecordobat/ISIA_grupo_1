import { apiClient } from './client'

export type OpcionPiso = 'BEPS' | 'SMMLV_COMPLETO' | 'NO_APLICA'
export type NivelARL = 'I' | 'II' | 'III' | 'IV' | 'V'

export interface LiquidacionRequest {
  perfil_id: string
  anio: number
  mes: number
  opcion_piso?: OpcionPiso
}

/** Los valores monetarios son strings (Decimal serializado desde Python). */
export interface LiquidacionResponse {
  liquidacion_id: string
  periodo: string
  ingreso_bruto_total: string
  ibc: string
  aporte_salud: string
  aporte_pension: string
  aporte_arl: string
  nivel_arl_aplicado: NivelARL
  total_aportes: string
  base_gravable_retencion: string
  retencion_fuente: string
  opcion_piso_proteccion: OpcionPiso
  neto_estimado: string
  ajustado_por_tope: boolean
}

export interface HistorialItem {
  id: string
  periodo: string
  ibc: string
  total_aportes: string
  retencion_fuente: string
  generado_en: string
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

  descargarPdf: async (liquidacionId: string): Promise<Blob> => {
    const { data } = await apiClient.get(`/liquidaciones/${liquidacionId}/pdf`, {
      responseType: 'blob',
    })
    return data
  },
}
