import React from 'react'
import { useAuthStore } from '../../store/authStore'
import { Link } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
  currentStep?: number
  totalSteps?: number
  stepLabels?: string[]
}

export function Layout({ children, currentStep, totalSteps, stepLabels }: LayoutProps) {
  const logout = useAuthStore((s) => s.logout)

  return (
    <div className="bg-[#f7f9fe] antialiased min-h-screen flex flex-col font-['Inter']">
      {/* TopNavBar */}
      <header className="fixed top-0 w-full z-50 bg-[#f7f9fe]/80 backdrop-blur-md shadow-[0_12px_32px_-4px_rgba(0,42,198,0.08)]">
        <nav className="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold tracking-tight text-[#181c20]">Motor de Cumplimiento</span>
            <div className="hidden md:flex gap-6 items-center">
              <Link className="text-[#434655] hover:text-[#004ac6] transition-colors font-medium text-sm" to="/liquidacion">Profile</Link>
              <Link className="text-[#004ac6] border-b-2 border-[#004ac6] pb-1 font-semibold text-sm" to="/liquidacion">Contracts</Link>
              <Link className="text-[#434655] hover:text-[#004ac6] transition-colors font-medium text-sm" to="/liquidacion">Period</Link>
              <Link className="text-[#434655] hover:text-[#004ac6] transition-colors font-medium text-sm" to="/liquidacion">Protection Floor</Link>
              <Link className="text-[#434655] hover:text-[#004ac6] transition-colors font-medium text-sm" to="/liquidacion">Result</Link>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="material-symbols-outlined text-[#004ac6] p-2 hover:bg-[#eceef3] rounded-lg transition-all">verified_user</button>
            <button className="material-symbols-outlined text-[#004ac6] p-2 hover:bg-[#eceef3] rounded-lg transition-all" onClick={logout}>account_circle</button>
          </div>
        </nav>
      </header>

      <main className="mt-24 px-6 md:px-12 flex-grow pb-12 max-w-7xl mx-auto w-full">
        {/* Step Indicator */}
        {totalSteps && (
          <div className="mb-10">
            <div className="flex items-center justify-between max-w-3xl">
              {Array.from({ length: totalSteps }).map((_, i) => {
                const stepIdx = i + 1
                const isActive = stepIdx === currentStep
                const isCompleted = stepIdx < (currentStep || 0)
                
                return (
                  <React.Fragment key={i}>
                    {i > 0 && <div className="h-[2px] flex-grow bg-slate-200 mx-4"></div>}
                    <div className={`flex flex-col items-center gap-2 ${isActive ? '' : 'opacity-40'}`}>
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${isActive ? 'bg-[#004ac6] text-white shadow-lg shadow-blue-200' : 'bg-slate-200 text-slate-600'}`}>
                        {stepIdx}
                      </div>
                      <span className={`text-xs ${isActive ? 'font-bold text-[#004ac6]' : 'font-semibold'}`}>
                        {stepLabels?.[i] || `Paso ${stepIdx}`}
                      </span>
                    </div>
                  </React.Fragment>
                )
              })}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Main Content */}
          <div className="lg:col-span-8 space-y-6">
            {children}
          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-4 space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-[0_12px_32px_-4px_rgba(0,74,198,0.08)] border border-blue-50">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <span className="material-symbols-outlined text-[#004ac6]">verified_user</span>
                </div>
                <h3 className="font-bold text-[#181c20]">Validación de Riesgo</h3>
              </div>
              <p className="text-sm text-[#434655] leading-relaxed mb-6">
                El Nivel ARL es crítico para el cálculo de su seguridad social. Asegúrese de que coincida con la actividad económica reportada en el RUT.
              </p>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded-lg">
                  <span className="text-[#434655]">Contratos activos</span>
                  <span className="font-bold">03</span>
                </div>
                <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded-lg border-l-4 border-blue-600">
                  <span className="text-[#434655]">Riesgo Máximo</span>
                  <span className="font-bold text-[#004ac6]">V</span>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden h-48 rounded-xl bg-blue-600 shadow-lg flex flex-col justify-end p-6">
               <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-blue-800 opacity-90"></div>
               <div className="relative z-10">
                <h4 className="text-white font-bold text-lg leading-tight mb-1">Clarity in Every Digit</h4>
                <p className="text-white/80 text-xs">Su información está encriptada y validada contra estándares de la UGPP.</p>
              </div>
            </div>
          </aside>
        </div>
      </main>

      <footer className="bg-[#f1f4f9] w-full py-8 mt-auto flex flex-col md:flex-row justify-between items-center px-12 border-t border-slate-200/20 text-xs tracking-wide">
        <div className="flex flex-col gap-1 mb-4 md:mb-0">
          <span className="font-bold text-[#181c20]">Motor de Cumplimiento</span>
          <span className="text-[#434655]">© 2024 Motor de Cumplimiento - The Sentinel’s Clarity</span>
        </div>
        <div className="flex gap-8">
          <a className="text-[#434655] hover:underline hover:text-[#004ac6] transition-opacity" href="#">Privacy Policy</a>
          <a className="text-[#434655] hover:underline hover:text-[#004ac6] transition-opacity" href="#">Terms of Service</a>
          <a className="text-[#434655] hover:underline hover:text-[#004ac6] transition-opacity" href="#">Security Standards</a>
        </div>
      </footer>
    </div>
  )
}
