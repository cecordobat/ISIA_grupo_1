import { apiClient } from './client'

export type NivelARL = 'I' | 'II' | 'III' | 'IV' | 'V'

export interface ContratoCreate {
  perfil_id: string
  entidad_contratante: string
  valor_bruto_mensual: string
  nivel_arl: NivelARL
  fecha_inicio: string
  fecha_fin?: string
}

export interface ContratoResponse {
  id: string
  perfil_id: string
  entidad_contratante: string
  valor_bruto_mensual: string
  nivel_arl: NivelARL
  fecha_inicio: string
  fecha_fin: string | null
  estado: string
  created_at: string
}

export const contratosApi = {
  listar: async (perfilId: string): Promise<ContratoResponse[]> => {
    const { data } = await apiClient.get<ContratoResponse[]>('/contratos/', {
      params: { perfil_id: perfilId },
    })
    return data
  },

  crear: async (body: ContratoCreate): Promise<ContratoResponse> => {
    const { data } = await apiClient.post<ContratoResponse>('/contratos/', body)
    return data
  },

  actualizar: async (
    contratoId: string,
    body: Omit<ContratoCreate, 'perfil_id'>
  ): Promise<ContratoResponse> => {
    const { data } = await apiClient.put<ContratoResponse>(`/contratos/${contratoId}`, body)
    return data
  },

  eliminar: async (contratoId: string): Promise<void> => {
    await apiClient.delete(`/contratos/${contratoId}`)
  },
}
