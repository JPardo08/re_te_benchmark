# Gold Policy

## Authority and preservation

The 95 typed blocks in `estatuto_goldstandard/data/old/rels` are the
authoritative Hohfeld Gold. The builder never edits or repairs them and never
deduplicates annotations.

The canonical layer preserves:

- annotations without `e1`;
- `MissingE2` as a non-inline argument with a null span;
- all inline `e2` values;
- complements as an ordered list;
- modifiers and their original spans;
- original tagged text and raw source blocks.

No field is silently promoted. Derived TE objects identify whether their source
was `inline_e2` or `MissingE2`.

## Capability-specific eligibility

Eligibility is not a global boolean. Every annotation receives a boolean and
machine-readable reason for:

- relation type;
- strict inline complete triplet;
- complete triplet allowing `MissingE2`;
- argument-level use;
- original span-level use;
- textual supportedness;
- schema/type use;
- document-level TE;
- sentence projection;
- sentence-span use.

At version 0.1.0 the verified source yields 95 relation labels, 60 strict inline
binaries, 85 complete candidates when `MissingE2` is allowed, and 10 partial
document-level records.

## Duplicates and alternatives

Source duplicates, alternative annotations, and projection collisions are
different phenomena and are tagged without deletion. In particular,
`articulo_64#2/#3` remain source duplicates and `articulo_47#2/#3` remain
alternative annotations, including the two inline `e2` values in `#3`.

## Prohibited P0 transformations

P0 performs no fuzzy offset repair, manual correction, semantic inference,
deduplication, ontology mapping, alias mapping, or Gold text rewriting.
