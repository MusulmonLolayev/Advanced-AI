import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { Button } from './Button'

export type ConfirmOptions = {
  title: string
  body?: ReactNode
  confirmLabel: string
  cancelLabel?: string
  tone?: 'default' | 'danger' | 'primary'
}
type Confirm = (opts: ConfirmOptions) => Promise<boolean>
type Req = { opts: ConfirmOptions; resolve: (ok: boolean) => void }

const Ctx = createContext<Confirm>(() => Promise.resolve(false))
/** `const { confirm } = useDialog()`; `await confirm({...})` is true when the confirm button was pressed, false for Cancel, Esc or the backdrop. */
export const useDialog = () => ({ confirm: useContext(Ctx) })

/** In-app replacement for window.confirm: a native <dialog> opened with showModal() (backdrop, focus trap, top layer).
 *  One dialog at a time; a second request waits for the first. Enter presses the focused button (confirm, or Cancel for danger). */
export function DialogProvider({ children }: { children: ReactNode }) {
  const [req, setReq] = useState<Req | null>(null)
  const queue = useRef<Req[]>([])
  const current = useRef<Req | null>(null)

  const confirm = useCallback<Confirm>(
    (opts) =>
      new Promise<boolean>((resolve) => {
        const r = { opts, resolve }
        if (current.current) queue.current.push(r)
        else {
          current.current = r
          setReq(r)
        }
      }),
    [],
  )
  const settle = useCallback((ok: boolean) => {
    const r = current.current
    if (!r) return
    r.resolve(ok)
    current.current = queue.current.shift() ?? null
    setReq(current.current)
  }, [])

  return (
    <Ctx.Provider value={confirm}>
      {children}
      {req && <DialogBox key={req.opts.title + queue.current.length} req={req} settle={settle} />}
    </Ctx.Provider>
  )
}

function DialogBox({ req, settle }: { req: Req; settle: (ok: boolean) => void }) {
  const { title, body, confirmLabel, cancelLabel = 'Cancel', tone = 'default' } = req.opts
  const ref = useRef<HTMLDialogElement>(null)
  const okRef = useRef<HTMLButtonElement>(null)
  const noRef = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    const d = ref.current
    if (d && !d.open) d.showModal()
    ;(tone === 'danger' ? noRef : okRef).current?.focus()
  }, [tone])
  return (
    <dialog
      ref={ref}
      className="dialog"
      aria-labelledby="dialog-title"
      onCancel={(e) => {
        e.preventDefault()
        settle(false)
      }}
      onClick={(e) => {
        if (e.target === ref.current) settle(false) // the backdrop belongs to the dialog element itself
      }}
      // the booth and the app listen for single keys on the document: keep them out while a question is open
      onKeyDown={(e) => e.nativeEvent.stopPropagation()}
    >
      <h2 id="dialog-title" className="dialog-title">{title}</h2>
      {body != null && <div className="dialog-body">{body}</div>}
      <div className="dialog-actions">
        <Button ref={noRef} onClick={() => settle(false)}>{cancelLabel}</Button>
        <Button ref={okRef} className="dialog-ok" variant={tone === 'default' ? 'default' : tone} onClick={() => settle(true)}>{confirmLabel}</Button>
      </div>
    </dialog>
  )
}
