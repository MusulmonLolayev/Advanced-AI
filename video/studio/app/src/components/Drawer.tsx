import { useEffect, useRef, type ReactNode } from 'react'
import { IconButton } from './IconButton'
/** A panel from the right, under the top bar: a native <dialog> opened with showModal() (so focus is trapped and Esc closes it), the full
 *  width as an overlay. With `dialog` it is a large centred modal instead (the Export dialog). */
export function Drawer({ title, onClose, children, dialog }: { title: ReactNode; onClose: () => void; children: ReactNode; dialog?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const d = ref.current
    if (d && !d.open) d.showModal()
  }, [])
  return (
    <dialog
      ref={ref}
      className={dialog ? 'dialog export-dialog' : 'drawer'}
      aria-label={typeof title === 'string' ? title : undefined}
      onCancel={(e) => {
        e.preventDefault()
        onClose()
      }}
      onClick={(e) => {
        if (e.target === ref.current) onClose() // the backdrop belongs to the dialog element itself
      }}
      // the app listens for single keys on the document: keep them out while the drawer is open
      onKeyDown={(e) => e.nativeEvent.stopPropagation()}
    >
      <header className="drawer-head">
        <h2 className="dialog-title">{title}</h2>
        <span className="grow" />
        <IconButton icon="x" label="Close (Esc)" onClick={onClose} />
      </header>
      <div className="drawer-body">{children}</div>
    </dialog>
  )
}
