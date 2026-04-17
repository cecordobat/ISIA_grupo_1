import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { MFAVerifyStep } from '../components/auth/MFAVerifyStep'

export function LoginPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const mfaPendingToken = useAuthStore((s) => s.mfaPendingToken)
  const setMfaPending = useAuthStore((s) => s.setMfaPending)
  const clearMfaPending = useAuthStore((s) => s.clearMfaPending)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await authApi.login(email, password)

      if (data.mfa_required && data.mfa_token) {
        setMfaPending(data.mfa_token)
      } else if (data.access_token && data.rol) {
        setSession(data.access_token, data.rol)
        const dest = data.rol === 'CONTADOR' ? '/contador' : data.rol === 'ADMIN' ? '/admin' : data.rol === 'ENTIDAD_CONTRATANTE' ? '/verificacion' : '/liquidacion'
        navigate(dest)
      } else {
        setError('La respuesta del servidor no contiene una sesion valida.')
      }
    } catch {
      setError('Email o contrasena incorrectos. Verifique sus datos.')
    } finally {
      setLoading(false)
    }
  }

  if (mfaPendingToken) {
    return (
      <div className="bg-[#f7f9fe] min-h-screen flex flex-col items-center justify-center p-4">
        <MFAVerifyStep mfaToken={mfaPendingToken} onCancel={clearMfaPending} />
      </div>
    )
  }

  return (
    <div className="bg-[#f7f9fe] text-[#181c20] min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden font-['Inter']">
      <div className="fixed top-0 left-0 w-full h-full -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-[#004ac6]/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[30%] h-[30%] bg-[#495c95]/5 rounded-full blur-[100px]" />
      </div>

      <div className="mb-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-1000">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="material-symbols-outlined text-[#004ac6] text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            security
          </span>
          <h1 className="text-xl font-extrabold tracking-tighter text-[#181c20]">Motor de Cumplimiento</h1>
        </div>
        <p className="text-[#434655] font-medium tracking-widest uppercase text-[10px]">Colombia Edition</p>
      </div>

      <main className="w-full max-w-[440px] bg-white p-10 rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] animate-in zoom-in-95 duration-500">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#181c20] tracking-tight mb-2">Bienvenido de nuevo</h2>
          <p className="text-[#434655] text-sm">Ingrese sus credenciales para acceder a la plataforma de cumplimiento.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#434655] ml-1" htmlFor="email">
              Correo Electronico
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg">mail</span>
              <input
                id="email"
                type="email"
                placeholder="nombre@empresa.co"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-[#004ac6]/20 transition-all text-[#181c20] placeholder:text-slate-300 border-b-2 border-slate-100 focus:border-[#004ac6]"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center px-1">
              <label className="block text-sm font-semibold text-[#434655]" htmlFor="password">
                Contrasena
              </label>
              <a className="text-xs font-bold text-[#004ac6] hover:text-[#2563eb] transition-colors" href="#">
                Olvido su contrasena?
              </a>
            </div>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg">lock</span>
              <input
                id="password"
                type="password"
                placeholder="********"
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-[#004ac6]/20 transition-all text-[#181c20] placeholder:text-slate-300 border-b-2 border-slate-100 focus:border-[#004ac6]"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-lg border border-red-100 animate-in fade-in slide-in-from-top-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 px-6 bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white font-bold rounded-xl shadow-lg shadow-blue-100 hover:shadow-blue-200 active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4"
          >
            <span>{loading ? 'Ingresando...' : 'Ingresar'}</span>
            {!loading && <span className="material-symbols-outlined text-xl">login</span>}
          </button>
        </form>

        <div className="mt-8 pt-8 border-t border-slate-50 text-center">
          <p className="text-sm text-[#434655]">
            Aun no tiene acceso?
            <Link className="text-[#004ac6] font-bold hover:underline ml-1" to="/register">
              Crear cuenta
            </Link>
          </p>
        </div>
      </main>
    </div>
  )
}
