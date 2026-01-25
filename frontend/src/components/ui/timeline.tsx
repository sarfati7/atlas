import * as React from 'react'
import { cn } from '@/lib/utils'

interface TimelineProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Timeline({ className, children, ...props }: TimelineProps) {
  return (
    <div className={cn('relative space-y-4 pl-6', className)} {...props}>
      {/* Vertical line connecting timeline items */}
      <div className="absolute left-[9px] top-2 bottom-2 w-px bg-border" />
      {children}
    </div>
  )
}

interface TimelineItemProps extends React.HTMLAttributes<HTMLDivElement> {
  active?: boolean
}

export function TimelineItem({ className, active, children, ...props }: TimelineItemProps) {
  return (
    <div className={cn('relative', className)} {...props}>
      {/* Circle indicator */}
      <div
        className={cn(
          'absolute -left-6 top-1.5 h-3 w-3 rounded-full border-2',
          active
            ? 'border-primary bg-primary'
            : 'border-muted-foreground bg-background'
        )}
      />
      {children}
    </div>
  )
}
