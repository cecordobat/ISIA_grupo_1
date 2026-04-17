import { useEffect, useState } from 'react'
import { contadorApi } from '../api/contador'
import type { ClienteContador } from '../api/contador'
import { MFASetupModal } from '../components/auth/MFASetupModal'
import { HistorialLiquidaciones } from '../components/liquidacion/HistorialLiquidaciones'
import { useAuthStore } from '../store/authStore'

export function ContadorDashboardPage() {
  const logout = useAuthStore((s) => s.logout)
  const [clientes, setClientes] = useState<ClienteContador[]>([])
  const [seleccionado, setSeleccionado] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showMFASetup, setShowMFASetup] = useState(false)

  useEffect(() => {
    let activo = true
    const cargar = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await contadorApi.listarClientes()
        if (!activo) return
        setClientes(data)
        setSeleccionado(data[0]?.perfil_id ?? null)
      } catch {
        if (!activo) return
        setError('No se pudieron cargar los clientes autorizados.')
      } finally {
        if (activo) setLoading(false)
      }
    }
    void cargar()
    return () => {
      activo = false
    }
  }, [])

  return (
    <div className="bg-[#f7f9fe] text-[#181c20] min-h-screen flex font-['Inter']">
      {/* SideNavBar */}
      <aside className="h-full w-64 fixed left-0 top-0 bg-[#1e3a5f] flex flex-col py-6 px-4 z-[60] shadow-xl">
        <div className="mb-10 px-2">
          <h1 className="text-xl font-bold text-white tracking-tight">Motor de Cumplimiento</h1>
          <p className="text-[10px] text-blue-100/60 uppercase tracking-widest mt-1">THE SENTINEL'S CLARITY</p>
        </div>
        
        <nav className="flex-1 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/10 text-white font-semibold transition-colors">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="text-sm">Dashboard</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-blue-100/70 hover:bg-white/5 transition-colors">
            <span className="material-symbols-outlined">fact_check</span>
            <span className="text-sm">Auditorías</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-blue-100/70 hover:bg-white/5 transition-colors">
            <span className="material-symbols-outlined">groups</span>
            <span className="text-sm">Contratistas</span>
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-blue-100/70 hover:bg-white/5 transition-colors">
            <span className="material-symbols-outlined">history</span>
            <span className="text-sm">Historial</span>
          </button>

          <div className="pt-6 mt-6 border-t border-white/10">
            <p className="text-[10px] font-bold text-blue-100/40 uppercase tracking-widest px-3 mb-2">Seguridad</p>
            <button 
              onClick={() => setShowMFASetup(true)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-blue-100/70 hover:bg-white/5 transition-colors"
            >
              <span className="material-symbols-outlined">security</span>
              <span className="text-sm">Configurar MFA</span>
            </button>
            <button 
              onClick={logout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-red-300/70 hover:bg-white/5 transition-colors"
            >
              <span className="material-symbols-outlined">logout</span>
              <span className="text-sm">Cerrar sesión</span>
            </button>
          </div>
        </nav>
      </aside>

      {/* TopAppBar */}
      <header className="fixed top-0 right-0 left-64 z-50 flex justify-between items-center h-16 px-8 bg-[#f7f9fe]/80 backdrop-blur-md shadow-sm">
        <div className="flex items-center gap-8">
          <h2 className="text-lg font-semibold text-slate-900 border-l-4 border-[#004ac6] pl-4">Portal del Contador</h2>
        </div>
        <div className="flex items-center gap-4">
          <button className="material-symbols-outlined text-slate-500 p-2 hover:bg-slate-100 rounded-full">notifications</button>
          <div className="h-8 w-[1px] bg-slate-200 mx-1"></div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-xs font-bold">C. Rodríguez</p>
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Senior Auditor</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-[#004ac6] font-bold shadow-sm">CR</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="ml-64 pt-16 flex-grow overflow-y-auto">
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="flex justify-between items-end pb-4">
            <div>
              <h3 className="text-3xl font-extrabold tracking-tight text-[#181c20]">Gestión de Contratistas</h3>
              <p className="text-slate-500 text-sm mt-1">Monitoreo de obligaciones y estado de liquidación tributaria.</p>
            </div>
            <button className="px-6 py-2.5 text-sm font-bold text-white bg-[#004ac6] rounded-xl shadow-lg shadow-blue-100 hover:scale-105 transition-all">
               Descargar Reporte Consolidado
            </button>
          </div>

          {/* Bento Grid Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1 bg-white p-6 rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] border border-blue-50/50 flex flex-col items-center justify-center">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">Compliance Health</p>
              <div className="relative w-28 h-28 flex items-center justify-center mb-4">
                 <svg className="w-full h-full -rotate-90">
                    <circle className="text-slate-100" cx="56" cy="56" fill="transparent" r="50" stroke="currentColor" strokeWidth="8"></circle>
                    <circle className="text-[#004ac6]" cx="56" cy="56" fill="transparent" r="50" stroke="currentColor" strokeWidth="8" strokeDasharray="314" strokeDashoffset="31"></circle>
                 </svg>
                 <span className="absolute text-2xl font-black text-[#181c20]">90%</span>
              </div>
              <p className="text-xs font-bold text-[#004ac6]">Documentación al día</p>
            </div>

            <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-[0_8px_20px_rgba(0,0,0,0.04)] border border-slate-50">
                <span className="material-symbols-outlined text-[#bc4800] mb-3">pending_actions</span>
                <h4 className="text-3xl font-black text-[#181c20]">{clientes.length}</h4>
                <p className="text-sm font-semibold text-slate-500">Pendientes Revisión</p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-[0_8px_20px_rgba(0,0,0,0.04)] border border-slate-50">
                <span className="material-symbols-outlined text-[#004ac6] mb-3">verified</span>
                <h4 className="text-3xl font-black text-[#181c20]">45</h4>
                <p className="text-sm font-semibold text-slate-500">Bajo Auditoría</p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-[0_8px_20px_rgba(0,0,0,0.04)] border border-slate-50">
                <span className="material-symbols-outlined text-green-600 mb-3">check_circle</span>
                <h4 className="text-3xl font-black text-[#181c20]">128</h4>
                <p className="text-sm font-semibold text-slate-500">Confirmadas UGPP</p>
              </div>
            </div>
          </div>

          {/* Table Container */}
          <div className="bg-white rounded-2xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] overflow-hidden border border-slate-50">
            <div className="px-6 py-4 bg-slate-50/50 flex justify-between items-center border-b border-slate-100">
               <h4 className="font-bold text-[#181c20]">Registro de Clientes autorizados</h4>
               <div className="relative">
                 <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-300 text-sm">search</span>
                 <input className="pl-9 pr-4 py-1.5 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-100 outline-none" placeholder="Buscar contratista..." />
               </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/30">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Nombre del Contratista</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Identificación</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Actividad CIIU</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Estado</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest text-right">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {loading ? (
                    <tr><td colSpan={5} className="px-6 py-10 text-center font-bold text-slate-300 animate-pulse">Consultando base de datos de contratistas...</td></tr>
                  ) : error ? (
                    <tr><td colSpan={5} className="px-6 py-10 text-center text-red-500 font-bold">{error}</td></tr>
                  ) : clientes.length === 0 ? (
                    <tr><td colSpan={5} className="px-6 py-10 text-center text-slate-400">Sin contratistas vinculados.</td></tr>
                  ) : (
                    clientes.map((cliente) => (
                      <tr 
                        key={cliente.perfil_id} 
                        className={`hover:bg-blue-50/20 transition-colors cursor-pointer ${seleccionado === cliente.perfil_id ? 'bg-blue-50/50' : ''}`}
                        onClick={() => setSeleccionado(cliente.perfil_id)}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-[#004ac6] font-bold text-[10px]">
                              {cliente.nombre_contratista.substring(0,2).toUpperCase()}
                            </div>
                            <span className="font-semibold text-sm">{cliente.nombre_contratista}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600 font-medium">{cliente.numero_documento}</td>
                        <td className="px-6 py-4 text-center">
                          <span className="bg-slate-100 px-3 py-1 rounded text-[10px] font-bold text-slate-600">{cliente.ciiu_codigo}</span>
                        </td>
                        <td className="px-6 py-4">
                           <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold bg-[#ffdbcd] text-[#943700]">
                             <span className="w-1.5 h-1.5 rounded-full bg-[#ba1a1a]"></span>
                             PENDIENTE_REVISION
                           </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button className="material-symbols-outlined text-slate-400 hover:text-[#004ac6] transition-colors">visibility</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Detailed View - Historial */}
          {seleccionado && (
            <div className="animate-in slide-in-from-bottom-4 duration-500">
               <HistorialLiquidaciones perfilId={seleccionado} />
            </div>
          )}
        </div>
      </main>

      {/* MFA Modal */}
      {showMFASetup && (
        <MFASetupModal
          onComplete={() => setShowMFASetup(false)}
          onCancel={() => setShowMFASetup(false)}
        />
      )}
    </div>
  )
}
