# Réttarvísir profile illustration

The profile replays a saved evaluation example in a 24-second SVG loop. It uses the real app's serif title, section-symbol mark, teal search accents and gold citations. Four stages show the question, the selected retrieval method, its final top three sources, and the first two sentences of the saved answer. The answer remains visible for ten seconds. The timing and moving search dots illustrate the pipeline; they do not represent measured latency or intermediate rankings.

## Provenance

All project references below are pinned to commit `f64cc658bd0bf27a589d26df135c3560d89f4c9c` in `solvisantos22/maltaekni_lokaverkefni`.

- [Question 5](https://github.com/solvisantos22/maltaekni_lokaverkefni/blob/f64cc658bd0bf27a589d26df135c3560d89f4c9c/docs/evaluation_questions.csv#L6): `Getur neytandi krafist úrbóta eða nýrrar afhendingar vegna galla?`
- [Saved result, line 25](https://github.com/solvisantos22/maltaekni_lokaverkefni/blob/f64cc658bd0bf27a589d26df135c3560d89f4c9c/reports/evaluation/evaluation_details_latest.jsonl#L25): run `gemini-strict-final`, method `rrf-bge-m3-bm25-rerank`.
- [Selected qualitative case](https://github.com/solvisantos22/maltaekni_lokaverkefni/blob/f64cc658bd0bf27a589d26df135c3560d89f4c9c/reports/evaluation/report_tables/qualitative_cases.csv#L2): the project's `strong_answer` example.
- [UI palette](https://github.com/solvisantos22/maltaekni_lokaverkefni/blob/f64cc658bd0bf27a589d26df135c3560d89f4c9c/src/maltaekni_lokaverkefni/web/styles.css) and [mark](https://github.com/solvisantos22/maltaekni_lokaverkefni/blob/f64cc658bd0bf27a589d26df135c3560d89f4c9c/src/maltaekni_lokaverkefni/web/index.html).

The final sources are all from [Lög um neytendakaup, 48/2003](https://www.althingi.is/lagas/nuna/2003048.html):

1. `[1]`, `2003048.html_029`: 29. gr. Krafa um úrbætur og nýja afhendingu.
2. `[2]`, `2003048.html_030`: 30. gr. Framkvæmd úrbóta og nýrrar afhendingar.
3. `[3]`, `2003048.html_026`: 26. gr. Úrræði neytanda vegna galla.

Source headings are shortened in the illustration. The answer excerpt is verbatim, including the exception about obstacles or unreasonable cost and the original `[1][3]` and `[1]` citation markers. Its source chips only show the two references used in that excerpt. The full saved answer uses all three sources.

This illustrates an educational prototype. It is not live output, a screen recording, legal advice, or a guarantee of retrieval correctness. The illustration shows the selected hybrid method; the app also supports methods that do not use fusion or reranking. No scores, accuracy percentages or comparative performance claims are shown.

## Assets

Run `python3 scripts/generate_rettarvisir.py` to recreate the light, dark and static SVGs. Assets are local to the profile repository and require no external service. The animated SVGs handle reduced motion internally; the README picture element also selects the static variant for reduced-motion visitors. The static file adapts its colours for dark mode. The open details section can be collapsed to hide motion.
