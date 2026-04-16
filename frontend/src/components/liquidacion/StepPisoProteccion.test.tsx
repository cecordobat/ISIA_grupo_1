/**
 * Tests del componente StepPisoProteccion.
 * Verifica el componente UI más crítico del sistema (HU-04, RN-06).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { StepPisoProteccion } from './StepPisoProteccion'

describe('StepPisoProteccion', () => {
  it('muestra advertencia que BEPS no acumula semanas de pensión', () => {
    render(
      <StepPisoProteccion
        onSelectOpcion={vi.fn()}
        opcionSeleccionada={null}
        onConfirmar={vi.fn()}
      />
    )
    expect(
      screen.getByText(/Esta opción NO acumula semanas de pensión/i)
    ).toBeInTheDocument()
  })

  it('el botón confirmar está deshabilitado sin opción seleccionada', () => {
    render(
      <StepPisoProteccion
        onSelectOpcion={vi.fn()}
        opcionSeleccionada={null}
        onConfirmar={vi.fn()}
      />
    )
    const btn = screen.getByRole('button', { name: /Confirmar/i })
    expect(btn).toBeDisabled()
  })

  it('habilita el botón al seleccionar BEPS', () => {
    render(
      <StepPisoProteccion
        onSelectOpcion={vi.fn()}
        opcionSeleccionada="BEPS"
        onConfirmar={vi.fn()}
      />
    )
    const btn = screen.getByRole('button', { name: /Confirmar/i })
    expect(btn).not.toBeDisabled()
  })

  it('habilita el botón al seleccionar SMMLV_COMPLETO', () => {
    render(
      <StepPisoProteccion
        onSelectOpcion={vi.fn()}
        opcionSeleccionada="SMMLV_COMPLETO"
        onConfirmar={vi.fn()}
      />
    )
    const btn = screen.getByRole('button', { name: /Confirmar/i })
    expect(btn).not.toBeDisabled()
  })

  it('llama a onSelectOpcion al hacer clic en opción BEPS', () => {
    const onSelect = vi.fn()
    render(
      <StepPisoProteccion
        onSelectOpcion={onSelect}
        opcionSeleccionada={null}
        onConfirmar={vi.fn()}
      />
    )
    const radioBEPS = screen.getByLabelText(/Piso de Protección Social.*BEPS/i)
    fireEvent.click(radioBEPS)
    expect(onSelect).toHaveBeenCalledWith('BEPS')
  })

  it('llama a onConfirmar al hacer clic en el botón con opción seleccionada', () => {
    const onConfirmar = vi.fn()
    render(
      <StepPisoProteccion
        onSelectOpcion={vi.fn()}
        opcionSeleccionada="SMMLV_COMPLETO"
        onConfirmar={onConfirmar}
      />
    )
    fireEvent.click(screen.getByRole('button', { name: /Confirmar/i }))
    expect(onConfirmar).toHaveBeenCalled()
  })
})
