import { beforeEach, describe, expect, it, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Navigate, Route, Routes } from 'react-router-dom'
import { LoginPage } from './LoginPage'
import { RegisterPage } from './RegisterPage'
import { LiquidacionWizardPage } from './LiquidacionWizardPage'
import { useAuthStore } from '../store/authStore'
import { useLiquidacionStore } from '../store/liquidacionStore'

const mocks = vi.hoisted(() => ({
  register: vi.fn(),
  login: vi.fn(),
  listarPerfiles: vi.fn(),
  crearPerfil: vi.fn(),
  vincularContador: vi.fn(),
  listarLiquidaciones: vi.fn(),
  obtenerLiquidacion: vi.fn(),
  crearContrato: vi.fn(),
  listarContratos: vi.fn(),
  eliminarContrato: vi.fn(),
  calcularLiquidacion: vi.fn(),
  descargarPdf: vi.fn(),
  confirmarLiquidacion: vi.fn(),
}))

vi.mock('../api/auth', () => ({
  authApi: {
    register: mocks.register,
    login: mocks.login,
  },
}))

vi.mock('../api/perfiles', () => ({
  perfilesApi: {
    listar: mocks.listarPerfiles,
    crear: mocks.crearPerfil,
  },
}))

vi.mock('../api/contador', () => ({
  contadorApi: {
    vincular: mocks.vincularContador,
    listarClientes: vi.fn(),
    revisarLiquidacion: vi.fn(),
  },
}))

vi.mock('../api/liquidaciones', () => ({
  liquidacionesApi: {
    listarPorPerfil: mocks.listarLiquidaciones,
    obtenerDetalle: mocks.obtenerLiquidacion,
    calcular: mocks.calcularLiquidacion,
    descargarPdf: mocks.descargarPdf,
    confirmar: mocks.confirmarLiquidacion,
  },
}))

vi.mock('../api/contratos', () => ({
  contratosApi: {
    crear: mocks.crearContrato,
    listarPorPerfil: mocks.listarContratos,
    eliminar: mocks.eliminarContrato,
  },
}))

function ProtectedRoute({
  children,
  requiredRole,
}: {
  children: React.ReactNode
  requiredRole?: 'CONTRATISTA' | 'CONTADOR'
}) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const rol = useAuthStore((s) => s.rol)

  if (!isAuthenticated || !rol) return <Navigate to="/login" replace />
  if (requiredRole && rol !== requiredRole) {
    return <Navigate to={rol === 'CONTADOR' ? '/contador' : '/liquidacion'} replace />
  }
  return <>{children}</>
}

function AppUnderTest({ initialPath = '/register' }: { initialPath?: string }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/liquidacion"
            element={
              <ProtectedRoute requiredRole="CONTRATISTA">
                <LiquidacionWizardPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Flujo principal de autenticacion y sesion', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuthStore.setState({ token: null, rol: null, isAuthenticated: false })
    useLiquidacionStore.getState().resetear()

    mocks.register.mockReset()
    mocks.login.mockReset()
    mocks.listarPerfiles.mockReset()
    mocks.crearPerfil.mockReset()
    mocks.vincularContador.mockReset()
    mocks.listarLiquidaciones.mockReset()
    mocks.obtenerLiquidacion.mockReset()
    mocks.crearContrato.mockReset()
    mocks.listarContratos.mockReset()
    mocks.eliminarContrato.mockReset()
    mocks.calcularLiquidacion.mockReset()
    mocks.descargarPdf.mockReset()
    mocks.confirmarLiquidacion.mockReset()

    mocks.listarLiquidaciones.mockResolvedValue([])
    mocks.obtenerLiquidacion.mockResolvedValue(null)
    mocks.vincularContador.mockResolvedValue({ message: 'ok' })
    mocks.listarContratos.mockResolvedValue([])
  })

  it('permite registrarse, crear perfil, cerrar sesion e iniciar sesion nuevamente', async () => {
    const user = userEvent.setup()

    mocks.register.mockResolvedValue({
      access_token: 'token-registro',
      token_type: 'bearer',
      rol: 'CONTRATISTA',
    })

    mocks.crearPerfil.mockResolvedValue({
      id: 'perfil-1',
      nombre_completo: 'Willi Test',
      tipo_documento: 'CC',
      numero_documento: '123456789',
      eps: 'Nueva EPS',
      afp: 'Porvenir',
      ciiu_codigo: '6201',
      pct_costos_presuntos: '0.60',
      estado: 'ACTIVO',
    })

    mocks.listarPerfiles
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        {
          id: 'perfil-1',
          nombre_completo: 'Willi Test',
          tipo_documento: 'CC',
          numero_documento: '123456789',
          eps: 'Nueva EPS',
          afp: 'Porvenir',
          ciiu_codigo: '6201',
          pct_costos_presuntos: '0.60',
          estado: 'ACTIVO',
        },
      ])
      .mockResolvedValueOnce([
        {
          id: 'perfil-1',
          nombre_completo: 'Willi Test',
          tipo_documento: 'CC',
          numero_documento: '123456789',
          eps: 'Nueva EPS',
          afp: 'Porvenir',
          ciiu_codigo: '6201',
          pct_costos_presuntos: '0.60',
          estado: 'ACTIVO',
        },
      ])

    mocks.login.mockResolvedValue({
      access_token: 'token-login',
      token_type: 'bearer',
      rol: 'CONTRATISTA',
    })

    render(<AppUnderTest />)

    await user.type(screen.getByLabelText(/Nombre Completo/i), 'Willi Test')
    await user.type(screen.getByLabelText(/^Email$/i), 'willi.test@example.com')
    await user.type(screen.getByLabelText(/Contrasena/i), 'Clave123*')
    await user.click(screen.getByRole('button', { name: /Registrarse/i }))

    expect(await screen.findByText(/No tiene perfiles registrados/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Crear Nuevo Perfil/i }))
    await user.type(screen.getByLabelText(/Numero Documento/i), '123456789')
    await user.type(screen.getByLabelText(/Nombre Completo/i), 'Willi Test')
    await user.type(screen.getByLabelText(/^EPS$/i), 'Nueva EPS')
    await user.type(screen.getByLabelText(/^AFP$/i), 'Porvenir')
    await user.type(screen.getByLabelText(/Codigo CIIU/i), '6201')
    await user.click(screen.getByRole('button', { name: /Guardar Perfil/i }))

    expect(await screen.findByText('Willi Test')).toBeInTheDocument()
    expect(screen.getByText(/CIIU: 6201/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Cerrar sesion/i }))

    expect(await screen.findByRole('heading', { name: /Motor de Cumplimiento/i })).toBeInTheDocument()
    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false)
    })

    await user.type(screen.getByLabelText(/^Email$/i), 'willi.test@example.com')
    await user.type(screen.getByLabelText(/Contrasena/i), 'Clave123*')
    await user.click(screen.getByRole('button', { name: /Ingresar/i }))

    expect(await screen.findByText('Willi Test')).toBeInTheDocument()
    expect(screen.getByText(/Seleccione el perfil de contratista/i)).toBeInTheDocument()
  })
})
