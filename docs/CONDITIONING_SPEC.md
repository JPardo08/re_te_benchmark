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
REBEL/mREBEL experiments. That sentence records the P0 freeze. The C3.2c
section below adds one common instruction shell. It does not change condition
boundaries, readiness, or `schemas/conditioning_conditions.json`.

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

The first implemented package is `schemas/c2/c2_schema_v1.json`
(`C2_SCHEMA_V1`, package version `1.0.0`). It freezes descriptive paraphrases
of the four C1 relations from Hohfeld 1913, abstract role boundaries, and the
annotation guidelines that are justified for extraction. The 2021 CEUR paper
supports the four-label scope. The 2022 PLN paper supports the complement
account and is not a second definition of the four positions. It is not a complete C2: entity
type definitions, the `e1`/`e2` mapping, domain/range, and signatures remain
unresolved and are not sent to the extractor. The model-facing payload is a
projection of that package, not a second inventory. The experimental C3
condition is not implemented. `C3_ONTOLOGY_V1` is a separate provisional TBox
and is not an extractor payload.

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

#### C3.1 local TBox

`schemas/c3/c3_ontology_v1.ttl`, recorded by `schemas/c3/c3_ontology_v1.json`
as `C3_ONTOLOGY_V1`, is the first local formal artifact. It is a TBox only.
It is not an extractor payload, not a SHACL validation layer, and not an
authorization to run the C0–C3 experiment.

The ontology IRI is `urn:example:re-te-benchmark:c3:first-order-position:v1`.
That URN uses the reserved `example` namespace. Its status in the artifact is
`PROVISIONAL_NOT_PUBLISHED`, and human approval of a definitive namespace is
still pending. The file must not be described as a published ontology.

`FirstOrderPosition` is equivalent to the disjoint union of `Duty`, `Right`,
`Privilege`, and `NoRight`. The equivalence scopes that class to the four
studied first-order positions. It does not declare the second-order positions,
and it does not exclude them with a complement axiom. `correlatesWith` and
`oppositeOf` are symmetric and irreflexive, and universal restrictions limit
the class of a filler when a link is already stated. Those restrictions do not
require the link to exist and do not invert bearer and counterpart. Act and
polarity are separate. `NoRight` is a class. The C2 paraphrases are not copied
into the ontology. The package pins the current C2 content and payload hashes.

#### C3.1c consolidation

Ontology version `1.0.1` keeps the same provisional IRI and the same package
identity, `C3_ONTOLOGY_V1` version `1.0.0`. Two axioms from the first Turtle
revision were withdrawn. `hasBearer` and `hasCounterpart` keep their abstract
domain and range, and they are not property-disjoint: distinct roles do not by
themselves require distinct individuals. `hasAct` keeps its domain and range.
No functional axiom is declared for it, and that absence is not itself an
axiom that the property is non-functional. No cardinality replaces the
withdrawn axiom. `hasPolarity`
remains a provisional functional property. It limits one
`NormativeContent` individual to at most one distinct polarity and does not
require a polarity to exist. `Polarity` is not closed by enumeration. That
closure is still a human decision.

The checked-in fixture helper still applies only explicit assertions. It is
not the OWL validation. The validation below used rdflib 7.6.0 for Turtle, and
ROBOT 1.9.11 with the bundled OWL API 4.5.29 profile checker and HermiT
1.4.5.456 for OWL 2 DL. Those tools were run from a temporary directory outside
the repositories. The profile check reports the TBox in OWL 2 DL, with no
violations. HermiT reports the TBox consistent and every named class
satisfiable. `owl:Thing` is not a subclass of `FirstOrderPosition`. `NoRight`
is not equivalent to the complement of `Right`.

| id | requirement | competency question | check | axioms | evidence |
|---|---|---|---|---|---|
| CQ-COV | The scoped root is exactly the four studied positions, and the general legal universe stays open. | Is every `FirstOrderPosition` exactly one of the four, while an individual outside that class remains possible? | entailment and satisfiability | scoped union equivalence; disjointness of the four | HermiT: each of the four classes is satisfiable; an individual in the root and in the complement of all four is inconsistent; an individual typed as two of the four is inconsistent; an individual typed only as the root is consistent and is not entailed to be `Duty` or `NoRight`; a probe class outside the vocabulary is not entailed to be a `FirstOrderPosition`. |
| CQ-COR-TYPE | An existing correlative link has the matching position type. | If a `Right` has a `correlatesWith` filler, must that filler be a `Duty`? | entailment | universal restriction on `correlatesWith` | HermiT: an untyped filler of a `Right` is entailed to be a `Duty`, and is not entailed to be a `Privilege`. |
| CQ-COR-WRONG | A correlative link to the wrong position class is incoherent. | Is a `Right` linked by `correlatesWith` to a `Privilege` inconsistent? | consistency | universal restriction; disjoint position classes | HermiT: the constructed ontology is inconsistent. ROBOT merge of `inconsistent_correlative_type.ttl` with the TBox is inconsistent. |
| CQ-NO-COR | A position may be stated without an explicit correlative. | Is a `Right` with no `correlatesWith` link consistent, and is no correlative individual constructed? | consistency and non-entailment | universal, not existential, restriction | HermiT: the ontology is consistent and does not entail a `correlatesWith` link or a `NoRight` individual. ROBOT merge of `consistent_absent_correlative.ttl` is consistent. |
| CQ-NORIGHT | `NoRight` is an explicit class, not the absence of `Right` and not a prohibition. | Does asserting a `Right` fail to entail that it is a `NoRight`? | non-entailment | disjoint classes; no complement axiom | HermiT: `NoRight` is not equivalent to the complement of `Right`, and a `Right` individual is not entailed to be a `NoRight`. |
| CQ-SYM | Correlativity and opposition are symmetric when a link is stated. | Does a stated link entail the reverse link without a new individual? | entailment | `owl:SymmetricProperty` on both relations | HermiT: `correlatesWith` and `oppositeOf` each entail the reverse assertion between the same two individuals. A self-link is inconsistent. |
| CQ-NO-INVERSION | Participant inversion is not an OWL consequence. | Does a correlative link entail that the bearer of one position is the counterpart of the other? | non-entailment | domain and range only; no inversion axiom | HermiT: from a linked `Right` and `Duty`, the reverse `correlatesWith` link is entailed, and neither bearer nor counterpart of the `Duty` is entailed. |
| CQ-POLARITY | One content individual has at most one distinct polarity, and may have none. | Are a missing polarity and a single polarity consistent; are two undesignated polarity IRIs identified; and are `Performance` and `Forbearance` together inconsistent? | consistency, entailment, and identity | functional `hasPolarity`; `owl:differentFrom` between the two named polarities | HermiT: no polarity is consistent and none is entailed; one polarity is consistent and does not identify `Performance` with `Forbearance`; two polarity IRIs without `owl:differentFrom` are consistent and `owl:sameAs` is entailed; both named polarities on one content are inconsistent. `Polarity` is not entailed to be exactly those two individuals, and a third distinct polarity is consistent. |
| CQ-SAME-PARTY | Role names do not force the bearer and the counterpart to be different individuals. | Is one position with the same party individual in both roles consistent? | consistency | domain and range of the two properties; no property disjointness | HermiT: the constructed ontology is consistent. ROBOT merge of `consistent_same_party.ttl` is consistent. |
| CQ-ACTS | A content node is not limited to one act. | Are two explicitly distinct acts on one content consistent, and are they not identified? | consistency and non-entailment | no `FunctionalObjectProperty` axiom and no cardinality axiom are declared for `hasAct` | HermiT: two acts declared different are consistent and `owl:sameAs` is not entailed. Two act IRIs without `owl:differentFrom` are also consistent and are not identified. ROBOT merge of `consistent_two_acts.ttl` is consistent. |
| CQ-VOCAB | The vocabulary matches the retained profile and omits the withdrawn and excluded axioms. | Are the four positions and the abstract properties present, without imports, complements, correlative class equivalence, bearer disjointness, or a functional `hasAct`? | vocabulary query | retained declarations and exclusions | rdflib reads 166 triples and no imports, complements, existentials, or cardinalities. OWL API finds no bearer/counterpart property disjointness, finds `hasPolarity` functional, and finds no `FunctionalObjectProperty` axiom for `hasAct`. The only class equivalence is the scoped union. |

The same ROBOT merge was consistent for `consistent_unswapped.ttl` and
`consistent_opposite_different_act.ttl`, and inconsistent for
`inconsistent_self_and_overlap.ttl` and
`inconsistent_two_classes_and_polarities.ttl`. None of these fixtures is Gold
or Silver text. This validation does not authorize an extractor payload.

The tools were not installed into the project environments and are not stored
in the repository. Java was Eclipse Temurin 21.0.12.1+1 LTS for macOS aarch64,
from Adoptium. The archive checksum is SHA-256
`3623232f33a9c3baadf304480b2535f9a3cba8a58d42ecbb438ba267315d9998`. ROBOT
1.9.11 was the official JAR published on 2026-10-01. Its SHA-256 is
`53cd275c8e4c0dad1fc2c1c34174876795cd7d6b6926e1444adcbb0cb3c7ab26`. That JAR
contains OWL API 4.5.29 and HermiT 1.4.5.456. rdflib 7.6.0 was already present
in the `re_te_system_312` environment and was used only to parse Turtle. The
checked file at the C3.1c logical revision was
`schemas/c3/c3_ontology_v1.ttl`, SHA-256
`1407fc3932036347f8e84f5daa1fb0384c57f3776fb57fb0194721179fa2b8f5`. The package
content hash at that revision was
`650a3f7dd8e5711a38c211011fde3852fa6d96b5a86fd0809584b3be6016c33c`.

`scripts/validate_c3_tbox.py` rechecks those pins with the standard library.
Given an external `java` binary and `robot.jar`, the same script runs
`robot reason --reasoner HermiT` on the TBox and on each synthetic fixture
after `robot merge`. It expects the five `consistent_*.ttl` fixtures to be
consistent and the three `inconsistent_*.ttl` fixtures to be inconsistent.
The OWL 2 DL profile result came from `org.semanticweb.owlapi.profiles.OWL2DLProfile`
on that ROBOT classpath: in profile, with zero violations. The script does not
reimplement that profile checker and does not embed the JAR or a JDK. HermiT
reported the TBox consistent and reported no named unsatisfiable class.

#### C3.2a projections

The TBox bytes stay at ontology version `1.0.1`. No axiom was added.
`hasPolarity` is accepted as the modeling commitment that one normative-content
node has at most one distinct polarity. The property does not require a value.
`hasAct` stays non-functional. `Polarity` stays open: there is no `owl:oneOf`.
Sharing a polarity does not identify an act, a position, or a party. The
correlative formalization remains partial: a stated link constrains the filler
class, and it does not swap participants or identify normative content. None of
these commitments is a validation of a binary `(subject, relation, object)`
prediction. The common instruction shell is still not defined. In
`re_te_system`, Pythia uses its own `basic-v1` Turtle prompt and GoLLIE uses
`gollie-prompt-v1`. Those shells are not part of these projections.

`c3_model_payload` reuses the C2 payload and appends `formal`, a list of
fragments read from the asserted TBox. Comments, provenance, hashes, and the
provisional IRI are not included. `c3_nl_model_payload` appends
`formal_natural`, rendered from those same fragments. It is a secondary
control, not a fifth main condition and not a second legal inventory. The
canonical JSON lengths at the C3.2a revision were 5789 characters for C2, 10443 for
the formal projection, and 8759 for the natural-language control. The
serializations differ, and that difference is not assumed to be neutral.

The projections do not change `schemas/conditioning_conditions.json`. C3 stays
`NOT_READY` and the package stays `NOT_EXECUTABLE`.

#### C3.2b semantic consolidation

C3.2b does not add or remove a logical axiom and does not change
`owl:versionInfo` `1.0.1`. It changes two things that are not logical axioms.
The shared C2 projection no longer sends `extraction_boundaries` or
`abstract_roles.textual_arguments` to the model. Those records stay in
`C2_SCHEMA_V1`. The boundary sentence now says that the descriptive schema
supplies no annotation entity-type definitions and no domain or range
constraints on those annotation types. It does not deny OWL domains of abstract
properties, and it is not part of the model payload. The textual-argument
record states the extractor contract and the unresolved mapping to legal roles,
so it remains methodological metadata. Bearer, counterpart, and normative
content remain in the shared payload. The C2 content hash is now
`6793ab0e2d4df7bc872064d255d9cc27bed8082ad0047efd1aa31236ac120538` and the C2
payload hash is now
`4d3ad2adce9e6d2c9a453d3df7c61583270dcc0664c94c7f90e241710689fd9a`.

The Turtle file changes only the `h:c2ContentSha256` and `h:c2PayloadSha256`
annotation literals, so that the provenance pins match those hashes. Its file
SHA-256 is now
`876f2d160d93c1866d40ae4634c9e7f0fe4be6c3099c4071bf0aef71282f0216`. The package
content hash is now
`1ed6fb2a3a883fc61a638ae26e97c2f485657a41d78f24cc52e7bff8d8f60852`. The
namespace remains the provisional URN and is not approved for publication.

The C3.2a `formal` list is no longer the experimental arm. It turned absent
axioms into boolean fields and then into sentences such as "not functional" and
"No link is required". Those sentences are not axioms. The experimental C3
payload is now `owl_functional`: OWL 2 Functional-Style Syntax rendered from
axioms the Turtle file asserts. Declarations, the scoped union, both
disjointness axioms, domains, ranges, symmetry, irreflexivity, functionality of
`hasPolarity`, property disjointness of the two relations, the eight universal
restrictions, the two polarity individuals, and their difference are included
because each one is asserted. Absence of functionality, symmetry, an
existential, a cardinality, or an enumeration is recorded by `audit_axiom_records`
as `UNSPECIFIED` and is not inserted into either experimental payload. No
reasoner result is labeled `ENTAILED` or `NOT_ENTAILED` by that audit.

`c3_nl_model_payload` paraphrases only those included axioms, one sentence per
axiom identifier. It does not add a requirement, an exclusion, a negation, a
cardinality, or a vocabulary closure. The canonical JSON lengths at the C3.2b
revision are 5440 characters for C2, 8908 for the OWL projection payload, and
12389 for the natural-language control. The OWL string itself is shorter than
the natural-language list. That difference is a serialization difference. It is
not evidence that the two arms are experimentally equivalent, and it is not
evidence that a model will not truncate one of them.

`scripts/validate_c3_tbox.py` still checks the pins. When an external Java
binary and `robot.jar` are supplied, it also asks ROBOT to parse the Functional
projection with `--input-format ofn` and then runs HermiT on the converted
ontology. The script does not implement a parser or a reasoner. C3 remains
`NOT_READY` and `NOT_EXECUTABLE`. At the end of C3.2b the common instruction
shell was still absent.

#### C3.2c semantic refinement and instruction shell

C3.2c changes the Privilege definition in `C2_SCHEMA_V1`. The previous sentence
could be read as the simultaneous absence of a duty to perform and a duty to
refrain. The replacement states two directed alternatives. A privilege to
perform an act is the absence of a duty to refrain from that act. A privilege
to refrain is the absence of a duty to perform it. One privilege does not
remove both duties. The four labels, the other three definitions, action
polarity, correlatives, and opposites stay in place. The contrast used for the
wording is the Spring 2022 Stanford Encyclopedia of Philosophy entry on rights.
That entry is not copied. No Gold sentence was used. Package version stays
`1.0.0` because the validator and the C3 dependency pin that version. The new
content and payload hashes identify the revision.

The Turtle file again changes only `h:c2ContentSha256` and
`h:c2PayloadSha256`. `owl:versionInfo` stays `1.0.1`. No class, property, or
logical axiom is added. The C2 content hash is now
`037ab7bcf9691310f5a56a1bb7c635f6c230bdc270d37d5cc9578c88afb76d24` and the C2
payload hash is now
`314a220d1916c260ff6f94c731225c43a39fa8136719794586298d47fdbe57fc`. The Turtle
SHA-256 is now
`5dfac3fae2f74aa9aa1f22efb2d41531b10eba43117f67fdfd8601cd4209d397`. The package
content hash is now
`fbccf154a4b822476e73ecca10c306536ab70c08383e5d4a972ead8e9e4776e7`.

`artifact_role` remains `TBOX_ONLY` so the existing package and Turtle
contracts keep that identifier. The identifier is narrower than the file. The
file contains class and property axioms and also two fixed vocabulary
individuals, `Performance` and `Forbearance`, with `ClassAssertion` and
`DifferentIndividuals`. Those assertions are part of the polarity vocabulary.
The file contains no individual taken from a corpus document. `artifact_role_note`
records that distinction. The individuals are not removed.

Two C3-NL paraphrases are narrowed where the previous English could change the
logical reading. `hasPolarity is functional` now says that one content is
linked to no more than one distinct polarity, and it still does not say that a
polarity is required. The eight universal restrictions say `every linked
individual` instead of `filler`. Domain and range sentences are unchanged.
`has domain` and `has range` can still be misread as a requirement that the
link exist; the sentences do not say that, and a broader rewrite is not made
here. The canonical JSON lengths at the C3.2c revision are 5672 characters for C2, 9140 for the OWL projection payload, and 12778 for the natural-language control.

`common-instruction-shell-v1` is implemented in
`src/re_te_benchmark/conditioning/shell.py`. The instruction text is the same
for C0, C1, C2, C3, and C3-NL. The only condition variable is the
target-schema conditioning slot. C0 leaves that slot empty. C1 places the four
labels there, without the C1 provenance record. C2, C3, and C3-NL place the
existing canonical payloads there. The shell does not name the four labels,
does not reuse Pythia `basic-v1` or GoLLIE `gollie-prompt-v1`, and does not
tell the model how to map `e1` or `e2`.

The requested output is one tab-separated line per relation, with the fields
`subject`, `relation`, and `object`. Those are the three fields of
`ParsedTriple` and of the evaluation export. The shell does not invent a JSON
schema. It is not Turtle, because a Turtle predicate must be an IRI and C0
must be able to emit an open relation name. No parser in `re_te_system`
currently reads this line format. Connecting a backbone therefore still needs
an adapter. That adapter is not implemented. Pythia remains on Turtle, and
that difference is a pending methodological choice, not a mapping derived from
Gold. The evaluator compares relation strings after its existing normalizer. It
does not translate an open C0 name into Duty, Right, Privilege, or NoRight.
The shell does not filter or repair one condition differently from another.
C3 stays `NOT_READY` and `NOT_EXECUTABLE`.

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
| relation definitions | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | AVAILABLE | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Descriptive paraphrases of the four C1 relations are frozen in `schemas/c2/c2_schema_v1.json`. They do not close C3. |
| entity-type vocabulary | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | PARTIAL | ORIGINAL_DESIGN | The three identifiers are retained in C2_SCHEMA_V1. Their definitions conflict across 2021-2023 sources and are `UNRESOLVED_DEFINITION`, so they are withheld from the extractor payload. |
| argument roles | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | C2_SCHEMA_V1 states abstract bearer, counterpart, and normative content, and states that e1/e2 are not those roles. The dataset mapping remains unresolved. |
| relation signatures | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Five Gold combinations are observed, not proven closed-world constraints. |
| domain constraints | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | BRAT grids and Gold observations are insufficient as axioms. |
| range constraints | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | BRAT grids and Gold observations are insufficient as axioms. |
| relation directionality | FORBIDDEN | FORBIDDEN | REQUIRED | REQUIRED | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | The four relations are directed. C2_SCHEMA_V1 forbids swapping arguments to emit a correlative. It does not map e1/e2 onto bearer/counterpart. |
| relation hierarchy | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | PARTIAL | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | `C3_ONTOLOGY_V1` introduces `FirstOrderPosition` as the scoped union of the four C1 classes. That hierarchy is not part of the C2 payload and does not add second-order positions. |
| formal classes/properties | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | PARTIAL | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | `C3_ONTOLOGY_V1` declares the four position classes and abstract role properties under a provisional URN. That file is not an extractor payload. |
| formal axioms | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | PARTIAL | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | The TBox contains disjointness, a scoped union equivalence, and universal restrictions on existing correlative and opposite links. Version 1.0.1 does not make bearer and counterpart property-disjoint and does not make `hasAct` functional. It does not contain existential correlatives, participant inversion, or Gold domain/range. |
| stable URIs | FORBIDDEN | FORBIDDEN | NOT_APPLICABLE | REQUIRED | NOT_AVAILABLE | EXTERNAL_AUTHORITATIVE; ORIGINAL_DESIGN | A provisional example URN is used locally and is explicitly not a published namespace. No approved stable URI policy exists. |
| lexical triggers | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | UNRESOLVED | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | Concrete Gold `relation_text` values are forbidden; any lexicon requires independent pre-freeze evidence. |
| complements | FORBIDDEN | FORBIDDEN | OPTIONAL | OPTIONAL | PARTIAL | ORIGINAL_DESIGN; EXTERNAL_AUTHORITATIVE | C2_SCHEMA_V1 describes `comp` as complement content. Concrete Gold complement values remain forbidden. |
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

The bullets above record the P0 freeze. They are not a description of the
later `C3_ONTOLOGY_V1` TBox.

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

`C2_SCHEMA_V1` is implemented and reproducible. Its relation definitions are
sourced paraphrases, not Gold-derived text. Readiness stays partial because
the package does not define the three entity types, does not map `e1`/`e2` to
bearer and counterpart, and does not supply domain, range, or signature
constraints. Observed signatures still cannot close those gaps.

### C3: NOT READY

The experimental condition remains not ready. `C3_ONTOLOGY_V1` now supplies a
provisional local TBox, and C3.2a can project that TBox beside the C2 payload.
Ontology version `1.0.1` records two withdrawn axioms and an independent OWL 2
DL check. Neither that check nor the projection approves model-facing use.
There is still no approved stable URI and no ontology-backed evaluation. The
machine-readable manifest therefore keeps the formal components unresolved: in
that file, unresolved means the experimental condition is not yet allowed to
supply them. The local labour-law terminology JSON-LD is not this TBox. The
TBox is not an extractor payload.

## Change control

The machine-readable mirror is `schemas/conditioning_conditions.json`, schema
version `1.1.0`. Version `1.1.0` records that descriptive relation definitions
now exist in `C2_SCHEMA_V1` and that entity-type definitions remain unresolved.
Any change to condition boundaries, provenance eligibility, readiness, or
component ordering requires a version change, an updated rationale in
`docs/CONDITIONING_PROVENANCE.md`, and corresponding tests. Runtime payloads
must be separate artifacts and must identify the frozen specification version.
`C2_SCHEMA_V1` identifies that version in the knowledge package and in its
integrity hashes. The model-facing projection does not repeat the package
identity, the shared output contract, or historical annotation-tag instructions.
Those instructions belong to `common-instruction-shell-v1`, which is not
part of the C2 payload. `C3_ONTOLOGY_V1` does not change
`schemas/conditioning_conditions.json`: condition boundaries, readiness, and
the unresolved experimental gaps stay as in schema version `1.1.0`. The TBox
package has its own integrity hashes and pins the C2 hashes.
