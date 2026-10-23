import type { SVGProps } from 'react'

const PATHS = {
  play: <path d="M6 4l14 8-14 8z" fill="currentColor" stroke="none" />,
  pause: <path d="M6 4h4v16H6zM14 4h4v16h-4z" fill="currentColor" stroke="none" />,
  prev: <path d="M6 5v14M19 5l-9 7 9 7z" />,
  next: <path d="M18 5v14M5 5l9 7-9 7z" />,
  rec: <circle cx="12" cy="12" r="7" fill="currentColor" stroke="none" />,
  stop: <rect x="6" y="6" width="12" height="12" fill="currentColor" stroke="none" />,
  mic: <path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM5 11a7 7 0 0 0 14 0M12 18v3" />,
  chevron: <path d="M9 6l6 6-6 6" />,
  chevronLeft: <path d="M15 6l-6 6 6 6" />,
  folder: <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />,
  plus: <path d="M12 5v14M5 12h14" />,
  minus: <path d="M5 12h14" />,
  check: <path d="M5 12l5 5 9-10" />,
  warn: <path d="M12 4l9 16H3zM12 10v4M12 17v.5" />,
  alert: <path d="M12 3v11M12 18v.5" />,
  ear: <path d="M7 10a5 5 0 0 1 10 0c0 3-3 3.5-3 6a2.5 2.5 0 0 1-5 0M10 10a2 2 0 0 1 4 0" />,
  silence: <path d="M4 12h3M17 12h3M10 8v8M14 10v4" />,
  download: <path d="M12 4v11M7 11l5 5 5-5M5 20h14" />,
  scissors: <path d="M6 7a2 2 0 1 0 0 .01M6 17a2 2 0 1 0 0 .01M8 8l11 9M8 16L19 7" />,
  server: <path d="M4 5h16v6H4zM4 13h16v6H4zM8 8h.01M8 16h.01" />,
  jobs: <path d="M12 4v4M12 16v4M4 12h4M16 12h4M6.5 6.5l2.8 2.8M14.7 14.7l2.8 2.8M17.5 6.5l-2.8 2.8M9.3 14.7l-2.8 2.8" />,
  globe: <path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" />,
  search: <path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4" />,
  fit: <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />,
  sidebar: <path d="M4 5h16v14H4zM9 5v14" />,
  keyboard: <path d="M3 7h18v10H3zM7 11h.01M11 11h.01M15 11h.01M7 14h10" />,
  trash: <path d="M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13" />,
  merge: <path d="M6 4v6a4 4 0 0 0 4 4h4M18 20v-6M6 20V10" />,
  film: <path d="M4 5h16v14H4zM8 5v14M16 5v14M4 9h4M4 15h4M16 9h4M16 15h4" />,
  mark: <path d="M12 3l6 9-6 9-6-9z" fill="currentColor" stroke="none" />,
  tick: <path d="M12 3v18" />,
  x: <path d="M6 6l12 12M18 6L6 18" />,
} as const

export type IconName = keyof typeof PATHS

export function Icon({ name, size = 16, ...rest }: { name: IconName; size?: number } & SVGProps<SVGSVGElement>) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...rest}>
      {PATHS[name]}
    </svg>
  )
}
