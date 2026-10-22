import type { CSSProperties } from 'react'
import { cls } from '../util'

/** A level meter: `level` and `peak` are 0-1. Vertical by default. */
export function Meter({ level, peak, horizontal, label }: { level: number; peak?: number; horizontal?: boolean; label: string }) {
  const style = { '--level': level, '--peak': peak ?? level } as CSSProperties
  return (
    <div className={cls('meter', horizontal ? 'h' : 'v')} style={style} role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={1} aria-valuenow={Number(level.toFixed(2))}>
      <div className="meter-fill" />
      {!horizontal && peak !== undefined && <div className="meter-peak" />}
    </div>
  )
}
