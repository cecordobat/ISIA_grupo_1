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
        navigate(rolRespuesta === 'CONTADOR' ? '/contador' : '/liquidacion')
      } else {
        setError('Error al crear la cuenta. Intente de nuevo.')
      }
    } catch {
      setError('Error al registrar la cuenta. Es posible que el correo ya este en uso.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Registro</h1>
        <p className="subtitle">Motor de Cumplimiento - Crear nueva cuenta</p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="nombre">Nombre Completo</label>
            <input
              id="nombre"
              type="text"
              value={nombreCompleto}
              onChange={(e) => setNombreCompleto(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="field">
            <label htmlFor="rol">Tipo de cuenta</label>
            <select id="rol" value={rol} onChange={(e) => setRol(e.target.value as RolUsuario)}>
              <option value="CONTRATISTA">Contratista</option>
              <option value="CONTADOR">Contador</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Contrasena</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-banner">{error}</div>}
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Registrando...' : 'Registrarse'}
          </button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center' }}>
          Ya tienes cuenta? <Link to="/login">Inicia sesion aqui</Link>
        </p>
      </div>
    </div>
  )
}
