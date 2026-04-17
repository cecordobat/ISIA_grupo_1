import { useEffect, useState } from 'react'
import { listarSnapshots, crearSnapshot, SnapshotNormativo, SnapshotCreate, listarCIIU, crearCIIU, CIIU } from '../api/admin'

export function AdminParametrosPage() {
  const [snapshots, setSnapshots] = useState<SnapshotNormativo[]>([])
  const [ciius, setCiius] = useState<CIIU[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'snapshots' | 'ciiu'>('snapshots')
  
  const [formSnapshot, setFormSnapshot] = useState<SnapshotCreate>({
    smmlv: 1300000,
    uvt: 47065,
    pct_salud: 0.125,
    pct_pension: 0.16,
    tabla_arl_json: '{"I":"0.00522","II":"0.01044","III":"0.02436","IV":"0.04350","V":"0.06960"}',
    vigencia_anio: new Date().getFullYear(),
  })

  const [formCIIU, setFormCIIU] = useState({
    codigo_ciiu: '',
    descripcion: '',
    pct_costos_presuntos: 0,
    vigente_desde: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    const cargar = async () => {
      setLoading(true)
      try {
        const [s, c] = await Promise.all([listarSnapshots(), listarCIIU()])
        setSnapshots(s)
        setCiius(c)
      } catch {
        setError('Error al conectar con los servicios administrativos.')
      } finally {
        setLoading(false)
      }
    }
    void cargar()
  }, [])

  const handleCrearSnapshot = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const nuevo = await crearSnapshot(formSnapshot)
      setSnapshots([nuevo, ...snapshots])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear el snapshot normativo.')
    }
  }

  const handleCrearCIIU = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const nuevo = await crearCIIU(formCIIU)
      setCiius([...ciius, nuevo])
      setFormCIIU({ ...formCIIU, codigo_ciiu: '', descripcion: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrar el código CIIU.')
    }
  }

  return (
    <div className="bg-[#f7f9fe] min-h-screen text-[#181c20] font-['Inter']">
      <div className="max-w-7xl mx-auto p-8 space-y-8">
        {/* Header Section */}
        <div className="flex justify-between items-end pb-4 border-b border-slate-200">
           <div>
             <h1 className="text-3xl font-extrabold tracking-tight">Gobernanza Normativa</h1>
             <p className="text-slate-500 mt-1">Administración de parámetros de ley y tablas maestras (INV-04 Safe).</p>
           </div>
           <div className="flex bg-white p-1 rounded-xl shadow-sm border border-slate-100">
              <button 
                onClick={() => setActiveTab('snapshots')}
                className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'snapshots' ? 'bg-[#004ac6] text-white' : 'text-slate-400 hover:text-slate-600'}`}
              >
                Snapshots Anuales
              </button>
              <button 
                onClick={() => setActiveTab('ciiu')}
                className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'ciiu' ? 'bg-[#004ac6] text-white' : 'text-slate-400 hover:text-slate-600'}`}
              >
                Catálogo CIIU
              </button>
           </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 p-4 rounded-xl flex items-center gap-3 animate-in fade-in transition-all">
            <span className="material-symbols-outlined">error</span>
            <span className="text-sm font-bold">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Column */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] border border-slate-50 sticky top-8">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#004ac6]">add_circle</span>
                {activeTab === 'snapshots' ? 'Nuevo Snapshot Anual' : 'Registrar Código CIIU'}
              </h3>
              
              {activeTab === 'snapshots' ? (
                <form onSubmit={handleCrearSnapshot} className="space-y-4">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Año de Vigencia</label>
                    <input 
                      type="number"
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none font-bold"
                      value={formSnapshot.vigencia_anio}
                      onChange={e => setFormSnapshot({...formSnapshot, vigencia_anio: +e.target.value})}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">SMMLV (COP)</label>
                      <input 
                        type="number"
                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                        value={formSnapshot.smmlv}
                        onChange={e => setFormSnapshot({...formSnapshot, smmlv: +e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">UVT (COP)</label>
                      <input 
                        type="number"
                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                        value={formSnapshot.uvt}
                        onChange={e => setFormSnapshot({...formSnapshot, uvt: +e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">% Salud</label>
                      <input 
                        type="number" step="0.001"
                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                        value={formSnapshot.pct_salud}
                        onChange={e => setFormSnapshot({...formSnapshot, pct_salud: +e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">% Pensión</label>
                      <input 
                        type="number" step="0.001"
                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                        value={formSnapshot.pct_pension}
                        onChange={e => setFormSnapshot({...formSnapshot, pct_pension: +e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Tabla ARL JSON</label>
                    <textarea 
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none text-xs font-mono"
                      rows={4}
                      value={formSnapshot.tabla_arl_json}
                      onChange={e => setFormSnapshot({...formSnapshot, tabla_arl_json: e.target.value})}
                    />
                  </div>
                  <button type="submit" className="w-full py-4 bg-[#004ac6] text-white rounded-xl font-bold shadow-lg shadow-blue-100 mt-2">Publicar Snapshot</button>
                </form>
              ) : (
                <form onSubmit={handleCrearCIIU} className="space-y-4">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Código CIIU</label>
                    <input 
                      placeholder="Ej: 6201"
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none font-bold"
                      value={formCIIU.codigo_ciiu}
                      onChange={e => setFormCIIU({...formCIIU, codigo_ciiu: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Descripción DIAN</label>
                    <textarea 
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none text-sm"
                      rows={3}
                      value={formCIIU.descripcion}
                      onChange={e => setFormCIIU({...formCIIU, descripcion: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">% Costos Presuntos (Art. 139 Ley 2010)</label>
                    <input 
                      type="number" step="0.01"
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                      value={formCIIU.pct_costos_presuntos}
                      onChange={e => setFormCIIU({...formCIIU, pct_costos_presuntos: +e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Vigente Desde</label>
                    <input 
                      type="date"
                      className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-100 outline-none"
                      value={formCIIU.vigente_desde}
                      onChange={e => setFormCIIU({...formCIIU, vigente_desde: e.target.value})}
                    />
                  </div>
                  <button type="submit" className="w-full py-4 bg-[#004ac6] text-white rounded-xl font-bold shadow-lg shadow-blue-100 mt-2">Registrar Código</button>
                </form>
              )}
            </div>
          </div>

          {/* List Column */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.06)] overflow-hidden border border-slate-50">
              {activeTab === 'snapshots' ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 font-bold text-[10px] text-slate-400 uppercase tracking-widest">
                      <tr>
                        <th className="px-6 py-4">Año</th>
                        <th className="px-6 py-4">SMMLV</th>
                        <th className="px-6 py-4">UVT</th>
                        <th className="px-6 py-4">Aportes %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {snapshots.map(s => (
                        <tr key={s.id} className="hover:bg-blue-50/10 transition-colors">
                          <td className="px-6 py-4 font-black text-lg text-[#004ac6]">{s.vigencia_anio}</td>
                          <td className="px-6 py-4 text-sm font-semibold">${s.smmlv.toLocaleString()}</td>
                          <td className="px-6 py-4 text-sm font-semibold">${s.uvt.toLocaleString()}</td>
                          <td className="px-6 py-4 text-xs font-medium text-slate-500">
                             Salud: {(s.pct_salud * 100).toFixed(1)}% | Pensión: {(s.pct_pension * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 font-bold text-[10px] text-slate-400 uppercase tracking-widest">
                      <tr>
                        <th className="px-6 py-4">CIIU</th>
                        <th className="px-6 py-4">Descripción</th>
                        <th className="px-6 py-4">% Costos</th>
                        <th className="px-6 py-4">Vigencia</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {ciius.map(c => (
                        <tr key={c.codigo_ciiu} className="hover:bg-blue-50/10 transition-colors">
                          <td className="px-6 py-4 font-bold text-[#004ac6]">{c.codigo_ciiu}</td>
                          <td className="px-6 py-4 text-xs font-medium text-slate-600 max-w-xs truncate">{c.descripcion}</td>
                          <td className="px-6 py-4 text-sm font-bold text-green-700">{(c.pct_costos_presuntos * 100).toFixed(0)}%</td>
                          <td className="px-6 py-4 text-xs text-slate-400">{c.vigente_desde}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {loading && <div className="p-12 text-center text-slate-300 font-bold animate-pulse">Sincronizando con el motor normativo...</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
