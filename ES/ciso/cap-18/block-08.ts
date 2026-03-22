// Extraído de: LibroCISO/cap-18-react-grc.md
// Ejemplo: test de accesibilidad para el formulario de DPIA
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { DPIAForm } from '@/modules/privacy/DPIAForm'

expect.extend(toHaveNoViolations)

test('DPIAForm no tiene violaciones WCAG 2.1 AA', async () => {
  const { container } = render(<DPIAForm onSubmit={jest.fn()} />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
