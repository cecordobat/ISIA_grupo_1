import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore, type RolUsuario } from '../store/authStore'

export function RegisterPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nombreCompleto, setNombreCompleto] = useState('')
  const [rol, setRol] = useState<RolUsuario>('CONTRATISTA')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { access_token, rol: rolRespuesta } = await authApi.register({
        email,
        password,
        nombre_completo: nombreCompleto,
        rol,
      })
      if (access_token && rolRespuesta) {
        setSession(access_token, rolRespuesta)
        const dest = rolRespuesta === 'CONTADOR' ? '/contador' : rolRespuesta === 'ADMIN' ? '/admin' : rolRespuesta === 'ENTIDAD_CONTRATANTE' ? '/verificacion' : '/liquidacion'
        navigate(dest)
      } else {
        setError('Error al crear la cuenta. Intente de nuevo.')
      }
    } catch {
      setError('Error al registrar la cuenta. Es posible que el correo ya esté en uso.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-[#f7f9fe] text-[#181c20] min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden font-['Inter']">
      {/* Background Decorative Elements */}
      <div className="fixed top-0 left-0 w-full h-full -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-[#004ac6]/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[30%] h-[30%] bg-[#004ac6]/5 rounded-full blur-[100px]" />
      </div>

      {/* Top Branding */}
      <div className="mb-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-1000">
        <div className="flex items-center justify-center gap-2 mb-1">
          <span className="material-symbols-outlined text-[#004ac6] text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>security</span>
          <h1 className="text-xl font-extrabold tracking-tighter text-[#181c20]">Motor de Cumplimiento</h1>
        </div>
        <p className="text-[#434655] font-medium tracking-widest uppercase text-[10px]">Colombia Edition</p>
      </div>

      {/* Main Registration Card */}
      <main className="w-full max-w-[440px] bg-white p-8 md:p-10 rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] animate-in zoom-in-95 duration-500">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-[#181c20] tracking-tight mb-2">Registro</h2>
          <p className="text-slate-500 font-medium text-sm">Motor de Cumplimiento - Crear nueva cuenta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Full Name Field */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#434655] ml-1">Nombre Completo</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg group-focus-within:text-[#004ac6] transition-colors">person</span>
              <input 
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 rounded-xl border-none border-b-2 border-slate-100 focus:ring-2 focus:ring-[#004ac6]/20 focus:border-[#004ac6] transition-all text-[#181c20] placeholder:text-slate-300 outline-none"
                placeholder="John Doe"
                type="text"
                value={nombreCompleto}
                onChange={(e) => setNombreCompleto(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#434655] ml-1">Correo Electrónico</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg group-focus-within:text-[#004ac6] transition-colors">mail</span>
              <input 
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 rounded-xl border-none border-b-2 border-slate-100 focus:ring-2 focus:ring-[#004ac6]/20 focus:border-[#004ac6] transition-all text-[#181c20] placeholder:text-slate-300 outline-none"
                placeholder="nombre@empresa.co"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#434655] ml-1">Contraseña</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg group-focus-within:text-[#004ac6] transition-colors">lock</span>
              <input 
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 rounded-xl border-none border-b-2 border-slate-100 focus:ring-2 focus:ring-[#004ac6]/20 focus:border-[#004ac6] transition-all text-[#181c20] placeholder:text-slate-300 outline-none"
                placeholder="••••••••"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Role Selector */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#434655] ml-1">Seleccionar Rol</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg group-focus-within:text-[#004ac6] transition-colors">manage_accounts</span>
              <select 
                className="w-full pl-12 pr-10 py-3.5 bg-slate-50 rounded-xl border-none border-b-2 border-slate-100 focus:ring-2 focus:ring-[#004ac6]/20 focus:border-[#004ac6] transition-all text-[#181c20] appearance-none cursor-pointer outline-none"
                value={rol}
                onChange={(e) => setRol(e.target.value as RolUsuario)}
                required
              >
                <option value="CONTRATISTA">Contratista</option>
                <option value="CONTADOR">Contador</option>
                <option value="ENTIDAD_CONTRATANTE">Entidad Contratante</option>
              </select>
              <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">expand_more</span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-lg border border-red-100 animate-in fade-in">
              {error}
            </div>
          )}

          {/* Action Button */}
          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-4 px-6 bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white font-bold rounded-xl shadow-lg shadow-blue-100 hover:shadow-blue-200 active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
          >
            <span>{loading ? 'Procesando...' : 'Crear Cuenta'}</span>
            {!loading && <span className="material-symbols-outlined text-xl">login</span>}
          </button>
        </form>

        <div className="mt-8 pt-8 border-t border-slate-50 text-center">
          <p className="text-sm text-[#434655]">
            ¿Ya tienes cuenta?
            <Link className="text-[#004ac6] font-bold hover:underline ml-1" to="/login">Inicia sesión</Link>
          </p>
        </div>
      </main>

      <footer className="w-full max-w-[440px] mt-8 text-center text-[10px] text-slate-400 font-medium uppercase tracking-widest leading-loose">
        <p>© 2024 Motor de Cumplimiento Colombia Edition</p>
        <div className="flex justify-center gap-4 mt-2">
          <a href="#" className="hover:text-[#004ac6] transition-colors">Privacidad</a>
          <a href="#" className="hover:text-[#004ac6] transition-colors">Términos</a>
          <a href="#" className="hover:text-[#004ac6] transition-colors">Soporte</a>
        </div>
      </footer>
    </div>
  )
}
