import { memo, type CSSProperties } from 'react'
import { cls } from '../util'
import { Icon, type IconName } from './Icon'

export type MarkerKind = 'fail' | 'listen' | 'update' | 'silence' | 'line'

const LOOK: Record<MarkerKind, { color: string; icon: IconName | null }> = {
  fail: { color: 'var(--bad)', icon: 'mark' },
  listen: { color: 'var(--warn)', icon: 'ear' },
  update: { color: 'var(--accent)', icon: 'alert' },
  silence: { color: 'var(--warn)', icon: null },
  line: { color: 'var(--faint)', icon: 'tick' },
}

export const Marker = memo(function Marker({ kind, left, width, title, onClick }: { kind: MarkerKind; left: number; width?: number; title: string; onClick?: () => void }) {
  const look = LOOK[kind]
  const style = { left, '--m': look.color, width: width !== undefined ? Math.max(3, width) : undefined } as CSSProperties
  return (
    <button type="button" className={cls('marker', kind === 'silence' && 'silence')} style={style} title={title} aria-label={title} onClick={onClick}>
      {look.icon && <Icon name={look.icon} size={kind === 'line' ? 12 : 11} strokeWidth={kind === 'listen' ? 2.4 : 2} />}
    </button>
  )
})
