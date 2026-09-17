# Benchmark Specification

## Resource overview

| Resource | Type | Primary unit |
|---|---|---|
| `teresia_hohfeld` | independent manual Gold | Estatuto article / annotation |
| `teresia_mrebel_human_validated` | model-dependent human-validated | sentence-context mREBEL candidate |

Do not merge their relation inventories.

---

## A. Hohfeld Gold — `teresia_hohfeld` v0.1.0

### Identity

- Benchmark: `teresia_hohfeld`
- Version: `0.1.0`
- Unit of the primary artifact: Estatuto article/document
- Authoritative annotation source: `estatuto_goldstandard/data/old/rels`

### Frozen layers

#### Layer A — Original Hohfeld Gold

The authoritative inventory contains 95 `RelationType` annotations. It is
article/document-level and retains the original inline annotation structure.

#### Layer B — Canonical TE representation

Layer B is derived deterministically from Layer A and retains all 95
annotations. It preserves inline arguments, `MissingE2`, every `e2`, every
complement, modifiers, evidence, and source blocks. It does not require every
annotation to form a complete binary triple. Eligibility is capability-specific.

#### Layer C — TeresIA sentence-aligned projection

Layer C is a historical derived view of 65 mapped annotations. Each row links to
its Layer A/B `original_annotation_id`. Sentence/document alignment is rebuilt
from corpus-juri `ejemplo_3_*` texts with the historical notebook policy. The
legacy published JSON is used only as a regression oracle.

#### Layer D — Span-complete projection

Layer D is the deterministic subset of Layer C with complete projected subject
and object spans. It contains 41 annotations. No fuzzy matching, repair, or
manual correction is applied.

Layers C and D are not the full Gold.

### Canonical contract

`canonical/documents.jsonl` is primary and contains `document_id`,
`source_text`, document provenance, and nested annotations. The normalized
`canonical/annotations.jsonl` companion contains the same annotations one per
line. Dataset hashes belong in manifests, not individual annotations.

---

## B. mREBEL human-validated — `teresia_mrebel_human_validated` v0.1.0

### Identity

- Resource: `teresia_mrebel_human_validated`
- Type: `model_dependent_human_validated`
- Generator: mREBEL
- Role: auxiliary human-validated asset
- Authoritative source: human-judged Excel finals in `teresia-mrebel`

### Canonical stage

Canonical P0 records are the **2189 dual-judged candidates** (1153 laboral +
1036 tributario). Raw prediction dumps are provenance context only and are not
used as the parent of the judged universe.

### Candidate contract

Each candidate includes contextual identity (`doc`, `sent_id`, text), the mREBEL
prediction, neutral annotator_A/annotator_B judgments, agreement, consensus,
status (`accepted`|`rejected`|`unresolved`), disputed flag, and provenance.

Rejected means `human_rejected_model_prediction`, not exhaustive absence of a
relation.

### Views

- accepted: consensus valid true
- rejected: consensus valid false
- disputed: disagreed before consensus (still resolved in P0)

Published corpus-juri Silver CSVs are a regression oracle for the accepted view.

### Evaluation constraints

- independent_of_generator: false
- recall_evaluation_of_generator_valid: false
- candidate_selection_bias: true

---

## Determinism

Files are UTF-8 with stable ordering and JSON keys. Content artifacts contain no
build timestamps. Rebuilding from identical source revisions and builder code
must produce identical SHA-256 hashes.
