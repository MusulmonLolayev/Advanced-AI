import { memo, type CSSProperties, type ReactNode } from 'react'
import { cls } from '../util'

type Props = { left: number; width: number; color?: string; selected?: boolean; muted?: boolean; section?: boolean; title?: string; onClick?: () => void; children?: ReactNode; top?: number; bottom?: number }

/** A clip on a lane: positioned in pixels by the caller (time x pixels-per-second). */
export const Clip = memo(function Clip({ left, width, color, selected, muted, section, title, onClick, children, top, bottom }: Props) {
  const style = { left, width: Math.max(2, width), '--clip-color': color, top, bottom } as CSSProperties
  return (
    <button type="button" className={cls('clip', selected && 'selected', muted && 'muted', section && 'section', width < 26 && 'tiny')} style={style} title={title} aria-pressed={selected} onClick={onClick}>
      {children}
    </button>
  )
})
