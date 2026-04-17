import { apiClient } from './client'
import type { RolUsuario } from '../store/authStore'

export interface LoginResponse {
  access_token?: string
  token_type?: string
  rol?: RolUsuario
  mfa_required?: boolean
  mfa_token?: string
  mensaje?: string
}

export interface RegisterRequest {
  email: string
  password: string
  nombre_completo: string
  rol: RolUsuario
}

export interface MFASetupResponse {
  totp_uri: string
  secret: string
  mensaje: string
}

export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    const { data } = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },

  mfaVerify: async (mfaToken: string, code: string): Promise<LoginResponse> => {
    const { data } = await apiClient.post<LoginResponse>('/auth/mfa/verify', {
      mfa_token: mfaToken,
      codigo: code,
    })
    return data
  },

  setupMFA: async (): Promise<MFASetupResponse> => {
    const { data } = await apiClient.post<MFASetupResponse>('/auth/mfa/setup')
    return data
  },

  activateMFA: async (codigo: string): Promise<void> => {
    await apiClient.post('/auth/mfa/activate', { codigo })
  },

  register: async (body: RegisterRequest): Promise<LoginResponse> => {
    const { data } = await apiClient.post<LoginResponse>('/auth/register', body)
    return data
  },
}
