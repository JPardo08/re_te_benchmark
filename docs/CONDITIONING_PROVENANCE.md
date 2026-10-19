# Conditioning Provenance

## Purpose

This register classifies candidate conditioning knowledge known at
`CONDITIONING_SPEC_P0`. Presence in this register does not authorize use. A
candidate is eligible only when both this register and
`docs/CONDITIONING_SPEC.md` permit its knowledge component.

Eligibility values are:

- `YES`: eligible in the stated condition;
- `NO`: prohibited or unrelated to the target condition;
- `CONDITIONAL`: eligible only after the stated independent evidence and
  scientific decision are frozen;
- `UNRESOLVED`: current evidence cannot support a decision.

`CONDITIONAL` and `UNRESOLVED` assets MUST NOT be supplied in a runtime payload
until resolved through versioned change control.

## Provenance classes

- `ORIGINAL_DESIGN`: explicitly encoded by the original annotation design,
  source metadata, or authoritative annotation guidance.
- `EXTERNAL_AUTHORITATIVE`: domain knowledge from an independent,
  authoritative source, with revision and scope recorded.
- `OBSERVED_IN_GOLD`: an empirical value or individual annotation visible in
  the Gold.
- `DERIVED_FROM_GOLD`: a count, aggregate, mapping, lexicon, alias, rule, or
  other artifact computed from Gold.
- `DERIVED_LATER`: created by a later pipeline, UI/export configuration,
  projection, model-dependent process, or subsequent analysis.
- `MODEL_NATIVE`: internal pretrained model knowledge not supplied by the
  experiment.
- `UNKNOWN`: origin, authority, or intended semantics cannot be established.

An asset may have multiple factual origins. This register assigns the class
that governs conditioning eligibility and records secondary evidence in the
rationale.

## Candidate asset register

| asset | description | source | source_revision/path if local | provenance_class | eligible_for_C1 | eligible_for_C2 | eligible_for_C3 | leakage_risk | decision | rationale |
|---|---|---|---|---|---|---|---|---|---|---|
| Duty / Right / Privilege / NoRight | Closed Hohfeld target relation inventory | Original `RelationType` metadata | `estatuto_goldstandard@8e22ead8359515164979e85e9fe1f3741f838826:data/old/rels` | ORIGINAL_DESIGN | YES | YES | YES | LOW | INCLUDE | The four labels are explicit source-schema metadata and the exact C1 inventory; empirical counts are excluded. |
| LegalAgent | Entity-type label in original signatures | Original `RelationSignature` metadata | `estatuto_goldstandard@8e22ead8359515164979e85e9fe1f3741f838826:data/old/rels` | ORIGINAL_DESIGN | NO | IDENTIFIER_ONLY | IDENTIFIER_ONLY | MEDIUM | WITHHOLD_DEFINITION | The identifier is retained in C2_SCHEMA_V1. Its definition is unresolved, so it is not an extractor instruction. Observed pair frequencies do not become constraints. |
| LegalEntity | Entity-type label in original signatures | Original `RelationSignature` metadata | same as above | ORIGINAL_DESIGN | NO | IDENTIFIER_ONLY | IDENTIFIER_ONLY | MEDIUM | WITHHOLD_DEFINITION | Same restriction as LegalAgent. |
| LegalConcept | Entity-type label in original signatures | Original `RelationSignature` metadata | same as above | ORIGINAL_DESIGN | NO | IDENTIFIER_ONLY | IDENTIFIER_ONLY | MEDIUM | WITHHOLD_DEFINITION | Rare occurrence does not establish its semantics. The unresolved identifier is withheld from the payload. |
| observed RelationSignature values | Five type-pair combinations appearing in typed Gold annotations | Audit of original Gold | `re_te_benchmark:datasets/teresia_hohfeld/manifests/statistics.json`; upstream `estatuto_goldstandard@8e22ead...:data/old/rels` | OBSERVED_IN_GOLD | NO | CONDITIONAL | CONDITIONAL | HIGH | DO_NOT_TREAT_AS_NORMATIVE | Retain as audit evidence only unless independent annotation-design evidence proves an intended closed-world signature schema. |
| e1 role identifier | Inline first-argument marker | Original tagged annotation format | `estatuto_goldstandard@8e22ead...:data/old/rels` | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_AVAILABLE_SEMANTICS_PARTIAL | The marker is original; the mapping to subject is later practice and does not fully establish legal role semantics. |
| e2 role identifier | Inline second-argument marker | Original tagged annotation format | same as above | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_AVAILABLE_SEMANTICS_PARTIAL | The marker is original; direction and role semantics require independent documentation. |
| comp role/concept | Ordered complement annotation construct | Original tagged annotation format | same as above | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_ONLY | C2/C3 may describe a justified role; concrete complement strings from Gold are prohibited. |
| concrete comp values | Annotated thematic/complement strings | Individual Gold annotations | same as above; canonical copy in `datasets/teresia_hohfeld/canonical/annotations.jsonl` | OBSERVED_IN_GOLD | NO | NO | NO | HIGH | EXCLUDE | Concrete values are test examples. |
| mod role/concept | Modifier annotation construct | Original tagged annotation format | `estatuto_goldstandard@8e22ead...:data/old/rels` | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_ONLY | The role exists, but authoritative semantics are not frozen. |
| concrete mod values | Individual modifier strings, including the observed rare value | Individual Gold annotations | same as above; canonical copy in `datasets/teresia_hohfeld/canonical/annotations.jsonl` | OBSERVED_IN_GOLD | NO | NO | NO | HIGH | EXCLUDE | Concrete values are test examples and may reveal annotation decisions. |
| MissingE1 role/concept | Metadata construct for a non-inline first participant | Original tagged annotation format | `estatuto_goldstandard@8e22ead...:data/old/rels` | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_ONLY | Existence is design knowledge; exact semantics and scoring policy remain incomplete, and the construct does not establish e1 as a privileged bearer or subject. |
| concrete MissingE1 values | Gold strings recorded outside inline spans | Individual Gold annotations | `estatuto_goldstandard@8e22ead...:data/old/rels` | OBSERVED_IN_GOLD | NO | NO | NO | HIGH | EXCLUDE | Concrete values are Gold content and MUST NOT be exposed. |
| MissingE2 role/concept | Metadata construct for a non-inline second participant | Original tagged annotation format | `estatuto_goldstandard@8e22ead...:data/old/rels` | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_ONLY | Existence is design knowledge; exact semantics and scoring policy remain incomplete. |
| concrete MissingE2 values | Gold strings recorded outside inline spans | Individual Gold annotations | same as above; canonical copy in `datasets/teresia_hohfeld/canonical/annotations.jsonl` | OBSERVED_IN_GOLD | NO | NO | NO | HIGH | EXCLUDE | Concrete values are Gold content and MUST NOT be exposed. |
| rel role | Inline surface-relation marker | Original tagged annotation format | `estatuto_goldstandard@8e22ead...:data/old/rels` | ORIGINAL_DESIGN | NO | CONDITIONAL | CONDITIONAL | MEDIUM | ROLE_ONLY | The role may be documented after semantics are frozen; values remain excluded. |
| relation_text / lexical triggers | Concrete surface verbalizations extracted from `<rel>` | Individual Gold annotations and later projection | upstream path above; `datasets/teresia_hohfeld/**/annotations.jsonl` | OBSERVED_IN_GOLD | NO | NO | NO | HIGH | EXCLUDE_CURRENT_ASSET | A future independent lexicon would be a separately versioned asset; Gold triggers cannot seed it. |
| BRAT annotation.conf Arg1/Arg2 grids | UI/export configuration enumerating 3×3 types for every relation | Historical corpus conversion/export | `teresia-mrebel-corpus-juri@0d79c10bd12def9d6f0120966ede0d609a3fdbd8:gold_standard/laboral/brat/annotation.conf` | DERIVED_LATER | NO | NO | NO | HIGH | REFERENCE_ONLY | The grid includes combinations not observed in Gold and is not evidence of intended domain/range axioms. |
| Gold relation frequencies | Counts by relation label | Computed from typed Gold | `datasets/teresia_hohfeld/manifests/statistics.json` and tests | DERIVED_FROM_GOLD | NO | NO | NO | CRITICAL | EXCLUDE | Empirical test distribution is direct leakage. |
| Gold signature frequencies | Counts by observed type pair | Computed from typed Gold | `datasets/teresia_hohfeld/manifests/statistics.json` | DERIVED_FROM_GOLD | NO | NO | NO | CRITICAL | EXCLUDE | Aggregates cannot establish schema constraints. |
| concrete Gold examples | Source text, arguments, labels, triggers, complements, and annotation combinations | Canonical independent Gold | `datasets/teresia_hohfeld/canonical/**` and `views/**` | OBSERVED_IN_GOLD | NO | NO | NO | CRITICAL | EXCLUDE | Main-condition payloads are zero-shot with respect to benchmark examples. |
| Silver accepted examples | Human-accepted mREBEL proposals | Generator-dependent human-validated resource | `datasets/teresia_mrebel_human_validated/views/accepted/candidates.jsonl` | DERIVED_LATER | NO | NO | NO | CRITICAL | EXCLUDE | These examples depend on mREBEL candidate generation and cannot silently become conditioning for the main experiment. |
| legacy REL_ALLOWED list | Seven Wikidata-like relation labels used as an mREBEL whitelist | Later system implementation | `teresia-mrebel@f75ad75567c9f10d7efa99cc58e0a20ae82de3ad:src/rebel/v3/core/model.py` | DERIVED_LATER | NO | NO | NO | HIGH | EXCLUDE_WRONG_SCHEMA | `subclass_of`, `part_of`, `instance_of`, `facet_of`, `different_from`, `has_cause`, and `field_of_work` are not the Hohfeld target inventory. |
| local labour-law terminology JSON-LD | LYNX/PoolParty SKOS terminology graph with non-Hohfeld legal concepts | External terminology resource copied into legacy source | `estatuto_goldstandard@8e22ead...:data/term_resources/labourlawterminology/terminology.jsonld` | EXTERNAL_AUTHORITATIVE | NO | NO | NO | HIGH | EXCLUDE_UNRELATED | It has URIs and SKOS concepts but does not formalize Duty/Right/Privilege/NoRight or the target relation schema. |
| local labour-law terminology JSON | Non-JSON-LD companion terminology export | External terminology resource copied into legacy source | `estatuto_goldstandard@8e22ead...:data/term_resources/labourlawterminology/terminology.json` | EXTERNAL_AUTHORITATIVE | NO | NO | NO | HIGH | EXCLUDE_UNRELATED | A terminology export is not a Hohfeld C2 definition set or C3 ontology. |
| local RDF/OWL/TTL resources | Candidate formal ontology serializations at P0, plus the later project TBox | Scoped local search, then C3.1 | P0 search found none in the then-audited benchmark and legacy sources. `schemas/c3/c3_ontology_v1.ttl` is a later project artifact, not one of those legacy files | UNKNOWN | NO | NO | NO | HIGH | NOT_A_LEGACY_IMPORT | The P0 absence does not prove that no external ontology exists. The project TBox is recorded in its own row and is not an imported legacy ontology. |
| local SHACL resources | Candidate validation shapes | Scoped local search | No SHACL resources found in audited benchmark and specified legacy sources | UNKNOWN | NO | NO | UNRESOLVED | HIGH | NOT_AVAILABLE | Shapes must not be invented or inferred from BRAT configuration. |
| model-native Hohfeld knowledge | Any internal knowledge acquired during pretraining | Controlled model/checkpoint, not a supplied file | Not inspectable as target conditioning asset | MODEL_NATIVE | NO | NO | NO | LOW_FOR_CONDITION_BOUNDARY | MODEL_CONTROL_ONLY | It is part of model identity and must not be counted as supplied C1–C3 knowledge. |
| Hohfeld relation definitions | Textual semantics for the four target relations | Hohfeld 1913, paraphrased; four-label scope from the 2021 CEUR paper | `schemas/c2/c2_schema_v1.json` | EXTERNAL_AUTHORITATIVE | NO | YES | YES | LOW | INCLUDE_FROM_C2 | C2_SCHEMA_V1 stores sourced paraphrases. The 2022 PLN paper supports the complement account and is not the definition source. The package does not copy protected formulations, Gold examples, or external ontology axioms. |
| normative domain/range rules | Intended type constraints per relation | No independent design or authoritative source found | Not available in audited assets | UNKNOWN | NO | UNRESOLVED | UNRESOLVED | HIGH | SOURCE_REQUIRED | Neither observed signatures nor BRAT grids establish these rules. |
| stable Hohfeld URIs and formal axioms | Formal target ontology identity and commitments | Hohfeld 1913 as semantics; local provisional TBox as the artifact | `schemas/c3/c3_ontology_v1.ttl`; URN `urn:example:re-te-benchmark:c3:first-order-position:v1` | EXTERNAL_AUTHORITATIVE | NO | NO | NO | MEDIUM | PROVISIONAL_TBOX_PUBLISHED_URI_PENDING | `C3_ONTOLOGY_V1` is a local provisional TBox. Its URN is not an approved stable URI. The experimental C3 payload remains unauthorized. Syntax-only conversion of C2 remains prohibited. |
| C3_ONTOLOGY_V1 TBox | Provisional OWL TBox of the four first-order positions | Project artifact. Descriptive semantics remain in C2_SCHEMA_V1. Legal source is Hohfeld 1913 as already paraphrased for C2 | `schemas/c3/c3_ontology_v1.ttl` and `schemas/c3/c3_ontology_v1.json` | EXTERNAL_AUTHORITATIVE | NO | NO | NO | LOW | TBOX_ONLY_NOT_PAYLOAD | The file axiomatizes the studied first-order square and also asserts the fixed vocabulary individuals Performance and Forbearance. Ontology version 1.0.1 withdraws bearer/counterpart property disjointness and functionality of hasAct; hasPolarity remains functional. C3.2c updates only the two C2 hash annotation literals. It is not supplied to an extractor. The URN is a reserved example identifier, not a published namespace. It does not import external ontologies, copy C2 prose, or encode Gold signatures. |

## Source hierarchy and conflict policy

For conditioning decisions, independently documented `ORIGINAL_DESIGN` and
in-scope `EXTERNAL_AUTHORITATIVE` evidence take precedence over empirical Gold
observations and later artifacts. Later artifacts may corroborate provenance
but cannot upgrade an observation into a rule.

If sources conflict, the component is `UNRESOLVED` until the conflict and its
resolution are documented. Silence is not evidence of permission.

## Leakage controls

1. Gold canonical records and views are evaluation assets, never conditioning
   payload sources.
2. Gold counts, co-occurrences, inferred signatures, lexical lists, and aliases
   are `DERIVED_FROM_GOLD` even if produced by deterministic code.
3. Role-level knowledge about `comp`, `mod`, `MissingE1`, or `MissingE2` is
   separable from concrete annotated values.
4. Silver accepted examples remain model-dependent and outside all main C0–C3
   payloads.
5. BRAT configuration and the unrelated terminology JSON-LD cannot be relabeled
   as C3 merely because they are machine-readable.

## P0 decision

C0 and the C1 label inventory are frozen. At P0, C2 remained partial pending
sourced definitions and independently justified role, direction, domain, and
range semantics. C3 remains not ready pending a versioned formal Hohfeld
ontology package with stable URIs and defensible semantic commitments.

## C2_SCHEMA_V1 decision (2026-10-13)

`schemas/c2/c2_schema_v1.json` freezes the descriptive relation definitions
and the extraction boundaries that have a source. The following stay out of
the extractor payload: unresolved entity-type definitions, the unmapped
`e1`/`e2` to bearer/counterpart correspondence, domain and range, observed
signatures, BRAT grids, Gold and Silver examples, and any OWL, SHACL, or SWRL
import. Author confirmation from Patricia Martín-Chozas, recorded on
2026-10-13, supports directionality, the complement role, the possibility that
a modifier changes interpretation, and the meaning of `MissingE1` and
`MissingE2` as absence. That confirmation does not supply examples, an
inversion rule, or an entity-type definition. The package is implemented; its
semantic coverage is not complete, and C3 is not implemented. The C2.2
projection review keeps correlatives, opposites, and action polarity in the
model-facing payload, and withholds annotation-tag instructions and general
output or non-invention instructions. Those remain in the package. The common
instruction shell is not part of this package. At this decision the recorded
shell identity was `common-instruction-shell-v1`. The current renderer is
`common-instruction-shell-v2`; v1 remains recorded and is not sent to a model. C3.2c records a Privilege wording change: a privilege to perform is
the absence of a duty to refrain, and a privilege to refrain is the absence of
a duty to perform. The previous wording could be read as both absences at
once. NORMA-O and the
Provision Model are present under `_legacy` after the 2026-10-13 source audit
and remain excluded. The earlier P0 row that found no local RDF, OWL, or TTL
files records that search; it is not a claim that those later clones are absent.

## C3_ONTOLOGY_V1 decision (2026-10-13)

`schemas/c3/c3_ontology_v1.ttl` is a provisional TBox for the four first-order
positions. `schemas/c3/c3_ontology_v1.json` records it as `C3_ONTOLOGY_V1`,
role `TBOX_ONLY`, experimental status `NOT_EXECUTABLE`. The ontology IRI is
the reserved URN `urn:example:re-te-benchmark:c3:first-order-position:v1`.
That identifier is not a published namespace.

The TBox pins `C2_SCHEMA_V1` by the content hash
`037ab7bcf9691310f5a56a1bb7c635f6c230bdc270d37d5cc9578c88afb76d24` and the
payload hash `314a220d1916c260ff6f94c731225c43a39fa8136719794586298d47fdbe57fc`.
Those hashes replace the C3.2b pins after the Privilege definition was split
into a privilege to perform and a privilege to refrain. The Turtle change is
limited to those two annotation literals. The logical axiom set is unchanged.
`artifact_role` remains `TBOX_ONLY`. That identifier does not deny the two
fixed vocabulary individuals `Performance` and `Forbearance`; it excludes
corpus instances, which this file does not contain.
It does not copy the C2 paraphrases. `FirstOrderPosition` is the disjoint
union of Duty, Right, Privilege, and NoRight. Correlative and opposite links,
when stated, are restricted to the matching position class. The axioms do not
require those links, do not invert parties, and do not compare act or polarity.
No external ontology is imported. Gold types, observed signatures, and statute
examples are absent.

Ontology version `1.0.1` withdraws property disjointness between `hasBearer`
and `hasCounterpart`, and withdraws functionality of `hasAct`. `hasPolarity`
remains functional and does not require a polarity. An OWL 2 DL profile check
and a HermiT consistency check of that revision are recorded in
`docs/CONDITIONING_SPEC.md`. They do not authorize a payload.

This decision does not change `schemas/conditioning_conditions.json`. C3 stays
`NOT_READY`. C3.2b can place OWL Functional-Style Syntax, built from the
asserted axioms, beside the shared C2 payload. The earlier JSON fragment list
is not that projection. Neither form is approved conditioning input. The
approved URI and the ontology-backed evaluation are not implemented. The TBox
is not eligible conditioning input for C0, C1, C2, or C3.
