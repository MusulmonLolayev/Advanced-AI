import type { ComponentProps, ReactNode } from 'react'
import { cls } from '../util'
import { Icon, type IconName } from './Icon'

type Props = ComponentProps<'button'> & {
  variant?: 'default' | 'primary' | 'ghost' | 'danger' | 'record'
  small?: boolean
  icon?: IconName
  children?: ReactNode
}

export function Button({ variant = 'default', small, icon, className, children, ...rest }: Props) {
  return (
    <button type="button" className={cls('btn', variant !== 'default' && variant, small && 'small', className)} {...rest}>
      {icon && <Icon name={icon} size={small ? 12 : 14} />}
      {children}
    </button>
  )
}
