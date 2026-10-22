import { usePlayhead } from '../playhead'

/** The red playhead line over every lane. `offset` is the header width, `pps` the pixels per second. */
export function Playhead({ pps, offset }: { pps: number; offset: number }) {
  const T = usePlayhead()
  return <div className="playhead" style={{ left: offset + T * pps }} />
}
