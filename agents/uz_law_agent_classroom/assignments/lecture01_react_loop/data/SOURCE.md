# The article sample

`sample_articles.jsonl` -- 40 articles of the Labor Code of the Republic of Uzbekistan (adopted 2022-10-28, lex.uz
document -6257288), one JSON object per line (`article_id`, `title`, `section`, `chapter`, `text`, ...), snapshot
2026-07. The whole Code has 581 articles.

Copied byte for byte, record by record, from the course's full file `mehnat_kodeksi.jsonl`, which is taken
unchanged from [javohirmat/uzbek-legal-corpus](https://github.com/javohirmat/uzbek-legal-corpus) at commit
`7fabb822cca04439ac6197bfa1441eca6112bc19`, file `data/articles/mehnat_kodeksi.jsonl`. Data CC0; legislative text
is not copyrightable (Art. 8 of the Law on Copyright and Related Rights).

The sample holds the articles that the recorded runs in `traces/` list or fetch (so that they replay), a few
articles the lecture quotes, and 15 filler articles (the first ones of the Code not already chosen).

sha256 `37ddf8d715d96f13b9e7e5d5150041b209de829cf508968c0bd9cbf9365ab64e` (checked by the self-checks).

The text keeps the corpus's spelling: oʻ/gʻ with U+02BB, the tutuq belgisi with U+02BC.
