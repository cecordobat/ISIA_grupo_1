/**
 * Estado del wizard de liquidación.
 * El wizard retiene el estado en el cliente hasta que el usuario confirma.
 * Solo se persiste en BD al completar el paso final (INV-03).
 */
import { create } from 'zustand'
import type { LiquidacionResponse, OpcionPiso } from '../api/liquidaciones'

interface WizardState {
  // Paso actual del wizard (1..6)
  paso: number
  // Datos del período
  perfilId: string | null
  anio: number
  mes: number
  // Decisión del Piso de Protección Social (solo si ingreso < SMMLV)
  opcionPiso: OpcionPiso | null
  // Resultado del engine (disponible después de calcular)
  resultado: LiquidacionResponse | null
  // Si el ingreso requiere decisión de Piso
  requiereDecisionPiso: boolean

  // Acciones
  setPeriodo: (perfilId: string, anio: number, mes: number) => void
  setOpcionPiso: (opcion: OpcionPiso) => void
  setResultado: (resultado: LiquidacionResponse) => void
  setRequiereDecisionPiso: (requiere: boolean) => void
  avanzarPaso: () => void
  retrocederPaso: () => void
  resetear: () => void
}

export const useLiquidacionStore = create<WizardState>((set) => ({
  paso: 1,
  perfilId: null,
  anio: new Date().getFullYear(),
  mes: new Date().getMonth() + 1,
  opcionPiso: null,
  resultado: null,
  requiereDecisionPiso: false,

  setPeriodo: (perfilId, anio, mes) => set({ perfilId, anio, mes }),
  setOpcionPiso: (opcion) => set({ opcionPiso: opcion }),
  setResultado: (resultado) => set({ resultado }),
  setRequiereDecisionPiso: (requiere) => set({ requiereDecisionPiso: requiere }),
  avanzarPaso: () => set((s) => ({ paso: Math.min(s.paso + 1, 6) })),
  retrocederPaso: () => set((s) => ({ paso: Math.max(s.paso - 1, 1) })),
  resetear: () =>
    set({
      paso: 1,
      perfilId: null,
      opcionPiso: null,
      resultado: null,
      requiereDecisionPiso: false,
    }),
}))
