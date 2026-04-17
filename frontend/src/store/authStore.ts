import { create } from 'zustand'

export type RolUsuario = 'CONTRATISTA' | 'CONTADOR' | 'ADMIN' | 'ENTIDAD_CONTRATANTE'

const tokenInicial = localStorage.getItem('access_token')
const rolInicial = localStorage.getItem('user_role') as RolUsuario | null

if (tokenInicial && !rolInicial) {
  localStorage.removeItem('access_token')
}

interface AuthState {
  token: string | null
  rol: RolUsuario | null
  isAuthenticated: boolean
  mfaPendingToken: string | null
  setSession: (token: string, rol: RolUsuario) => void
  setMfaPending: (token: string) => void
  clearMfaPending: () => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: rolInicial ? tokenInicial : null,
  rol: rolInicial,
  isAuthenticated: Boolean(tokenInicial && rolInicial),
  mfaPendingToken: null,

  setSession: (token, rol) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user_role', rol)
    set({ token, rol, isAuthenticated: true, mfaPendingToken: null })
  },

  setMfaPending: (token) => set({ mfaPendingToken: token }),

  clearMfaPending: () => set({ mfaPendingToken: null }),

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    set({ token: null, rol: null, isAuthenticated: false, mfaPendingToken: null })
  },
}))
