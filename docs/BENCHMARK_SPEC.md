# Benchmark Specification

## Identity

- Benchmark: `teresia_hohfeld`
- Version: `0.1.0`
- Unit of the primary artifact: Estatuto article/document
- Authoritative annotation source: `estatuto_goldstandard/data/old/rels`

## Frozen layers

### Layer A — Original Hohfeld Gold

The authoritative inventory contains 95 `RelationType` annotations. It is
article/document-level and retains the original inline annotation structure.

### Layer B — Canonical TE representation

Layer B is derived deterministically from Layer A and retains all 95
annotations. It preserves inline arguments, `MissingE2`, every `e2`, every
complement, modifiers, evidence, and source blocks. It does not require every
annotation to form a complete binary triple. Eligibility is capability-specific.

### Layer C — TeresIA sentence-aligned projection

Layer C is a historical derived view of 65 mapped annotations. Each row links to
its Layer A/B `original_annotation_id`. Sentence/document alignment is rebuilt
from corpus-juri `ejemplo_3_*` texts with the historical notebook policy. The
legacy published JSON is used only as a regression oracle.

### Layer D — Span-complete projection

Layer D is the deterministic subset of Layer C with complete projected subject
and object spans. It contains 41 annotations. No fuzzy matching, repair, or
manual correction is applied.

Layers C and D are not the full Gold.

## Canonical contract

`canonical/documents.jsonl` is primary and contains `document_id`,
`source_text`, document provenance, and nested annotations. The normalized
`canonical/annotations.jsonl` companion contains the same annotations one per
line. Dataset hashes belong in manifests, not individual annotations.

Each annotation records relation, signature, argument lists, relation text,
complement list, modifier, evidence, original tagged/raw text, provenance,
derived TE view where supported, and explainable eligibility decisions.

## Determinism

Files are UTF-8 with stable ordering and JSON keys. Content artifacts contain no
build timestamps. Rebuilding from identical source revisions and builder code
must produce identical SHA-256 hashes.
