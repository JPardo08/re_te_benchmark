# Conditioning Specification

## Status and scope

This document is the normative P0 definition of the controlled experimental
conditions consumed later by `re_te_system`. It freezes experimental metadata,
not prompts or runtime payloads. The keywords **MUST**, **MUST NOT**, **REQUIRED**,
and **OPTIONAL** are normative.

Conditioning means target knowledge deliberately supplied to a model for an
experimental run. Knowledge already internal to a pretrained model is
`MODEL_NATIVE`; it is part of the model and is not counted as supplied target
conditioning.

This P0 specification does not select a model, define prompts, inject
conditioning, implement extractors, train or fine-tune models, select few-shot
examples, invent an ontology, implement SHACL, define new metrics, or run
REBEL/mREBEL experiments.

## Condition definitions

### C0 — OPEN

C0 supplies the input text only. It MUST NOT supply:

- target Hohfeld schema knowledge;
- Hohfeld relation labels or definitions;
- entity-type vocabulary;
- argument-role semantics;
- relation signatures, domain/range constraints, or directionality rules;
- ontology content, examples from Gold or Silver, aliases, lexical trigger
  lists, or target statistics.

Model-native pretrained knowledge is not target conditioning and does not
violate C0. Any model selection and model revision must later be controlled and
reported independently of the condition.

### C1 — LABEL-CONDITIONED

C1 is C0 plus exactly this closed target relation inventory, in this order:

1. `Duty`
2. `Right`
3. `Privilege`
4. `NoRight`

C1 supplies only the labels and the minimal provenance needed to identify that
inventory. It MUST NOT supply definitions, entity types, argument roles,
signatures, examples, inferred frequencies, Gold-derived relation statistics,
aliases, ontology content, or other schema semantics. The normative C1 asset is
`schemas/c1/hohfeld_labels.json`.

### C2 — SCHEMA-CONDITIONED

C2 is C1 plus an independently justified descriptive target schema. A complete
C2 package requires:

- textual definitions of each target relation;
- an entity-type vocabulary;
- argument-role identifiers and semantics;
- relation directionality semantics;
- any relation signatures or domain/range information that are established as
  intended schema knowledge rather than inferred from test annotations.

Other descriptive constraints may be included only when their source and
scientific justification are frozen before evaluation. C2 is descriptive:
bare labels or serialization alone do not make an asset C2-complete.

Every C2 component MUST distinguish:

1. `ORIGINAL_DESIGN`: part of the original annotation design;
2. `EXTERNAL_AUTHORITATIVE`: independently sourced domain knowledge;
3. `OBSERVED_IN_GOLD` or `DERIVED_FROM_GOLD`: empirical test-set knowledge;
4. `DERIVED_LATER`: a later transformation or artifact.

Observed Gold statistics MUST NOT automatically become conditioning knowledge.
In particular, the five observed `RelationSignature` combinations are not a
closed-world signature inventory unless independent evidence establishes that
status.

### C3 — ONTOLOGY-CONDITIONED

C3 is C2 plus an explicit formal representation of target knowledge. A complete
C3 package requires:

- stable, versioned URIs;
- explicit classes and properties;
- machine-interpretable formal relationships or constraints;
- hierarchy or axioms where scientifically justified;
- documented semantics connecting the formal representation to C2.

SHACL or equivalent validation shapes are OPTIONAL and may be included only
when scientifically justified. C3 MUST NOT be merely C2 text serialized as
Turtle, RDF, or another syntax. The C2/C3 distinction is semantic and formal:
C3 must add explicit, machine-interpretable commitments.

## Normative state vocabulary

- `FORBIDDEN`: the component MUST NOT be supplied.
- `REQUIRED`: the component is necessary for a complete condition package.
- `OPTIONAL`: the component may be supplied only under the stated provenance
  and leakage rules; its inclusion must be frozen and reported.
- `NOT_APPLICABLE`: the component has no role in that condition.
- `UNRESOLVED`: evidence is insufficient to decide whether or how the component
  may be supplied. It MUST NOT be treated as available.

Current-status values are `AVAILABLE`, `PARTIAL`, `NOT_AVAILABLE`, and
`UNRESOLVED`. Availability describes local evidence; it does not override a
condition's normative state.

## Normative knowledge-component matrix

| knowledge_component | C0 | C1 | C2 | C3 | current_status | allowed_source_class | notes |
|---|---|---|---|---|---|---|---|
| relation labels | FORBIDDEN | REQUIRED | REQUIRED | REQUIRED | AVAILABLE | ORIGINAL_DESIGN | C1 is exactly Duty, Right, Privilege, NoRight. |
| relation definitions | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | NOT_AVAILABLE | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | No defensible local definitions are frozen. |
| entity-type vocabulary | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | AVAILABLE | ORIGINAL_DESIGN | LegalAgent, LegalEntity, LegalConcept occur in original signature metadata. |
| argument roles | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | e1/e2 and MissingE1/MissingE2 identifiers exist; authoritative role semantics remain unresolved, and e1 is not presumed to be a privileged bearer/subject. |
| relation signatures | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Five Gold combinations are observed, not proven closed-world constraints. |
| domain constraints | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | BRAT grids and Gold observations are insufficient as axioms. |
| range constraints | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | BRAT grids and Gold observations are insufficient as axioms. |
| relation directionality | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | e1/e2 ordering exists; intended semantic direction is not independently documented. |
| relation hierarchy | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | Include only if independently justified. |
| formal classes/properties | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | C3 must explicitly identify the target concepts and relations it formalizes. |
| formal axioms | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | Required to distinguish C3 semantically from C2. |
| stable URIs | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | No frozen Hohfeld URI policy exists locally. |
| lexical triggers | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Concrete Gold `relation_text` values are forbidden; any lexicon requires independent pre-freeze evidence. |
| complements | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | The `comp` role may be described; concrete Gold complement values are forbidden. |
| examples | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | AVAILABLE | NOT_APPLICABLE | Few-shot and Gold-derived examples are outside the main C0–C3 experiment. |
| Gold frequencies/statistics | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | AVAILABLE | NOT_APPLICABLE | Test-set distributions are leakage, not conditioning. |
| Silver examples | FORBIDDEN | FORBIDDEN | FORBIDDEN | FORBIDDEN | AVAILABLE | NOT_APPLICABLE | Silver is model-dependent and excluded from main-condition payloads. |
| aliases | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | NOT_AVAILABLE | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Post-hoc or Gold-derived aliases are forbidden. |
| SHACL/formal validation shapes | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | OPTIONAL | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | Shapes are not mandatory merely to claim C3 and must encode justified commitments. |

`OBSERVED_IN_GOLD`, `DERIVED_FROM_GOLD`, `DERIVED_LATER`, `MODEL_NATIVE`, and
`UNKNOWN` are not eligible source classes for supplied target-schema knowledge
unless an independently established source also exists. `MODEL_NATIVE` remains
part of model control, not the conditioning payload.

## Scientific controls

### A. Test-Gold leakage

Information learned only by inspecting empirical distributions, frequencies,
or individual test annotations MUST NOT become conditioning knowledge unless
the same information is independently documented as annotation/schema design.
The independent evidence, revision, and decision must be recorded before use.

### B. Observed signatures are not axioms

The five `RelationSignature` combinations observed in the 95 typed Gold
annotations are empirical observations. They MUST NOT be converted into a
closed-world signature inventory or hard domain/range constraints without
independent evidence of intended schema status.

### C. BRAT configuration is not an ontology

Legacy `annotation.conf` is an annotation/UI configuration artifact. Its
Arg1/Arg2 grid enumerates all three-by-three type combinations for every label,
including combinations absent from Gold. It MUST NOT be interpreted as formal
ontology axioms or normative C2 domain/range knowledge without independent
evidence.

### D. `MissingE1`, `MissingE2`, `comp`, and `mod`

These are annotation-design constructs and evidence/provenance fields.
The existence of each role or concept is `ORIGINAL_DESIGN` and is distinct from
its concrete annotated values, which are `OBSERVED_IN_GOLD`. Independently
justified role semantics may enter C2/C3; concrete Gold `MissingE1`,
`MissingE2`, complement, modifier, or trigger content MUST NOT be exposed in
any C0–C3 conditioning payload.
Neither the existence nor the ordering of these constructs establishes that
`e1` is a privileged bearer or subject.

### E. Silver

The human-validated mREBEL asset is generator-dependent. Accepted records MUST
NOT silently become Gold-derived or Silver-derived few-shot conditioning in the
main controlled C0–C3 experiment. Any future auxiliary experiment must use a
separate condition identifier and disclose generator dependence.

### F. Model-native knowledge

Pretrained internal knowledge of a controlled model or baseline is part of the
model, not supplied target-schema conditioning. It MUST be controlled through
model identity/revision reporting and MUST NOT be reclassified as C1–C3 input.

## Evidence frozen at P0

- Relation inventory: `Duty`, `Right`, `Privilege`, `NoRight`.
- Entity-type labels currently known: `LegalAgent`, `LegalEntity`,
  `LegalConcept`.
- Annotation constructs currently known: `e1`, `e2`, `rel`, `comp`, `mod`,
  `MissingE1`, `MissingE2`, `RelationType`, and `RelationSignature`.
- Empirically observed signatures: `LegalAgent-LegalEntity`,
  `LegalAgent-LegalAgent`, `LegalEntity-LegalAgent`,
  `LegalEntity-LegalEntity`, and `LegalAgent-LegalConcept`.
- Relation definitions: not available.
- Normative domain/range constraints: not available.
- Formal Hohfeld ontology package: not available.

The entity types and role identifiers occur in original annotation metadata,
but this does not make observed combinations normative. Empirical counts and
individual values remain evaluation evidence, not conditioning content.

## Current readiness

### C0: READY

The condition is fully specified as input text only with all supplied target
schema knowledge forbidden.

### C1: READY

The exact four-label inventory and minimal provenance are frozen in
`schemas/c1/hohfeld_labels.json`.

### C2: PARTIAL

Entity-type labels and annotation-role identifiers exist, and signatures are
observable. However, relation definitions, authoritative argument-role and
directionality semantics, and normative domain/range knowledge are not yet
independently established. Observed signatures cannot close these gaps.

### C3: NOT READY

No defensible formal Hohfeld ontology package has been frozen. Stable URIs,
classes/properties, formal semantic commitments, and justified axioms remain
unresolved. The local labour-law terminology JSON-LD is not a Hohfeld ontology.

## Change control

The machine-readable mirror is `schemas/conditioning_conditions.json`. Any
change to condition boundaries, provenance eligibility, readiness, or component
ordering requires a version change, an updated rationale in
`docs/CONDITIONING_PROVENANCE.md`, and corresponding tests. Runtime payloads
must be separate artifacts and must identify the frozen specification version.
