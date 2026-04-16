import { create } from 'zustand'

export type RolUsuario = 'CONTRATISTA' | 'CONTADOR' | 'ADMIN'

const tokenInicial = localStorage.getItem('access_token')
const rolInicial = localStorage.getItem('user_role') as RolUsuario | null

// Limpia sesiones heredadas de versiones anteriores que no guardaban el rol.
if (tokenInicial && !rolInicial) {
  localStorage.removeItem('access_token')
}

interface AuthState {
  token: string | null
  rol: RolUsuario | null
  isAuthenticated: boolean
  setSession: (token: string, rol: RolUsuario) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: rolInicial ? tokenInicial : null,
  rol: rolInicial,
  isAuthenticated: Boolean(tokenInicial && rolInicial),

  setSession: (token, rol) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user_role', rol)
    set({ token, rol, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    set({ token: null, rol: null, isAuthenticated: false })
  },
}))
