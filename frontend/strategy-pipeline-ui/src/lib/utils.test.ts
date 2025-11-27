/**
 * Tests for utility functions
 */

import { describe, it, expect } from 'vitest'
import { cn } from '@/lib/utils'

describe('Utils', () => {
  describe('cn', () => {
    it('merges class names correctly', () => {
      const result = cn('text-red-500', 'bg-blue-500')
      expect(result).toContain('text-red-500')
      expect(result).toContain('bg-blue-500')
    })

    it('handles conditional classes', () => {
      const result = cn('base-class', false && 'conditional-class', 'always-class')
      expect(result).toContain('base-class')
      expect(result).toContain('always-class')
      expect(result).not.toContain('conditional-class')
    })

    it('merges conflicting Tailwind classes correctly', () => {
      // twMerge should keep the last class when there's a conflict
      const result = cn('p-4', 'p-8')
      expect(result).toBe('p-8')
    })

    it('handles arrays of class names', () => {
      const result = cn(['class1', 'class2'], 'class3')
      expect(result).toContain('class1')
      expect(result).toContain('class2')
      expect(result).toContain('class3')
    })

    it('filters out undefined and null values', () => {
      const result = cn('valid-class', undefined, null, 'another-valid-class')
      expect(result).toContain('valid-class')
      expect(result).toContain('another-valid-class')
    })

    it('handles empty input', () => {
      const result = cn()
      expect(result).toBe('')
    })
  })
})

