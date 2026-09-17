# Silver Policy — TeresIA mREBEL Human-Validated Asset

## Resource identity

- Resource id: `teresia_mrebel_human_validated`
- Resource type: `model_dependent_human_validated`
- Generator: mREBEL
- Role: **AUXILIARY HUMAN-VALIDATED ASSET**
- Version: `0.1.0`

This asset is **not** independent Gold and must never be confused with
`teresia_hohfeld`.

## Conceptual tree

```text
TERESIA HOHFELD
  = independent manual Gold (Hohfeld relations)

TERESIA mREBEL HUMAN VALIDATED
  = model-dependent human judgments over mREBEL proposals
    (Wikidata-like relations)
```

## Canonical universe

P0 canonical records start at the **human-judged** stage reconstructed from:

`teresia-mrebel/.../resultados_finales/metricas_finales_{laboral,tributario}.xlsx`

sheet `tripletas_etiquetadas`.

Raw/filtered prediction dumps (`results_completos/`) are recorded as historical
context only. They are **not** the canonical parent of S1 because the laboral
allowed sentence dump exhibits soft-key drift versus the annotation Excels.

## Semantics

| Label | Meaning |
|---|---|
| accepted | human-accepted mREBEL proposal |
| rejected | `human_rejected_model_prediction` |
| disputed | annotators disagreed before consensus |
| unresolved | no final consensus (expected 0 in P0) |

Rejected proposals are **not** exhaustive `negative_relation` labels. Humans
judged candidate validity, not absence of every possible relation in the text.

## Views

- `canonical/candidates.jsonl` — all judged candidates with both judgments
- `views/accepted/` — `consensus.valid == true`
- `views/rejected/` — `consensus.valid == false`
- `views/disputed/` — `flags.disputed_before_consensus == true`

Accepted rows regress against published corpus-juri Silver CSVs as an oracle,
not as the canonical parent.

## Circularity constraints

Machine-readable constraints are stored in the manifest:

- `independent_of_generator: false`
- `recall_evaluation_of_generator_valid: false`
- `candidate_selection_bias: true`

Humans only saw candidates proposed by mREBEL after historical `REL_ALLOWED`
filtering. The asset cannot measure mREBEL recall and is not an independent
test set for that generator.

## Intended uses

Supported with explicit caveats:

- supportedness research
- human disagreement analysis
- error analysis (free-text notes only; no taxonomy in P0)
- validator / reranker development over this proposal distribution
- cross-domain laboral/tributario analysis
- weak supervision **not** for Hohfeld C1–C3

## Notes

Notes remain `FREE_TEXT_ONLY`. No automatic error taxonomy is derived.
