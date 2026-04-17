import { useState, useEffect } from 'react'
import { apiClient } from '../../api/client'

interface MFASetupResponse {
  totp_uri: string
  secret: string
  mensaje: string
}

export function MFASetupModal({ onComplete, onCancel }: { onComplete: () => void, onCancel: () => void }) {
  const [data, setData] = useState<MFASetupResponse | null>(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSetup = async () => {
      try {
        const { data } = await apiClient.post<MFASetupResponse>('/auth/mfa/setup')
        setData(data)
      } catch {
        setError('No se pudo iniciar la configuración de MFA.')
      }
    }
    void fetchSetup()
  }, [])

  const handleActivate = async () => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.post('/auth/mfa/activate', { codigo: code })
      onComplete()
    } catch {
      setError('Código inválido. Verifique su aplicación.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wizard-step" style={{ border: '2px solid var(--primary)' }}>
      <h2>Configurar Segundo Factor (MFA)</h2>
      <p className="step-description">
        Proteja su cuenta de Contador. Escanee el código QR con su aplicación de autenticación (Google Authenticator, Authy, etc.).
      </p>

      {error && <div className="error-banner">{error}</div>}

      {data ? (
        <div style={{ textAlign: 'center' }}>
          <div style={{ background: '#eee', padding: '2rem', marginBottom: '1.5rem', borderRadius: '8px', display: 'inline-block' }}>
            {/* Aquí iría un componente de QR real en el futuro, por ahora simulamos con el URI */}
            <div style={{ fontSize: '0.8rem', wordBreak: 'break-all', maxWidth: '300px' }}>
              <code>{data.totp_uri}</code>
            </div>
            <p style={{ marginTop: '1rem', fontWeight: 'bold' }}>Secreto: {data.secret}</p>
          </div>

          <div className="field" style={{ maxWidth: '200px', margin: '0 auto 1.5rem' }}>
            <label>Código de Validación</label>
            <input
              type="text"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="000000"
              style={{ textAlign: 'center', fontSize: '1.2rem' }}
            />
          </div>

          <div className="wizard-actions">
            <button className="btn-primary" onClick={handleActivate} disabled={loading || code.length !== 6}>
              {loading ? 'Activando...' : 'Activar MFA'}
            </button>
            <button className="btn-secondary" onClick={onCancel}>Cancelar</button>
          </div>
        </div>
      ) : (
        <div className="loading-state">Iniciando configuración...</div>
      )}
    </div>
  )
}
