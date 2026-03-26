import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('should render the dashboard title', () => {
    render(<App />)
    expect(screen.getByText('Financial Risk Dashboard')).toBeInTheDocument()
  })

  it('should render the setup complete message', () => {
    render(<App />)
    expect(screen.getByText(/Dashboard setup complete/i)).toBeInTheDocument()
  })
})
