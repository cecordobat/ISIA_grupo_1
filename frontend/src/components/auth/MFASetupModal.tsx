import { useEffect, useState } from 'react'
import { authApi, type MFASetupResponse } from '../../api/auth'

interface Props {
  onComplete: () => void
  onCancel: () => void
}

export function MFASetupModal({ onComplete, onCancel }: Props) {
  const [data, setData] = useState<MFASetupResponse | null>(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSetup = async () => {
      try {
        setData(await authApi.setupMFA())
      } catch {
        setError('No se pudo iniciar la configuracion de MFA.')
      }
    }
    void fetchSetup()
  }, [])

  const handleActivate = async () => {
    setLoading(true)
    setError(null)
    try {
      await authApi.activateMFA(code)
      onComplete()
    } catch {
      setError('Codigo invalido. Verifique su aplicacion.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="wizard-step" style={{ border: '2px solid var(--primary)' }}>
      <h2>Configurar Segundo Factor (MFA)</h2>
      <p className="step-description">
        Proteja su cuenta de contador. Escanee el codigo QR con su aplicacion de autenticacion.
      </p>

      {error && <div className="error-banner">{error}</div>}

      {data ? (
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              background: '#eee',
              padding: '2rem',
              marginBottom: '1.5rem',
              borderRadius: '8px',
              display: 'inline-block',
            }}
          >
            <div style={{ fontSize: '0.8rem', wordBreak: 'break-all', maxWidth: '300px' }}>
              <code>{data.totp_uri}</code>
            </div>
            <p style={{ marginTop: '1rem', fontWeight: 'bold' }}>Secreto: {data.secret}</p>
          </div>

          <div className="field" style={{ maxWidth: '200px', margin: '0 auto 1.5rem' }}>
            <label htmlFor="mfa-code">Codigo de validacion</label>
            <input
              id="mfa-code"
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
            <button className="btn-secondary" onClick={onCancel}>
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <div className="loading-state">Iniciando configuracion...</div>
      )}
    </div>
  )
}
