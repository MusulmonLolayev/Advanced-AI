import type { CSSProperties, ReactNode } from 'react'

/** One lane of the timeline: a sticky header on the left and a body as wide as the time it shows. */
export function Track({ label, sub, color, height, width, children }: { label: string; sub?: string; color?: string; height: number; width: number; children?: ReactNode }) {
  return (
    <div className="track" style={{ height }}>
      <div className="track-head">
        <span>
          {color && <i className="swatch" style={{ background: color }} />}
          {label}
        </span>
        {sub && <small>{sub}</small>}
      </div>
      <div className="track-body" style={{ width, height }}>
        {children}
      </div>
    </div>
  )
}

export type { CSSProperties }
