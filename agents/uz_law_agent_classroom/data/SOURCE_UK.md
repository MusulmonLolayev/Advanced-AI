# The optional UK example corpus

`uk_working_time.jsonl` — two UK laws on work, one regulation or section per record (`article_id` such as `WTR 5A`
or `NMWA 1`, `title`, `part`, `text`, `uri`, …), 118 records (64 regulations, 54 sections; repealed provisions and
text quoted inside amendments to other acts are left out):

| Law | Source XML | sha256 of the XML |
|---|---|---|
| The Working Time Regulations 1998 (S.I. 1998/1833), "WTR" | <https://www.legislation.gov.uk/uksi/1998/1833/data.xml> | `6a587da9a465c2d76c0db5c4706089f7e266f385fd00ccccf0e87275bdf93f13` |
| National Minimum Wage Act 1998 (c. 39), "NMWA" | <https://www.legislation.gov.uk/ukpga/1998/39/data.xml> | `333bd96d67156491b912378b0178216f959ae9c86aede1f7bbca9440d15733f8` |

Both are the revised text valid on 2026-10-01 for England, Wales and Scotland (Northern Ireland has its own working
time regulations), downloaded 2026-10-17 and converted by `build_uk_corpus.py` (subdivisions kept as `(1)`, `(a)`;
editorial notes dropped; a formula written as `(A + B) / (C)`). The site's text changes as the law is amended, so
the JSONL file is the pinned copy:

sha256 `f9c1d92d8022a3ddf8ebe472fa5f335a8062b8233601645c4ca0e0bc0fb21b73` (checked by the tests).

Licence: Contains public sector information licensed under the
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
(Crown copyright).

Neither law states the minimum wage in pounds: NMWA s. 1(3) leaves it to the Secretary of State, who sets it in the
National Minimum Wage Regulations 2015, which are deliberately not in the corpus (the agent should say the corpus
does not answer, as with the Uzbek code).
