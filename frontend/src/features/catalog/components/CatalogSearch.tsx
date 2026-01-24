/**
 * CatalogSearch - Search input with 300ms debounce.
 */

import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'

interface CatalogSearchProps {
  value: string
  onChange: (value: string) => void
}

export function CatalogSearch({ value, onChange }: CatalogSearchProps) {
  const [localValue, setLocalValue] = useState(value)

  // Sync external value changes
  useEffect(() => {
    setLocalValue(value)
  }, [value])

  // Debounce local changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [localValue, value, onChange])

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        type="search"
        placeholder="Search catalog..."
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        className="pl-9 w-full max-w-sm"
      />
    </div>
  )
}
