/* eslint-env jest */
import { escapeHTML } from '@/utils/sanitize'

describe('escapeHTML', () => {
  it('does not throw for null input', () => {
    expect(() => escapeHTML(null)).not.toThrow()
  })

  it('does not throw for undefined input', () => {
    expect(() => escapeHTML(undefined)).not.toThrow()
  })

  it('does not throw for numeric input', () => {
    expect(() => escapeHTML(42)).not.toThrow()
  })
})

