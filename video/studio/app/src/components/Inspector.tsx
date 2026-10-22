import type { ReactNode } from 'react'

/** A collapsible section of the right-hand inspector. */
export function InspectorSection({ title, count, actions, open = true, children }: { title: string; count?: ReactNode; actions?: ReactNode; open?: boolean; children: ReactNode }) {
  return (
    <details className="insp-sec" open={open}>
      <summary>
        <span>{title}</span>
        {count !== undefined && <span className="count dim">{count}</span>}
        <span className="grow" />
        {actions}
      </summary>
      <div className="insp-body">{children}</div>
    </details>
  )
}
