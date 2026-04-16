import { apiClient } from './client'

export interface VincularContadorRequest {
  perfil_id: string
  contador_email: string
}

export interface ClienteContador {
  perfil_id: string
  nombre_contratista: string
  numero_documento: string
  ciiu_codigo: string
  contratista_email: string
}

export interface RevisionContadorRequest {
  liquidacion_id: string
  nota: string
  aprobada: boolean
}

export const contadorApi = {
  vincular: async (body: VincularContadorRequest): Promise<{ message: string }> => {
    const { data } = await apiClient.post<{ message: string }>('/contador/vinculos', body)
    return data
  },

  listarClientes: async (): Promise<ClienteContador[]> => {
    const { data } = await apiClient.get<ClienteContador[]>('/contador/clientes')
    return data
  },

  revisarLiquidacion: async (body: RevisionContadorRequest): Promise<{ message: string }> => {
    const { data } = await apiClient.post<{ message: string }>('/contador/revisiones', body)
    return data
  },
}
