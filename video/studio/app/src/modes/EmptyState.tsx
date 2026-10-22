import type { ReactNode } from 'react'

export function EmptyState({ title, children, tone }: { title: string; children?: ReactNode; tone?: 'bad' }) {
  return (
    <div className="empty-state">
      <h2 className={tone}>{title}</h2>
      {children}
    </div>
  )
}
