import { useEffect, useRef, type ReactNode } from 'react'
import { Button } from './Button'

/** The shell of the dialogs that host a panel (versions, tighten & nudge, script check, languages, recordings): a native
 *  <dialog> opened with showModal() like Dialog and TakeEditor, a title, the panel, and Close. Esc, the backdrop and Close all close it. */
export function PanelDialog({ title, sub, wide, onClose, children }: { title: ReactNode; sub?: ReactNode; wide?: boolean; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const d = ref.current
    if (d && !d.open) d.showModal()
  }, [])
  return (
    <dialog
      ref={ref}
      className={'dialog panel-dialog' + (wide ? ' wide' : '')}
      aria-label={typeof title === 'string' ? title : undefined}
      onCancel={(e) => {
        e.preventDefault()
        onClose()
      }}
      onClick={(e) => {
        if (e.target === ref.current) onClose()
      }}
      // the app listens for single keys on the document: keep them out while this is open
      onKeyDown={(e) => e.nativeEvent.stopPropagation()}
    >
      <div className="pd-head">
        <h2 className="dialog-title">{title}</h2>
        {sub && <span className="dim sub">{sub}</span>}
      </div>
      <div className="pd-body">{children}</div>
      <div className="dialog-actions">
        <Button variant="primary" onClick={onClose}>Close</Button>
      </div>
    </dialog>
  )
}
