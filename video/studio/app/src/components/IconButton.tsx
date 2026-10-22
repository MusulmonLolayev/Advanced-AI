import type { ButtonHTMLAttributes } from 'react'
import { cls } from '../util'
import { Icon, type IconName } from './Icon'

type Props = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'title'> & { icon: IconName; label: string; on?: boolean; big?: boolean; size?: number }

/** An icon-only button. `label` is both the tooltip and the accessible name. */
export function IconButton({ icon, label, on, big, size, className, ...rest }: Props) {
  return (
    <button type="button" className={cls('icon-btn', on && 'on', big && 'big', className)} title={label} aria-label={label} aria-pressed={on} {...rest}>
      <Icon name={icon} size={size ?? (big ? 18 : 16)} />
    </button>
  )
}
