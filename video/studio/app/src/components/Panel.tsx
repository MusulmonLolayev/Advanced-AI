import type { ReactNode } from 'react'
import { cls } from '../util'

export function Panel({ title, actions, className, bodyClass, children, ...rest }: { title?: ReactNode; actions?: ReactNode; className?: string; bodyClass?: string; children: ReactNode } & { 'aria-label'?: string }) {
  return (
    <section className={cls('panel', className)} {...rest}>
      {title && (
        <header className="panel-head">
          <span>{title}</span>
          <span className="grow" />
          {actions}
        </header>
      )}
      <div className={cls('panel-body', bodyClass)}>{children}</div>
    </section>
  )
}
