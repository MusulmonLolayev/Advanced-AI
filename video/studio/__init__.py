"""The studio's editor: line-by-line takes, an edit list both the browser preview and the export read, transcripts.

    timeline.py      pure logic: events -> takes -> two tracks (voice, picture) -> the lecture's edit list,
                     cuts, nudges, silence proposals, subtitles, chapters, the script check
    store.py         the SQLite tables (sessions, take edits, choices, jobs)
    media.py         ffmpeg/DeepFilterNet work: a session's audio (assembled from its chunks, cleaned, preview copy,
                     silences), and the export (picture + voice + .srt + chapters)
    words_worker.py  speech recognition with word times and forced alignment to the script (the Navoiy env)
    editor.html      the editor page
"""
