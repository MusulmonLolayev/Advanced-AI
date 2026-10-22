import type { HTMLAttributes, ReactNode } from 'react'
import { cls } from '../util'

export type ChipTone = 'neutral' | 'good' | 'warn' | 'bad' | 'accent' | 'empty' | 'you' | 'clone'

export function Chip({ tone = 'neutral', plain, className, children, ...rest }: { tone?: ChipTone; plain?: boolean; children: ReactNode } & HTMLAttributes<HTMLSpanElement>) {
  return (
    <span className={cls('chip', tone !== 'neutral' && tone, plain && 'plain', className)} {...rest}>
      {children}
    </span>
  )
}
