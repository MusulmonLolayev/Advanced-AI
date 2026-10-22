import type { ReactNode } from 'react'
import { cls } from '../util'

export type TabDef<K extends string> = { id: K; label: ReactNode; hint?: string }

export function Tabs<K extends string>({ tabs, value, onChange, pills, label }: { tabs: TabDef<K>[]; value: K; onChange: (k: K) => void; pills?: boolean; label: string }) {
  return (
    <div className={cls('tabs', pills && 'pills')} role="tablist" aria-label={label}>
      {tabs.map((t) => (
        <button key={t.id} type="button" role="tab" className="tab" aria-selected={t.id === value} onClick={() => onChange(t.id)}>
          {t.label}
          {t.hint && <kbd>{t.hint}</kbd>}
        </button>
      ))}
    </div>
  )
}
