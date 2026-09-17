# Data Provenance

## Source repositories

The builder accepts portable roots:

- `--estatuto-root` for `estatuto_goldstandard`;
- `--corpus-juri-root` for `teresia-mrebel-corpus-juri`.

Development defaults discover both below the workspace `_legacy` directory.
No absolute user path is embedded in code or generated data.

The manifest records repository URL, commit, relative file path, byte size, and
SHA-256 for every consumed source file. Source trees are referenced in place and
are not copied into this repository.

## Transformation chain

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

The historical notebook itself is hashed as transformation provenance. Every
projected record carries both `original_annotation_id` and historical row id.

## Known historical loss

The notebook required `e1`, retained only the first `e2`, flattened
complements, and omitted `MissingE2` and modifiers. The rebuilt projection keeps
its 65-row mapping behavior while attaching the complete canonical argument
provenance. The 25 parseable unmatched originals and five historical parser
exclusions remain in Layer B.
