# re_te_benchmark

Reproducible benchmark data and schema packages for legal relation and triple
extraction.

## Resource tree

```text
TERESIA HOHFELD
  = independent manual Gold (Hohfeld relations)

TERESIA mREBEL HUMAN VALIDATED
  = model-dependent human judgments over mREBEL proposals
```

These resources share packaging conventions but **must not** be mixed into a
single TE ontology or scored as one Gold set.

## Hohfeld Gold (P0)

The original Gold is 95 typed source annotations. It is not equivalent to the
65-row published TeresIA table: that table is a historical sentence-aligned
projection, and only 41 projected rows have complete subject/object spans.

- Layer A: 95 original Hohfeld annotations.
- Layer B: 95 canonical article-centered annotations.
- Layer C: 65 historical sentence-aligned annotations.
- Layer D: 41 span-complete projected annotations.

## mREBEL human-validated asset (P0)

Canonical universe: **2189** dual-judged candidates reconstructed from the
human consensus Excels (laboral 1153 + tributario 1036).

Derived views:

- accepted: 465 (`human_accepted_mrebel_proposal`)
- rejected: 1724 (`human_rejected_model_prediction`)
- disputed-before-consensus: 469 (all resolved in P0)

This asset is **generator-dependent**. It cannot measure mREBEL recall and is
not an independent test set for mREBEL. See `docs/SILVER_POLICY.md`.

## Build

```bash
python3 scripts/build_hohfeld.py
python3 scripts/build_silver.py
```

Portable roots:

```bash
python3 scripts/build_hohfeld.py \
  --estatuto-root /path/to/estatuto_goldstandard \
  --corpus-juri-root /path/to/teresia-mrebel-corpus-juri

python3 scripts/build_silver.py \
  --teresia-mrebel-root /path/to/teresia-mrebel \
  --corpus-juri-root /path/to/teresia-mrebel-corpus-juri
```

No package installation or non-stdlib runtime dependency is required.

## Audit and tests

```bash
python3 scripts/audit_hohfeld.py
python3 scripts/audit_silver.py
python3 -m unittest discover -s tests -t .
```

## Outputs

- `datasets/teresia_hohfeld/` — Gold layers + manifests + C1 labels
- `datasets/teresia_mrebel_human_validated/` — judged candidates + accepted /
  rejected / disputed views + manifests

Ordering and serialization are deterministic. Content-addressed artifacts omit
timestamps; manifests pin consumed source files and repository revisions.
