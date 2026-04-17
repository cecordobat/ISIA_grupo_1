import { useState, useRef } from 'react'
import { authApi } from '../../api/auth'
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'

interface MFAVerifyStepProps {
  mfaToken: string
  onCancel: () => void
}

export function MFAVerifyStep({ mfaToken, onCancel }: MFAVerifyStepProps) {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [code, setCode] = useState(['', '', '', '', '', ''])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return
    const newCode = [...code]
    newCode[index] = value.slice(-1)
    setCode(newCode)

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handleVerify = async () => {
    const fullCode = code.join('')
    if (fullCode.length < 6) return

    setLoading(true)
    setError(null)
    try {
      const data = await authApi.mfaVerify(mfaToken, fullCode)
      if (data.access_token && data.rol) {
        setSession(data.access_token, data.rol)
        const dest = data.rol === 'CONTADOR' ? '/contador' : data.rol === 'ADMIN' ? '/admin' : data.rol === 'ENTIDAD_CONTRATANTE' ? '/verificacion' : '/liquidacion'
        navigate(dest)
      } else {
        setError('Error en la respuesta del servidor.')
      }
    } catch {
      setError('Código inválido o expirado.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-[480px] animate-in fade-in zoom-in-95 duration-500 font-['Inter']">
      <div className="bg-white rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] overflow-hidden">
        <div className="p-8 md:p-10 text-center">
          <div className="mb-8 flex justify-center">
            <div className="w-16 h-16 bg-[#004ac6]/10 rounded-full flex items-center justify-center text-[#004ac6]">
              <span className="material-symbols-outlined text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>lock_person</span>
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-[#181c20] tracking-tight mb-2">Verificación en dos pasos</h1>
          <p className="text-[#434655] text-sm mb-8">Ingresa el código de tu app autenticadora</p>

          <div className="flex justify-between gap-2 mb-8">
            {code.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                className="w-12 h-14 md:w-14 md:h-16 text-center text-2xl font-bold bg-slate-50 border-b-2 border-slate-200 focus:border-[#004ac6] focus:ring-0 transition-all text-[#181c20] rounded-lg"
                maxLength={1}
                placeholder="0"
                type="text"
                value={digit}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
              />
            ))}
          </div>

          {error && <div className="mb-4 text-xs font-bold text-red-600 bg-red-50 p-2 rounded">{error}</div>}

          <button 
            onClick={handleVerify}
            disabled={loading || code.some(d => !d)}
            className="w-full bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white py-4 px-6 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl active:scale-[0.98] transition-all mb-6 disabled:opacity-50"
          >
            {loading ? 'Verificando...' : 'Verificar y Continuar'}
          </button>

          <div className="flex flex-col gap-4">
            <button onClick={onCancel} className="text-[#004ac6] font-medium hover:underline text-sm inline-flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-sm">arrow_back</span>
              Regresar al login
            </button>
            <div className="h-px bg-slate-50 w-full"></div>
            <p className="text-[#434655] text-[10px] tracking-wide uppercase font-medium">
              ¿Problemas con la verificación?
            </p>
            <button className="text-[#434655] hover:text-[#181c20] font-medium text-sm">
              Contactar con soporte técnico
            </button>
          </div>
        </div>

        <div className="bg-slate-50 px-8 py-4 flex items-center justify-center gap-3">
          <span className="material-symbols-outlined text-slate-400 text-lg">encrypted</span>
          <span className="text-[10px] font-medium text-[#434655] tracking-wider uppercase">Sesión Protegida — TLS 1.3</span>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/50 border border-white/20 p-4 rounded-xl flex items-start gap-3 backdrop-blur-sm">
          <span className="material-symbols-outlined text-[#004ac6]" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
          <div>
            <p className="text-[10px] font-bold text-[#181c20]">Ubicación Actual</p>
            <p className="text-[10px] text-[#434655]">Bogotá, Colombia</p>
          </div>
        </div>
        <div className="bg-white/50 border border-white/20 p-4 rounded-xl flex items-start gap-3 backdrop-blur-sm">
          <span className="material-symbols-outlined text-[#004ac6]" style={{ fontVariationSettings: "'FILL' 1" }}>devices</span>
          <div>
            <p className="text-[10px] font-bold text-[#181c20]">Dispositivo</p>
            <p className="text-[10px] text-[#434655]">Navegador Reconocido</p>
          </div>
        </div>
      </div>
    </div>
  )
}
