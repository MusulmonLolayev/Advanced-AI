import type { ReactNode, RefObject } from 'react'
import { Button, IconButton, PlayheadTimecode, Timecode } from '../../components'
import type { Project } from '../../types'
import type { Transport } from './usePlayer'

/** The video monitor: the silent picture at 16:9, as large as the panel allows, with the line's text under it and the transport below. The voice comes from the player's audio elements. */
export function Monitor({
  p, total, videoRef, tr, line, onSeekLine, silences, onSilence, strip,
}: {
  p: Project
  total: number
  videoRef: RefObject<HTMLVideoElement | null>
  tr: Transport
  line: number
  onSeekLine: (k: number) => void
  silences: { a: number; b: number }[]
  onSilence: (dir: 1 | -1) => void
  /** a one-line summary of the selected line under the transport */
  strip?: ReactNode
}) {
  const own = tr.what.kind !== 'lecture'
  return (
    <div className="monitor">
      <div className="stage">
        <div className="screen" data-testid="screen">
          <video ref={videoRef} muted playsInline preload="auto" />
          <div className="screen-tag">{tr.what.kind === 'version' ? `VERSION · ${tr.what.label}` : tr.what.kind === 'take' ? `YOUR VOICE · ${tr.what.label}` : 'PICTURE · silent video + edit list'}</div>
        </div>
      </div>
      <div className="subtitle" data-testid="subtitle">
        <span className="clamp">
          <span className="mono">{line + 1}</span> {p.lines[line]?.[1]}
        </span>
      </div>
      <div className="transport">
        {own ? (
          <span className="timecode" title="the clock of what is playing">{tr.sideClock || '0:00 / 0:00'}</span>
        ) : (
          <>
            <PlayheadTimecode />
            <span className="mono dim"> / </span>
            <Timecode seconds={total} />
          </>
        )}
        <span className="grow" />
        <IconButton icon="prev" label="Previous line (←)" onClick={() => onSeekLine(Math.max(0, line - 1))} />
        <IconButton icon={tr.playing ? 'pause' : 'play'} label={tr.playing ? 'Pause (Space)' : 'Play (Space)'} big on={tr.playing} onClick={tr.toggle} />
        <IconButton icon="next" label="Next line (→)" onClick={() => onSeekLine(Math.min(p.lines.length - 1, line + 1))} />
        <span className="grow" />
        <span className="transport-sil">
          <IconButton icon="chevronLeft" label="Previous long silence" onClick={() => onSilence(-1)} />
          <Button small variant="ghost" icon="silence" onClick={() => onSilence(1)} title="Jump to the next long silence">next long silence</Button>
          <span className="dim mono">{silences.length}</span>
        </span>
        <Button small variant={own ? 'primary' : 'ghost'} disabled={!own} onClick={tr.back} title="leave the take or the version and play the lecture's edit list again">
          {own ? 'back to the lecture' : 'whole lecture'}
        </Button>
      </div>
      {strip && <div className="line-strip" data-testid="line-strip">{strip}</div>}
    </div>
  )
}
