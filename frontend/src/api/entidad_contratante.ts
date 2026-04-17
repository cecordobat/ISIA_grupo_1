import { apiClient } from './client'

export interface EstadoCumplimiento {
  nombre_contratista: string
  documento: string
  periodo_reciente: string | null
  tiene_liquidacion_confirmada: boolean
  estado: 'CONFIRMADA' | 'PENDIENTE_CONFIRMACION' | 'SIN_LIQUIDACIONES'
}

export const entidadContratanteApi = {
  verificarCumplimiento: async (perfilId: string): Promise<EstadoCumplimiento> => {
    const { data } = await apiClient.get<EstadoCumplimiento>(`/verificacion/cumplimiento/${perfilId}`)
    return data
  },

  autorizarAcceso: async (perfilId: string, entidadEmail: string): Promise<{ mensaje: string }> => {
    const { data } = await apiClient.post<{ mensaje: string }>(
      `/verificacion/accesos/${perfilId}/autorizar`,
      { entidad_email: entidadEmail },
    )
    return data
  },

  revocarAcceso: async (perfilId: string, entidadEmail: string): Promise<{ mensaje: string }> => {
    const { data } = await apiClient.delete<{ mensaje: string }>(
      `/verificacion/accesos/${perfilId}/revocar`,
      { data: { entidad_email: entidadEmail } },
    )
    return data
  },
}
