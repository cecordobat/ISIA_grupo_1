import { apiClient } from './client'

export interface PerfilResponse {
  id: string
  nombre_completo: string
  tipo_documento: string
  numero_documento: string
  eps: string
  afp: string
  ciiu_codigo: string
  estado: string
}

export interface PerfilCreate {
  tipo_documento: string
  numero_documento: string
  nombre_completo: string
  eps: string
  afp: string
  ciiu_codigo: string
}

export const perfilesApi = {
  listar: async (): Promise<PerfilResponse[]> => {
    const { data } = await apiClient.get<PerfilResponse[]>('/perfiles/')
    return data
  },
  crear: async (perfil: PerfilCreate): Promise<PerfilResponse> => {
    const { data } = await apiClient.post<PerfilResponse>('/perfiles/', perfil)
    return data
  },
}
