import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'

const Ctx = createContext<(msg: string) => void>(() => {})
export const useToast = () => useContext(Ctx)

/** Provider and stack. `toast("…")` shows a message for 3 s. */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<{ id: number; msg: string }[]>([])
  const push = useCallback((msg: string) => {
    const id = Date.now() + Math.random()
    setItems((l) => [...l.slice(-3), { id, msg }])
    setTimeout(() => setItems((l) => l.filter((x) => x.id !== id)), 3200)
  }, [])
  return (
    <Ctx.Provider value={push}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {items.map((t) => (
          <div className="toast" key={t.id}>
            {t.msg}
          </div>
        ))}
      </div>
    </Ctx.Provider>
  )
}
