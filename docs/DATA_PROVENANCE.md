# Data Provenance

## Source repositories

Builders accept portable roots. Development defaults discover `_legacy`
siblings. No absolute user path is embedded in code or generated data.

### Hohfeld Gold

- `--estatuto-root` for `estatuto_goldstandard`
- `--corpus-juri-root` for `teresia-mrebel-corpus-juri`

### mREBEL human-validated

- `--teresia-mrebel-root` for `teresia-mrebel`
- `--corpus-juri-root` for `teresia-mrebel-corpus-juri` (accepted-view oracle)

Manifests record repository URL, commit, relative file path, byte size, and
SHA-256 for consumed source files. Source trees are referenced in place and are
not copied into this repository.

---

## Hohfeld transformation chain

1. **Original:** parse every typed block in
   `data/old/rels/articulo_*.txt`, preserving all known inline roles and
   metadata.
2. **Canonical:** group the parsed annotations by article and attach the
   corresponding `data/old/old_articles` text.
3. **Sentence projection:** run the historical notebook's deterministic
   whitespace normalization, sentence split, sorted global `ejemplo_3_*`
   fallback search, and exact span lookup against
   `corpus/laboral/brat/ejemplo_3_*.txt`. These corpus-juri texts contain every
   host document needed for the 65 mapped annotations. The published
   `gold_standard/laboral/hohfeld_laboral.json` is used only as a regression
   oracle, not as annotation or alignment input.
4. **Span projection:** recompute exact subject/object offsets against projected
   `sent_text` and retain only complete rows.

### Known historical loss (Hohfeld)

The notebook required `e1`, retained only the first `e2`, flattened
complements, and omitted `MissingE2` and modifiers. The rebuilt projection keeps
its 65-row mapping behavior while attaching the complete canonical argument
provenance. The 25 parseable unmatched originals and five historical parser
exclusions remain in Layer B.

---

## mREBEL human-validated transformation chain

1. **Historical context (non-canonical parent):** mREBEL dumps under
   `results_completos/` and `REL_ALLOWED` filtering. Laboral allowed sentence
   dumps currently exhibit soft-key drift versus annotation Excels; they are
   hashed as context only.
2. **Canonical human-judged universe:** read
   `evaluacion/resultados_finales/metricas_finales_{laboral,tributario}.xlsx`
   sheet `tripletas_etiquetadas`, preserving both annotator judgments, notes,
   consensus, and adjudication origin.
3. **Derived views:** accepted / rejected / disputed-before-consensus filters
   over the canonical candidate IDs.
4. **Published Silver regression:** compare accepted soft-keys against
   `silver_standard/{laboral,tributario}/tripletas_*.csv`.

### Provenance gap (documented)

Because raw prediction dumps are not a proven monotonic parent of the judged
rows for laboral, P0 does **not** claim a reconstructible S0→S1 funnel identity.
The scientifically stable reconstructible universe begins at the human-judged
final Excels.

### Notes policy

Free-text notes are preserved as-is (`FREE_TEXT_ONLY`). No error taxonomy is
invented in P0.
