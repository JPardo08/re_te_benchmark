# re_te_benchmark

Reproducible benchmark data and schema packages for legal relation and triple
extraction. P0 builds the Hohfeld Gold from its original article-level inline
annotations without changing or copying the legacy sources.

## Hohfeld layers

The original Gold is 95 typed source annotations. It is not equivalent to the
65-row published TeresIA table: that table is a historical sentence-aligned
projection, and only 41 projected rows have complete subject/object spans.

- Layer A: 95 original Hohfeld annotations.
- Layer B: 95 canonical article-centered annotations.
- Layer C: 65 historical sentence-aligned annotations.
- Layer D: 41 span-complete projected annotations.

Layers C and D are derived views, not the full Gold. See `docs/` for the frozen
specification, Gold policy, and transformation provenance.

## Build

From this repository:

```bash
python3 scripts/build_hohfeld.py
```

Portable source locations can be supplied explicitly:

```bash
python3 scripts/build_hohfeld.py \
  --estatuto-root /path/to/estatuto_goldstandard \
  --corpus-juri-root /path/to/teresia-mrebel-corpus-juri
```

No package installation or non-stdlib runtime dependency is required.

## Audit and tests

```bash
python3 scripts/audit_hohfeld.py
python3 -m unittest discover -s tests
```

The audit validates critical counts, C1, artifact hashes, and exact historical
regression.

## Outputs

Generated files live under `datasets/teresia_hohfeld/`: canonical document and
annotation JSONL, sentence-aligned and span-complete JSONL views, statistics,
historical regression results, and a SHA-256 manifest. The C1 label package is
`schemas/c1/hohfeld_labels.json`.

Ordering and serialization are deterministic. Content-addressed artifacts omit
timestamps; manifests pin consumed source files and repository revisions.
