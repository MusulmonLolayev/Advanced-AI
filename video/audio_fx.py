"""Clean-up applied to every cloned-voice clip. Kept free of manim so the voice tools that run in
the Navoiy stack's env (revoice.py) can import it too."""
import subprocess
from pathlib import Path


def trim_silence(path, keep=0.12, threshold="-40dB"):
    """Cut a clip's leading and trailing silence down to `keep` seconds, in place.
    The cloned voice pads clips with up to ~1.2 s of quiet at each end, which turned
    scene boundaries into 3 s gaps."""
    f = (f"silenceremove=start_periods=1:start_threshold={threshold}:start_silence={keep}")
    tmp = Path(path).with_suffix(".trim.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", f"{f},areverse,{f},areverse",
                    "-ar", "24000", "-ac", "1", "-b:a", "128k", str(tmp)], check=True)
    tmp.replace(path)


def cap_pauses(path, longer_than=0.8, threshold="-40dB"):
    """Shorten any silence inside a clip that runs past `longer_than` seconds to under a second,
    in place. The cloned voice once paused 2.3 s between two sentences of one line (Lecture 5,
    10.9), and anything over 2 s that is not a hands-on pause is a defect. Normal breaths
    between sentences (~0.4 s) are left alone."""
    f = f"silenceremove=stop_periods=-1:stop_threshold={threshold}:stop_duration={longer_than}:stop_silence=0.2:window=0.02"
    tmp = Path(path).with_suffix(".cap.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", f,
                    "-ar", "24000", "-ac", "1", "-b:a", "128k", str(tmp)], check=True)
    tmp.replace(path)
