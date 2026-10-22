import { usePlayhead } from '../playhead'
import { cls, timecode } from '../util'

export function Timecode({ seconds, big, rec, title }: { seconds: number; big?: boolean; rec?: boolean; title?: string }) {
  return (
    <span className={cls('timecode', big && 'big', rec && 'rec')} title={title}>
      {timecode(seconds)}
    </span>
  )
}

export function PlayheadTimecode({ big }: { big?: boolean }) {
  return <Timecode seconds={usePlayhead()} big={big} title="playhead" />
}
