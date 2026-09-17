# Hohfeld C2/C3 Source Audit

**Iteration:** `HOHFELD_C2_C3_SOURCE_AUDIT`

**Date:** 2026-09-17

**Type:** scientific audit; not a normative source freeze

**Scope:** `re_te_benchmark/**`, `_legacy/**`, and independently accessible
scholarly/formal sources

**Normative boundary:** `docs/CONDITIONING_SPEC.md` and
`docs/CONDITIONING_PROVENANCE.md`

**Claim tags:** `[FACT]` local or directly verified evidence ·
`[EXTERNAL_SOURCE]` independently published evidence · `[INFERENCE]`
conservative synthesis · `[CONFLICT]` incompatible evidence · `[UNKNOWN]`
evidence not established · `[RECOMMENDATION]` proposed next decision

## 1. Executive verdict

[FACT] No local legacy file supplies definitions for `Duty`, `Right`,
`Privilege`, or `NoRight`, authoritative semantics for `e1`/`e2`, definitions
of `LegalAgent`/`LegalEntity`/`LegalConcept`, or a frozen Hohfeld ontology.

[FACT] The publication associated with the initial annotation project,
Martín-Chozas and Revenko (2021), explicitly limits its experiment to the four
deontic Hohfeld relations and defers the four potestative relations. It therefore
explains the four-label scope. It lists the square and claims that domain/range
restrictions were manually defined, but it does not publish a complete
restriction table or textual definitions for the four labels.

[EXTERNAL_SOURCE] Hohfeld (1913) provides authoritative semantics for the
first-order square: right/claim correlates with duty; privilege correlates with
no-right; right and no-right are opposites; privilege and duty are opposites.
This primary source can support concise C2 definitions and terminology, without
adding Power, Liability, Immunity, or Disability to the benchmark inventory.

[FACT] External theory also establishes bearer/counterpart semantics and
correlative role reversal. It does not establish that this dataset's `e1` is
always the Hohfeld-position bearer or that `e2` is always its counterpart.
That bridge appears explicitly only in later TeresIA work.

[CONFLICT] The 2021 project paper classifies example workers and employers as
`LegalEntity` and also uses `LegalDocument` and `Duration`. A 2023 follow-up
defines `LegalAgent` as a natural person, `LegalEntity` as a non-natural person
or corporation, and `LegalConcept` residually. The current Gold uses only
`LegalAgent`, `LegalEntity`, and `LegalConcept`. This is schema evolution, not a
stable externally grounded type system.

[FACT] Several formal Hohfeld-related models exist, but no single verified
artifact is both semantically exact for this four-label benchmark, accessible
and versioned, stably named, and clearly reusable under a known license.

[RECOMMENDATION] Freeze C2 relation definitions from Hohfeld (1913), with the
four-relation scope justified by Martín-Chozas and Revenko (2021). Do not yet
freeze `e1`/`e2` role mapping, entity-type definitions, domain/range, or closed
signatures. For C3, author a new benchmark-specific formalization later, informed
by Hohfeld, Francesconi's bearer/counterpart pattern, UFO-L, LKIF-Core, and
LegalRuleML, rather than copying any candidate artifact unchanged.

## 2. Method and scientific controls

[FACT] The four frozen benchmark/specification documents were read in full
before source discovery:

- `docs/CONDITIONING_SPEC.md`
- `docs/CONDITIONING_PROVENANCE.md`
- `docs/BENCHMARK_SPEC.md`
- `docs/GOLD_POLICY.md`

[FACT] Local searches covered the requested `_legacy` trees and audit
documents. Repository history was inspected read-only. External discovery used
publisher pages, institutional repositories, standards pages, scholarly PDFs,
and public source-repository metadata. No model was run and no canonical Gold
or Silver artifact was modified.

[FACT] Empirical Gold examples and distributions were not used to infer
definitions, role direction, type semantics, or constraints. They remain
evaluation evidence under the frozen leakage policy.

[UNKNOWN] Web availability was checked on 2026-09-17 and is not a permanence
guarantee. A paper's statement that code or an OWL file exists was not treated
as an accessible formal artifact unless an artifact endpoint or versioned source
was independently located.

## 3. Local source audit

### 3.1 Exact local lineage

| Layer | Evidence | Classification | Scientific use |
|---|---|---|---|
| Original typed annotations | `_legacy/estatuto_goldstandard@8e22ead8359515164979e85e9fe1f3741f838826:data/old/rels` | `[FACT] ORIGINAL_DESIGN + OBSERVED_IN_GOLD` | Label inventory and role identifiers only; no definitions. |
| Local repository history | `relations per article added` at commit `046c5540b3dbeaf778eafbea3ce6bea25dd6a407` (2024-07-26); `updated annotations` at `695120dc64f9df696c1bc78588e087f0d8919250` (2025-02-17) | `[FACT] provenance` | Shows the frozen files post-date the 2021 publication; commit messages contain no semantics. |
| Published sentence projection | `_legacy/teresia-mrebel-corpus-juri@0d79c10bd12def9d6f0120966ede0d609a3fdbd8:gold_standard/laboral/**` | `[FACT] DERIVED_FROM_GOLD` | Regression/projection evidence only. |
| BRAT configuration | Same repository, `gold_standard/laboral/brat/annotation.conf` | `[FACT] DERIVED_LATER` | UI/export grid; not ontology or normative range. |
| mREBEL and Silver | `_legacy/teresia-mrebel/**`; benchmark human-validated Silver | `[FACT] DERIVED_LATER`, model-dependent | Wrong relation family and prohibited as main C0–C3 conditioning. |
| Local terminology JSON-LD | `_legacy/estatuto_goldstandard/data/term_resources/labourlawterminology/terminology.jsonld` | `[FACT] EXTERNAL_AUTHORITATIVE`, non-Hohfeld | SKOS labour terminology; no Hohfeld target semantics. |

[FACT] `_legacy/estatuto_goldstandard/data/old/rels/intro.txt` is a short term
list, not annotation guidance. No README, guideline, bibliography, ontology,
definition file, or type glossary is present in that repository snapshot.

[FACT] No `.owl`, `.rdf`, `.ttl`, or SHACL resource occurs in the requested
local Hohfeld lineage. The one local JSON-LD resource is the unrelated LYNX
labour-law terminology.

### 3.2 Local semantics actually explicit

| Candidate knowledge | Explicit locally? | Evidence | Decision |
|---|---:|---|---|
| Four labels | Yes | `RelationType` metadata | `[FACT] original inventory; C1 only` |
| `RelationSignature` syntax | Yes | `TypeA-TypeB (e1, e2)` | `[FACT] design syntax, not a closed constraint set` |
| `e1`, `e2`, `rel`, `comp`, `mod`, `MissingE1`, `MissingE2` identifiers | Yes | Inline tags and metadata | `[FACT] identifiers only` |
| Duty/Right/Privilege/NoRight definitions | No | No guideline or prose | `[UNKNOWN] source required` |
| `e1`/`e2` as bearer/counterpart | No | No local semantic declaration | `[UNKNOWN] do not infer from annotations` |
| Type definitions | No | Bare type labels only | `[UNKNOWN] source required` |
| Normative domain/range | No | Gold observations and later BRAT grid only | `[FACT] not available` |
| Stable target URIs or axioms | No | No local formal package | `[FACT] not available` |

[FACT] Two author-encoded `MissingE1` fields occur in the original source, at
`data/old/rels/articulo_40.txt:13` and `articulo_67.txt:8`. Concrete values
remain redacted here because they are Gold content. Their existence was omitted
from the frozen construct inventory and provenance register and must be handled
in a later normative revision, not silently added during this audit.

[FACT] All 95 source `RelationSignature` lines use the literal ordered suffix
`(e1, e2)`, and all 95 `RelationType` lines bind the label to `(rel)`. This
establishes positional ordering and type-to-marker binding as
`ORIGINAL_DESIGN`. It does not establish legal subject/object,
bearer/counterpart, or holder/correlative-party semantics. The symmetric
presence of both `MissingE1` and `MissingE2` further cautions against treating
`e1` as a privileged semantic subject.

[FACT] One source annotation file, `articulo_36.txt`, has unbalanced `comp`
markup (four opening versus two closing tags). This is annotation-hygiene
evidence, not conditioning knowledge.

## 4. Original project and publication lineage

### 4.1 Dataset-author publication

[EXTERNAL_SOURCE] Patricia Martín-Chozas and Artem Revenko, “Thesaurus
Enhanced Extraction of Hohfeld's Relations from Spanish Labour Law,”
DeepOntoNLP 2021, CEUR Workshop Proceedings 2918, pp. 30–38, has no DOI in the
publisher record. Stable paper:
<https://ceur-ws.org/Vol-2918/paper4.pdf>.

[EXTERNAL_SOURCE] Section 1 divides Hohfeld's relations into:

- deontic: `Right`, `Duty`, `No-Right`, `Privilege`;
- potestative: `Power`, `Liability`, `Disability`, `Immunity`.

The paper states that the preliminary experiment focuses on the deontic
relations and leaves the potestative relations for future work. This is direct
author evidence for the benchmark's four-relation scope.

[FACT] The publication-associated repository is
<https://github.com/pmchozas/term_relex>, currently pinned for this audit at
commit `69136ce8e4276e6501c4ac3cc5b7154d77ed03d2` (2023-06-13). It has no
declared repository license. It contains earlier annotated data and, since
commit `06436f9b52c6dddbbff2c70b42e97663f41edab0` (2021-11-15), a copy of
`ontology/ProvisionModel.owl`.

[FACT] Its companion `ontology/right_sample.owl` is a pre-current-Gold,
dataset-author-repository witness for the selected Provision Model pattern. It
instantiates a `Right` with `hasRightBearer`, `hasRightCounterpart`,
`hasRightObject`, and `hasRightAction`. This independently strengthens the
project lineage for the abstract Bearer/Counterpart/Object/Action roles. The
file does not refer to `e1`, `e2`, or `comp`, so it does not prove the marker
mapping.

[FACT] The exact local benchmark source is a later repository and revision:
`estatuto_goldstandard` gained article relation files in 2024 and was updated in
2025. No publication was found that explicitly documents the semantics of this
exact revision.

### 4.2 What the project paper does and does not define

| Question | Result |
|---|---|
| Defines the four labels individually? | `[FACT] NO. It names the square and explains deontic versus potestative relations, but gives no four-label glossary.` |
| Cites Hohfeld? | `[FACT] YES. Hohfeld (1913) is reference 10.` |
| Explains why only four? | `[FACT] YES. It deliberately limits the preliminary experiment to deontic relations.` |
| Publishes argument-role semantics? | `[FACT] NO. It discusses subject/object entities but does not define `e1` and `e2` as Hohfeld bearer/counterpart.` |
| Claims domain/range restrictions? | `[FACT] YES. Section 3.2 says they were manually defined for relation types.` |
| Publishes a complete domain/range table? | `[FACT] NO.` |
| Uses the current three entity types consistently? | `[CONFLICT] NO. Examples use `LegalEntity`, `LegalDocument`, `Duration`, and `LegalConcept`; current Gold uses a different three-label inventory.` |
| Identifies formal vocabularies? | `[FACT] YES. Table 1 maps Right→`lrml:Right`/`prv:Right`, Duty→`lrml:Obligation`/`prv:Duty`, No-right→`lrml:Prohibition`/`prv:Prohibition`, and Privilege→`lrml:Permission`/`prv:Permission`.` |

[CONFLICT] Mapping Hohfeldian `NoRight` directly to `Prohibition` is not
semantically neutral. A no-right/no-claim is the absence of a claim correlating
with another party's privilege; a prohibition is a duty not to act. Therefore
Table 1 is useful project lineage but is not by itself a safe C2 definition or
C3 equivalence axiom.

### 4.3 Later TeresIA interpretation

[EXTERNAL_SOURCE] Gabriela Argüelles Terrón, Patricia Martín-Chozas, and Víctor
Rodríguez-Doncel, “Event Extraction and Semantic Representation from Spanish
Workers' Statute Using Large Language Models,” JURIX 2023, FAIAP 379,
pp. 329–334, DOI <https://doi.org/10.3233/FAIA230983>. The extended master's
thesis is available at <https://oa.upm.es/75904/>.

[FACT] The extended thesis explicitly says:

- `e1` and `e2` are subject and object;
- subject is the action agent and object the receiver;
- Provision Model `Bearer`, `Counterpart`, and `Object` correspond respectively
  to subject, object, and complement;
- `LegalAgent` means natural person;
- `LegalEntity` means non-natural person, normally a corporation or enterprise;
- `LegalConcept` is the residual category.

[CONFLICT] These definitions do not match the 2021 paper's example typing,
which classifies worker/employer as `LegalEntity` and introduces
`LegalDocument` and `Duration`. They also conflate linguistic agent/receiver
roles with Hohfeld bearer/counterpart roles, which are not identical in every
surface construction.

[INFERENCE] The 2023 work is academically traceable and co-authored by a
dataset author, but it is a later reinterpretation and transformation of the
dataset. Under the frozen provenance boundary it may corroborate a future
decision, but cannot alone establish `ORIGINAL_DESIGN`.

### 4.4 Earliest downstream `e1`/`e2` mapping

[FACT] A Hohfeld notebook now visible at
`oeg-upm/teresia-annotators@d0357fccb018514f01d157f1abdbb5bbcc8e0736:src/hohfeld/hohfeld_estatuto.ipynb`
(2024-12-03) maps `e1→head`, `e2→tail`, and signature positions to
`head_type`/`tail_type`. The same notebook blob later entered
`_legacy/teresia-mrebel` history and was subsequently deleted there.

[FACT] This is the earliest recovered explicit head/tail decision, but it was
authored on the downstream TeresIA side by a different committer after the
original article relations were added. It contains no Hohfeld citation,
definitions, role glossary, or prompt. It is `DERIVED_LATER`, not evidence that
the annotator designed `e1` as a Hohfeld bearer.

[FACT] The same historical path requires inline `e1`, `e2`, and `rel`, whereas
the later corpus-juri parser requires `e1` and `rel` but accepts absent inline
`e2`. These downstream parsers disagree on eligibility and neither resolves
source semantics.

[FACT] The public `oeg-upm/teresia-brat-server` snapshot contains a generated
`estatuto_hohfeld/relaciones.txt` introduced in 2025. It lists observed
Arg1/Arg2 type combinations rather than definitions. Its existence does not
upgrade observed signatures to normative constraints.

## 5. Authoritative Hohfeld theory

### 5.1 Primary sources

[EXTERNAL_SOURCE] Wesley Newcomb Hohfeld, “Some Fundamental Legal Conceptions
as Applied in Judicial Reasoning,” *Yale Law Journal* 23(1), 1913, pp. 16–59,
DOI <https://doi.org/10.2307/785533>. Yale repository:
<http://hdl.handle.net/20.500.13051/11079>.

[EXTERNAL_SOURCE] Wesley Newcomb Hohfeld, “Fundamental Legal Conceptions as
Applied in Judicial Reasoning,” *Yale Law Journal* 26(8), 1917, pp. 710–770,
DOI <https://doi.org/10.2307/786270>.

[FACT] The 1913 article and the 1919 collected volume have openly accessible
historical scans. Internet Archive marks the 1919 volume as
`NOT_IN_COPYRIGHT`; modern publisher editions have their own rights.

### 5.2 Defensible concise semantics

[EXTERNAL_SOURCE] Hohfeld states at journal p. 30 that the fundamental legal
relations are *sui generis* and that attempts at formal definition are
unsatisfactory; he proceeds through the table of correlatives/opposites and
examples. Accordingly, the primary source authoritatively fixes conceptual
meaning and terminology, but should not be cited as supplying modern formal
biconditional definitions.

[EXTERNAL_SOURCE] Leif Wenar and Rowan Cruft, “Rights,” *Stanford Encyclopedia
of Philosophy* (first published 2005; substantive revision 2025), supplies the
modern biconditional formulations: a privilege to act iff there is no duty not
to act, and a claim that another act iff that other party has a directed duty.
<https://plato.stanford.edu/entries/rights/>.

These are audit paraphrases combining primary conceptual authority with modern
formal clarification, not yet frozen C2 wording:

| Benchmark label | Primary-source semantics | Correlative orientation | Audit status |
|---|---|---|---|
| `Right` | `[EXTERNAL_SOURCE]` A right in Hohfeld's strict sense is a claim by X against Y concerning Y's conduct. Hohfeld proposes “claim” as its best synonym. | X's Right/Claim against Y ↔ Y's Duty toward X, with the same normative content. | `AUTHORITATIVE` |
| `Duty` | `[EXTERNAL_SOURCE]` A duty is the directed obligation borne by Y toward X that correlates with X's right/claim. | Y Duty→X ↔ X Right/Claim→Y. | `AUTHORITATIVE` |
| `Privilege` | `[EXTERNAL_SOURCE]` X has a privilege to act when X has no duty toward Y to refrain from that act; Hohfeld treats “liberty” as equivalent in this relational sense. | X Privilege→Y ↔ Y NoRight/NoClaim→X regarding the contrary conduct. | `AUTHORITATIVE` |
| `NoRight` | `[EXTERNAL_SOURCE]` Y has no-right with respect to X's privileged conduct: Y lacks the claim that X refrain. It is not a general absence of all rights. | Y NoRight→X ↔ X Privilege→Y. | `AUTHORITATIVE` |

[EXTERNAL_SOURCE] Hohfeld's caution about content is essential: a privilege to
perform an act negates a duty to refrain from that act, not a duty to perform
the same act. A future C2 definition must preserve action polarity.

[INFERENCE] These definitions are independent of test Gold and can be scoped to
the benchmark's four labels. They do not justify any `LegalAgent`/
`LegalEntity`/`LegalConcept` restriction.

## 6. Four-relation versus eight-position problem

[EXTERNAL_SOURCE] Classical Hohfeld contains eight positions arranged in two
families:

| Family | Positions | Function |
|---|---|---|
| First-order / deontic | Right/Claim, Duty, Privilege/Liberty, NoRight/NoClaim | Regulates whether ordinary conduct is required or permitted and the directed positions of two parties. |
| Second-order / potestative | Power, Liability, Immunity, Disability | Regulates the creation, modification, or extinction of legal positions. |

[FACT] Martín-Chozas and Revenko (2021) explicitly select the first family for
their preliminary experiment and reserve the second for future work.

[INFERENCE] The benchmark's four labels are therefore not an accidental
truncation of an otherwise intended eight-class classifier. They correspond to
one Hohfeldian square/family and define a narrower extraction task.

[RECOMMENDATION] C2 may cite the full eight-position framework to explain scope,
but MUST expose only the existing four labels as target knowledge. Importing
Power, Liability, Immunity, or Disability as additional target classes,
examples, output options, or inferred labels would change the task and violate
the frozen C1 inventory.

## 7. Terminology alignment candidates

No alias is created by this audit.

| benchmark_label | external_term | source | relationship | confidence/evidence | safe_to_use_as_definition_source |
|---|---|---|---|---|---|
| Right | Claim | Hohfeld 1913, pp. 30–32 | Hohfeld's proposed synonym for “right” in its strict claim-right sense | HIGH; primary source | YES |
| Right | Claim-right | Modern Hohfeld scholarship; Herstein, SEP “Legal Rights”, §3.1 | Disambiguated name for the same first-order incident | HIGH; strong secondary | YES |
| Right | generic “right” | General legal usage | Broader term that may include privilege, power, and immunity | HIGH evidence of overloading | NO |
| Privilege | Liberty | Hohfeld 1913; Herstein, SEP §3.1.2 | Equivalent in the Hohfeldian first-order relational sense | HIGH; primary plus strong secondary | YES |
| Privilege | Permission | LegalRuleML; Provision Model; project paper | Related deontic concept; may be weak/strong and not necessarily directed as Hohfeld requires | MEDIUM; semantic broadening risk | UNRESOLVED |
| NoRight | No-right / No-Right | Hohfeld 1913; dataset publication | Orthographic variants of Hohfeld's original term | HIGH | YES |
| NoRight | No-claim | Hohfeld 1917 usage and modern scholarship | Modern disambiguating replacement after Right→Claim | HIGH | YES |
| NoRight | Prohibition | Martín-Chozas and Revenko 2021 Table 1; LegalRuleML term | Not equivalent in classical Hohfeld: prohibition imposes a duty not to act | HIGH conflict evidence | NO |
| Duty | Obligation | LegalRuleML; deontic literature | Closely related, but C2 must retain directed duty toward a counterpart | HIGH with direction caveat | YES, with qualification |

## 8. Argument semantics and directionality

### 8.1 Theory-level semantics

[EXTERNAL_SOURCE] Francesconi (2016) represents a duty as
`Duty(Bearer=Supplier, Counterpart=Consumer)` and its correlative as
`Right(Bearer=Consumer, Counterpart=Supplier)`. Peters and Wyner (2016) use
`DutyBearer`, `DutyCounterpart`, `DutyAction`, and `DutyObject` with the same
orientation.

[EXTERNAL_SOURCE] Slootweg et al. (2016) extend the same pattern to
Privilege/NoRight and explicitly swap bearer/counterpart across correlatives.

The theory-level ordered interpretation is:

| Position asserted | First party | Second party | Correlative view |
|---|---|---|---|
| Right(x, y, φ) | right/claim bearer | duty bearer / counterpart | Duty(y, x, φ) |
| Duty(x, y, φ) | duty bearer | right/claim bearer / counterpart | Right(y, x, φ) |
| Privilege(x, y, φ) | privilege/liberty bearer | no-right holder / counterpart | NoRight(y, x, φ) |
| NoRight(x, y, φ) | no-right/no-claim holder | privilege holder / counterpart | Privilege(y, x, φ) |

[EXTERNAL_SOURCE] A complete formal relation needs normative content `φ`
(action or omission), not only two party arguments.

### 8.2 Bridge to `e1`/`e2`

[FACT] The original annotation syntax orders `RelationSignature` as `(e1, e2)`.
It does not name either argument `Bearer` or `Counterpart`.

[FACT] The 2023 follow-up maps subject→Bearer, object→Counterpart and states
that `e1`/`e2` are subject/object. This bridge is explicit but later.

[CONFLICT] The same follow-up also describes subject/object as linguistic
agent/receiver. Surface agent and Hohfeld-position bearer need not coincide in
passive clauses or in a Right whose counterpart performs the relevant action.

[RECOMMENDATION] Freeze abstract Hohfeld bearer/counterpart directionality as a
candidate C2 semantic source, but do not freeze `e1=Bearer` and
`e2=Counterpart` until original annotation guidance or dataset-author
confirmation resolves the bridge. Therefore:

- abstract Hohfeld role semantics: `READY_TO_DRAFT`;
- current `e1`/`e2` mapping: `PARTIAL`;
- benchmark relation directionality: `PARTIAL`.

## 9. Entity-type semantics

| Type | Original local definition | Dataset-associated external evidence | Independent ontology link | Verdict |
|---|---|---|---|---|
| `LegalAgent` | None | 2023: natural person | None established | `[CONFLICT]` likely project-specific; not ready |
| `LegalEntity` | None | 2021 examples include workers/employers and other items; 2023 restricts to non-natural person/corporation | None established | `[CONFLICT]` not ready |
| `LegalConcept` | None | 2023 residual “neither natural person nor corporation” | None established | `[UNKNOWN]` too broad and not ontologically grounded |

[FACT] The LYNX terminology resource does not define these three annotation
types. The Provision Model explicitly allows attribute values from arbitrary
domain ontologies and does not impose this type vocabulary.

[INFERENCE] These labels appear locally invented or adapted for annotation.
Their occurrence in signatures proves inventory membership, not semantics.

[RECOMMENDATION] Obtain annotation guidelines or a written confirmation from
the dataset author covering inclusion/exclusion criteria and difficult cases.
Do not map the types to LKIF, SEM, Schema.org, or another ontology solely by
name similarity.

## 10. External source register

| Source | Concepts and evidence | Formal/role coverage | License/reuse | Status |
|---|---|---|---|---|
| Hohfeld 1913, *Yale Law Journal* 23(1), 16–59, DOI `10.2307/785533` | All eight positions; detailed first-order correlatives/opposites and terminology | Authoritative conceptual exposition and directed party semantics; explicitly declines formal definitions; no machine artifact | Historical text publicly accessible; original US work is public domain, but scan/platform terms vary | `AUTHORITATIVE` |
| Hohfeld 1917, *Yale Law Journal* 26(8), 710–770, DOI `10.2307/786270` | Continues complete framework; uses no-claim terminology | Further theory; second-order positions | Same caveat | `AUTHORITATIVE` |
| Martín-Chozas & Revenko 2021, CEUR-WS 2918, 30–38 | Exact project, four-label scope, manual-constraint claim, mappings to LegalRuleML/Provision Model | No complete definitions or role/range tables | CEUR paper accessible; associated code repository has no license | `AUTHORITATIVE` for task scope; `SUPPORTING_ONLY` for semantics |
| Francesconi 2016, *Semantic Web* 7(3), 255–265, DOI `10.3233/SW-140150` | Right/Duty and broader Hohfeld patterns | Explicit bearer/counterpart reversal, OWL-DL axioms, property domains | Article rights reserved; ontology license not found | `STRONG_SECONDARY` |
| Peters & Wyner 2016, LREC, 379–384, ACL ID `L16-1059` | Duty extraction and Hohfeld roles | DutyBearer, Counterpart, Action, Object | Paper openly accessible; no ontology license implicated | `STRONG_SECONDARY` |
| Sartor 2006, *Artificial Intelligence and Law* 14, 101–142, DOI `10.1007/s10506-006-9009-x` | Formal/teleological definitions of deontic and legal-right concepts | Formal theory broader than benchmark | Publisher copyright; cite, do not copy | `STRONG_SECONDARY` |
| Rubino, Rotolo & Sartor 2006, JURIX 2006, 101–110, ACM record `10.5555/1563577.1563589` | OWL ontology of basic legal concepts | Taxonomy and semantic relations; evolved into LKIF-Core | Original artifact not separately located; LKIF mirror now CC BY 4.0 | `STRONG_SECONDARY` |
| Herstein 2023, “Legal Rights,” Stanford Encyclopedia of Philosophy, §3 | Modern account of claim/duty and privilege/no-claim | Clear directed semantics and terminology caveats | Copyright SEP; citation/paraphrase only | `STRONG_SECONDARY` |
| Wenar & Cruft 2025 revision, “Rights,” Stanford Encyclopedia of Philosophy, §2.1 | Modern biconditional definitions of claim and privilege | Explicit directed-duty and action-polarity semantics | Copyright SEP; citation/paraphrase only | `STRONG_SECONDARY` |
| Van Engers & Nijssen 2014, EGOV, 133–146, DOI `10.1007/978-3-662-44426-9_11` | Eight kinds and semantic-conceptual integrity rules | Formal conceptual model, not target OWL package | Springer copyright | `SUPPORTING_ONLY` |
| Slootweg et al. 2016, AI4J workshop paper and OU thesis handle `1820/7185` | HohfeldSW extension with all four pairs | OWL/SWRL/SPARQL patterns, bearer/counterpart, disjointness | Artifact/license not verified | `STRONG_SECONDARY` paper; artifact unresolved |
| Griffo et al. 2015–2018, UFO-L project | Right-duty, permission/no-right, liberty and potestative legal relators | Ontologically grounded relational patterns | Papers accessible; no dedicated UFO-L machine artifact/license located | `STRONG_SECONDARY` concept; `SUPPORTING_ONLY` artifact |
| Gangemi and collaborators, Core Legal Ontology (CLO) | Eight Hohfeld position classes and directed position properties | OWL/DOLCE-based legal core ontology; thin position axiomatization | `CoreLegal.owl` accessible; no license found; stale/broken module imports | `STRONG_SECONDARY` artifact; `REFERENCE_ONLY` for reuse |
| Mustafa et al. 2026, ODRL Legal Profile | Eight UFO-L legal positions and simple legal relators grounded from ODRL | OWL/Turtle profile plus external first-order formalization and prover benchmark | Ontology CC BY 4.0; repository MIT; FOIS paper to appear | `STRONG_SECONDARY`; `ADAPT` as alignment source |
| OASIS LegalRuleML 1.0 | Obligation, Permission, Prohibition, Right, Bearer, AuxiliaryParty | Stable XML namespaces and RDFS metamodel; generic legal-rule semantics | OASIS RF on Limited Terms IPR mode | `SUPPORTING_ONLY` |
| LKIF-Core 1.1 | Norm, Right, Obligation, Permission, Liberty_Right, powers, legal roles | OWL/RDF/Turtle modules and stable project IRIs; not the exact Hohfeld square | Repository ontology files declare CC BY 4.0 | `SUPPORTING_ONLY` foundation |

## 11. C3 formalization audit

### 11.1 Candidate artifacts

| candidate | formal artifact available | semantic fit | namespace / formal content | licensing / maintenance | risks | decision |
|---|---:|---|---|---|---|---|
| CLO / NormativePositions | YES; `CoreLegal.owl` version 7.4 was retrievable | PARTIAL: all eight positions and bidirectional position properties | `http://www.loa-cnr.it/ontologies/CLO/NormativePositions.owl#`; `owl:inverseOf` target-direction properties, DOLCE/DUL grounding | No license statement; module and import IRIs fail to dereference; file unchanged since 2009 | Thin axioms; inverse target properties do not by themselves encode Right↔Duty correlativity or opposites; stale dependencies | `REFERENCE_ONLY` |
| Provision Model copy in `pmchozas/term_relex` | YES; OWL/RDF/XML pinned at commit `69136ce...`, file introduced at `06436f9...` | PARTIAL: Right, Duty, Permission, Prohibition; original model focuses Right/Duty and Power/Liability | Historical `http://www.ittig.cnr.it/ontologies/def/ProvisionModel#`; classes/properties, explicit/implicit views, domains | No repository or ontology license found; upstream artifact endpoint returned 502 and namespace endpoint 404 during audit | No native Privilege/NoRight; project mapping risks equating NoRight with Prohibition; stale namespace | `REFERENCE_ONLY` |
| ODRL Legal Profile (`odrl-l`) | YES; working-draft OWL/Turtle, source repository, and Zenodo software DOI | HIGH for position/relator structure; uses `Permission` rather than benchmark `Privilege` | `https://w3id.org/odrl-legal/`; eight position classes, bearer/content/relator properties, pairwise class disjointness | Ontology CC BY 4.0; repository MIT; first public release in 2026 | ODRL policy scope; FOIS paper still “to appear”; correlativity and incompatibility explicitly remain outside OWL in FOL; young project | `ADAPT` as alignment and axiom-design source, not direct import |
| HohfeldSW | NO directly accessible/versioned artifact found; paper and thesis accessible | HIGH conceptual fit: adds Privilege/NoRight and Immunity/Disability | Paper documents OWL classes/properties, equivalent classes/properties, disjointness, SWRL/SPARQL | License unknown; linked historical source page exposes no verified artifact | Reproducibility and reuse impossible until artifact/license recovered; case-study qualification rules may overfit HIPAA | `REFERENCE_ONLY` |
| LKIF-Core 1.1 `norm.owl`/Turtle mirror | YES; public GitHub mirror and modular OWL | MEDIUM: broad rights/powers taxonomy, no exact NoRight class or four-pair bearer reversal | `http://www.estrellaproject.org/lkif-core/norm.owl#`; class hierarchy and legal role/action modules | Ontology files declare CC BY 4.0; repository updated in 2026, while original version is 2008 | Broader theory; adapting names does not automatically yield Hohfeld correlatives | `ADAPT` only as optional foundation, not as target ontology |
| LegalRuleML 1.0 RDFS metamodel | YES; OASIS `os/rdfs/*.rdf` | MEDIUM-LOW: generic Obligation/Permission/Prohibition/Right, not exact Hohfeld pair system | Stable `http://docs.oasis-open.org/legalruleml/ns/mm/v1.0/`; RDFS modules, rule roles | OASIS standard, RF on Limited Terms IPR mode | No NoRight; Permission/Prohibition mapping is not exact; rule-language scope exceeds target | `REFERENCE_ONLY` |
| UFO-L | No dedicated reusable OWL/TTL target artifact located; gUFO foundation exists separately | HIGH conceptual fit; relational right-duty/no-right-permission patterns and all eight positions | Reference ontology/pattern diagrams; gUFO base has stable `http://purl.org/nemo/gufo#` but no UFO-L legal classes | UFO-L artifact license unresolved; gUFO is CC BY 4.0 | Conceptual-to-OWL translation would be new work; Alexy extensions may alter scope | `REFERENCE_ONLY` for semantics; possible foundation for NEW |
| Zomerdijk 2018 Hohfeld ODPs | Thesis says one OWL file per ODP, but portal exposes only thesis PDF in this audit | PARTIAL: temporal/legal-fact extensions rather than minimal four-label core | Claimed RDFS/OWL/SWRL patterns | No direct artifact, version, namespace, or license verified | Adds temporal/event commitments outside minimal target | `REFERENCE_ONLY` |
| Van Engers–Nijssen semantic-conceptual model | Paper accessible; no reusable target OWL artifact verified | HIGH conceptual Hohfeld coverage, broader temporal model | Conceptual integrity rules, not a frozen Semantic Web package | Publisher copyright; artifact/license absent | Different modeling paradigm and broader task | `REFERENCE_ONLY` |
| 2023 `spanish-laws.es` proposal | No ontology artifact; proposed resource URIs did not resolve during audit | PARTIAL and dataset-related | Proposes ActorType URIs and Provision Model mappings | No license/versioned package; endpoint returned 502 | Later derived work; mappings include NoRight→Prohibition | `REJECT` as reusable C3 artifact |
| ODRL 2.2 ontology | YES; W3C Recommendation and ontology | LOW: digital-policy Permission/Prohibition/Duty; no Hohfeld Right/NoRight pair | Stable `http://www.w3.org/ns/odrl/2/`; OWL/RDF | W3C document/software terms; maintained standard | Different domain and semantics; `Duty` can also mean condition/consequence/remedy | `REJECT` for target C3 |
| OntoLex-Lemon | YES as lexical-model vocabulary | NONE for jural relations | Lexicon/lexicalization model | W3C community specification | Can express terms for a separate ontology but supplies no legal semantics | `REFERENCE_ONLY` for future lexicalization |
| A-Hohfeld / LEGAL RELATIONS Language | Formal logic and controlled language described in publications; no reusable RDF/OWL target artifact found | HIGH for the eight-position logical framework | Quantified modal/deontic/action logic, not a Semantic Web ontology package | ACM/publisher copyright; no reusable artifact license found | Substantially extends and modernizes Hohfeld; translation to C3 would be new work | `REFERENCE_ONLY` |
| Nòmos framework | Formal requirements metamodel described in publications; no benchmark-ready OWL artifact verified | HIGH for eight Hohfeld positions, subjects, and normative propositions | Requirements-engineering notation and reasoning framework | Publication rights; artifact license not established in this audit | Software-requirements scope and complete eight-position inventory exceed the target | `REFERENCE_ONLY` |
| FIBO Legal Core | YES, maintained ontology suite | LOW: generic legal persons, capacities, rights and obligations; not the Hohfeld square | Stable FIBO namespaces and OWL modules | EDM Council specification terms; exact reuse review deferred | Finance/legal-domain breadth and no exact correlative pattern | `REFERENCE_ONLY` |
| Local LYNX terminology JSON-LD | YES | NONE for Hohfeld target | SKOS concepts/URIs; provenance matches the Lynx Labour Law Terminology deposited at Zenodo record `3843561` | Dataset deposit and authorship verified; exact license was not exposed by the retrieved record and remains unresolved | Unrelated terminology track; lexical false friends such as ordinary/financial senses of duty/right | `REJECT` |

[UNKNOWN] No uniquely identifiable, established artifact formally titled
“Rights and Obligations Ontology” was found that implements the four
Hohfeldian positions. Searches under that generic name resolve primarily to
LKIF-Core and broader legal/financial ontologies. A name-level match is
insufficient for C3 eligibility.

### 11.2 No SHACL result

[FACT] No candidate located in this audit provides a verified, reusable SHACL
package for the benchmark's four Hohfeld relations.

[INFERENCE] This is not a blocker to defining C3 conceptually, because SHACL is
optional in the frozen specification. It is a blocker to claiming that
machine-interpretable validation shapes already exist.

### 11.3 LegalRuleML and other standards

[FACT] LegalRuleML directly represents general deontic specifications and role
bearers, but explicitly remains independent of any one formal ontology or logic
framework and supports references to external ontologies by IRI.

[INFERENCE] LegalRuleML can be a serialization/rule foundation, not the source
of an exact Hohfeld target ontology. Its `Prohibition` must not be declared
equivalent to benchmark `NoRight`.

[FACT] LKIF-Core includes reusable legal concepts, legal persons/roles, rights,
permissions, obligations, powers, and immunities. It does not directly encode
the benchmark's complete four-position correlative pattern.

[INFERENCE] LKIF-Core may be imported or aligned selectively in a future C3,
but importing it wholesale would add unrelated classes and would not resolve
benchmark role orientation or type semantics.

[FACT] ODRL is a policy-expression ontology for actions over assets. OntoLex is
a lexicalization model. Neither directly formalizes the target Hohfeld square.

[EXTERNAL_SOURCE] The 2026 ODRL Legal Profile is distinct from core ODRL. It
does represent `Permission`, `NoRight`, `Duty`, `Right`, `Power`,
`Subjection`, `Immunity`, and `Disability` as legal positions and supplies
licensed, versioned machine artifacts. However, its OWL document explicitly
leaves full correlativity and incompatibility to first-order axioms, and its
semantics are grounded in activated ODRL policy rules. It is therefore a strong
alignment/design source, not an as-is target ontology for this benchmark.

## 12. C2 source decision table

| component | candidate source | source class | independent of test Gold? | authoritative enough? | compatible with benchmark semantics? | ready to freeze? | decision | reason |
|---|---|---|---:|---:|---:|---:|---|---|
| Duty definition | Hohfeld 1913 + Wenar/Cruft SEP + directed-role clarification from Francesconi 2016 | EXTERNAL_AUTHORITATIVE | YES | YES | YES, subject to dataset-role bridge | YES for source selection | `FREEZE_SOURCE` | Hohfeld supplies conceptual authority; modern sources supply formal wording and operational roles. |
| Right definition | Hohfeld 1913 + Wenar/Cruft SEP | EXTERNAL_AUTHORITATIVE | YES | YES | YES | YES for source selection | `FREEZE_SOURCE` | Benchmark spelling matches Hohfeld's strict right/claim; the biconditional comes from modern scholarship. |
| Privilege definition | Hohfeld 1913 + Wenar/Cruft SEP | EXTERNAL_AUTHORITATIVE | YES | YES | YES | YES for source selection | `FREEZE_SOURCE` | Privilege/liberty and opposite-content caveat are explicit; formal wording is secondary. |
| NoRight definition | Hohfeld 1913/1917 + SEP | EXTERNAL_AUTHORITATIVE | YES | YES | YES | YES for source selection | `FREEZE_SOURCE` | Must be no-claim, not Prohibition. |
| Abstract argument roles | Hohfeld 1913; Francesconi 2016; Peters & Wyner 2016 | EXTERNAL_AUTHORITATIVE | YES | YES | YES at theory level | PARTIAL | `FREEZE_BEARER_COUNTERPART_CONCEPTS_ONLY` | Bearer/counterpart/action semantics are defensible. |
| `e1`/`e2` mapping | 2023 TeresIA follow-up | DERIVED_LATER | YES of test inspection, but post-design | PARTIAL | UNRESOLVED | NO | `SEEK_AUTHOR_CONFIRMATION` | Only later evidence maps subject/object to Bearer/Counterpart; linguistic-role conflict remains. |
| Directionality | Hohfeld 1913; Francesconi 2016 | EXTERNAL_AUTHORITATIVE | YES | YES | PARTIAL | PARTIAL | `FREEZE_THEORY_NOT_DATASET_MAPPING` | Correlative swap is clear; label perspective in current annotations is not independently documented. |
| LegalAgent semantics | 2023 follow-up | DERIVED_LATER | YES | PARTIAL | CONFLICTED | NO | `SEEK_ORIGINAL_GUIDELINE` | Natural-person definition conflicts with earlier project typing and likely role-based usage. |
| LegalEntity semantics | 2021 and 2023 project sources | ORIGINAL_PROJECT / DERIVED_LATER | YES | PARTIAL | CONFLICTED | NO | `SEEK_ORIGINAL_GUIDELINE` | Scope changed between sources. |
| LegalConcept semantics | 2023 follow-up | DERIVED_LATER | YES | PARTIAL | UNRESOLVED | NO | `SEEK_ORIGINAL_GUIDELINE` | Residual definition is too weak for normative schema use. |
| Domain | 2021 paper claim; Hohfeld theory | ORIGINAL_PROJECT / EXTERNAL_AUTHORITATIVE | YES | Claim only | NO complete table | NO | `OMIT_FROM_C2_FOR_NOW` | Claimed manual restrictions were not published and external theory does not map to local types. |
| Range | Same | Same | YES | Claim only | NO complete table | NO | `OMIT_FROM_C2_FOR_NOW` | Same gap. |
| Relation signatures | Original metadata plus observed Gold pairs | ORIGINAL_DESIGN + OBSERVED_IN_GOLD | NO for the pair inventory | NO as closed world | UNRESOLVED | NO | `DO_NOT_FREEZE_AS_NORMATIVE` | Observed pairs remain test evidence. |
| Aliases/terminology | Hohfeld 1913/1917 + SEP | EXTERNAL_AUTHORITATIVE | YES | YES | YES with scope caveats | PARTIAL | `FREEZE_TERMINOLOGY_RELATIONSHIPS_LATER` | Right↔Claim, Privilege↔Liberty, NoRight↔NoClaim are defensible; no alias payload yet. |

## 13. C3 source decision table

| candidate | formal artifact available | semantic fit | reuse/adapt/new | licensing | risks | decision |
|---|---:|---|---|---|---|---|
| CLO / NormativePositions | YES | MEDIUM-HIGH vocabulary, thin axioms | ADAPT as alignment reference | UNKNOWN | Dead module/import IRIs, stale, no explicit opposites or class-level correlativity | `REFERENCE_ONLY` |
| Provision Model | YES via associated GitHub copy | PARTIAL | ADAPT conceptually | UNKNOWN | Missing exact Privilege/NoRight semantics, dead upstream namespace | `REFERENCE_ONLY` |
| ODRL Legal Profile | YES; OWL/Turtle plus formal benchmark | HIGH structural fit, ODRL-specific grounding | ADAPT selected patterns/alignment | CC BY 4.0 ontology; MIT repository | Young working draft; Permission naming; key correlativity axioms outside OWL | `ADAPT_ALIGNMENT_SOURCE` |
| HohfeldSW | NO verified artifact | HIGH | Would require recovery and audit | UNKNOWN | Reproducibility, license, HIPAA-specific validation | `REFERENCE_ONLY` |
| LKIF-Core | YES | MEDIUM | ADAPT as foundation | CC BY 4.0 in current files | Broad ontology; no exact pair axioms | `ADAPT_FOUNDATION_ONLY` |
| LegalRuleML | YES, RDFS standard modules | MEDIUM-LOW | ADAPT as rule/serialization foundation | OASIS RF on Limited Terms | Generic deontic model; no exact NoRight | `REFERENCE_ONLY` |
| UFO-L | NO target machine artifact verified | HIGH conceptual | NEW implementation informed by model | UNKNOWN for UFO-L; gUFO base CC BY 4.0 | Translation and Alexy extensions require explicit design | `REFERENCE_ONLY` |
| A-Hohfeld / Nòmos | NO benchmark-ready Semantic Web artifact verified | HIGH theoretical, broader task | NEW translation would be required | UNKNOWN for artifacts | Different logic/metamodel and all eight positions | `REFERENCE_ONLY` |
| ODRL | YES | LOW | REJECT | W3C terms | Wrong policy/asset semantics | `REJECT` |
| New benchmark-specific ontology | Not yet; explicitly out of scope here | POTENTIALLY HIGH | NEW | Can be explicitly licensed | Requires expert review, competency questions, versioned URIs, tests | `RECOMMENDED_PATH` |

## 14. Recommended candidate source set

### 14.1 C2

[RECOMMENDATION] Candidate source set:

1. Hohfeld (1913), pp. 30–33, as the primary conceptual and terminology source
   for Right/Claim, Duty, Privilege/Liberty, and NoRight/NoClaim.
2. Hohfeld (1917) for continuity of the complete framework and modern
   no-claim terminology.
3. Wenar and Cruft's SEP “Rights” entry for modern biconditional wording.
4. Martín-Chozas and Revenko (2021) solely to establish the benchmark's
   deliberate four-relation deontic scope.
5. Francesconi (2016) and Peters and Wyner (2016) to operationalize the
   independently defensible concepts Bearer, Counterpart, Action, and Object.
6. Herstein (2023 SEP) as a strong secondary terminology check, not as a
   replacement for Hohfeld.

[RECOMMENDATION] Do not include relation-specific type signatures, local entity
type definitions, BRAT grids, lexical triggers, examples, frequencies, or
NoRight→Prohibition equivalence in the C2 source freeze.

### 14.2 C3

[RECOMMENDATION] The most defensible path is `NEW`: later author a minimal,
versioned, benchmark-specific ontology of the four positions and their
bearer/counterpart/content structure. It should:

- use stable project-controlled URIs;
- keep the C1 inventory exactly unchanged;
- encode correlatives with role reversal and opposites with action-polarity
  care;
- distinguish NoRight/NoClaim from Prohibition;
- avoid hard domain/range over the unresolved local entity types;
- document every imported/aligned external term;
- add Power/Liability/Immunity/Disability only as out-of-target contextual
  concepts, if at all;
- define competency questions before OWL/SHACL design;
- receive legal-domain and dataset-author review.

[INFERENCE] ODRL-Legal now provides the strongest licensed machine-readable
alignment and relator-pattern source, while CLO provides useful historical
position-property vocabulary. LKIF-Core or gUFO may later provide a licensed
foundation, and LegalRuleML may provide rule serialization. None should
determine the benchmark semantics. Provision Model and HohfeldSW remain design
references until licensing and artifact recovery are resolved.

## 15. Audit-integrity and provenance corrections

[CONFLICT] `_legacy/docs/HOHFELD_SOURCE_RECONSTRUCTION_AUDIT.md` describes its
tag figures as opening-tag counts, but those figures are the sums of opening and
closing tags. The independently verified opening counts are `rel=95`, `e1=90`,
`e2=66`, `comp=99`, and `mod=1`; the prior figures are approximately double.
This error does not affect the 95-relation inventory or the conditioning
verdict, but the tag-count table must not be cited as written.

[CONFLICT] `_legacy/docs/TERESIA_PAPER3_AUDIT.md` refers to an
`estatuto_goldstandard/README.md` observed in an earlier dirty working copy.
No such file exists in the current local repository or its reachable history.
Because an untracked author README could contain design guidance, recovery from
a backup or direct author inquiry is a worthwhile provenance action.

[FACT] Public inspection of `oeg-upm/teresia-annotators` and
`oeg-upm/teresia-brat-server`, which are named in the prior audit but absent
locally, found downstream notebooks, BRAT copies, and generated signature
inventories. It found no original definitions or annotation guideline. These
repositories therefore do not close C2.

[FACT] `estatuto_goldstandard` has no license in any reachable local commit.
The associated `term_relex` repository also declares no license. Licensing of
the Gold source and Provision Model copy should be resolved with the source
author before redistribution or ontology reuse.

## 16. Remaining evidence requests

1. `[UNKNOWN]` Original annotation guideline defining `e1`, `e2`, `comp`,
   `mod`, `MissingE1`, and `MissingE2`.
2. `[UNKNOWN]` Dataset-author confirmation that the labeled relation is always
   asserted from `e1`'s perspective and that `e2` is the correlative party.
3. `[UNKNOWN]` Authoritative definitions and inclusion criteria for
   `LegalAgent`, `LegalEntity`, and `LegalConcept`.
4. `[UNKNOWN]` The unpublished manual domain/range tables claimed in the 2021
   paper, and whether they apply to the 2024–2025 annotation revision.
5. `[UNKNOWN]` License and canonical version for the Provision Model OWL file.
6. `[UNKNOWN]` Recoverable, versioned, licensed HohfeldSW or Zomerdijk ODP
   artifacts.
7. `[UNKNOWN]` Legal review of the exact C2 paraphrases before normative freeze.

## 17. Final readiness

| Area | Verdict |
|---|---|
| Local authoritative definitions | `NONE` |
| External authoritative definitions | `AVAILABLE`: conceptual authority from Hohfeld 1913/1917; formal wording from modern scholarship |
| Four-relation semantic alignment | `SUPPORTED` as the first-order/deontic family |
| Eight-position expansion | `PROHIBITED TASK CHANGE` unless separately designed |
| Abstract argument semantics | `READY_TO_DRAFT` |
| `e1`/`e2` semantics | `PARTIAL` |
| Directionality | `PARTIAL` because dataset mapping is unresolved |
| Entity-type semantics | `NOT_READY` |
| C2 definitions | `READY_FOR_SOURCE_FREEZE`, pending legal review of wording |
| C2 domain/range and signatures | `NOT_READY`; omit rather than infer |
| Existing reusable C3 package | `NONE SUITABLE AS-IS` |
| Best licensed C3 alignment source | `ODRL-Legal`, subject to its working-draft and ODRL-scope caveats |
| C3 path | `NEW`, informed by cited formal models |

**C2_SOURCE_FREEZE_READY = PARTIAL**

**C3_FORMALIZATION_PATH = NEW**

## 18. Bibliography and verification register

1. Hohfeld, W. N. (1913). “Some Fundamental Legal Conceptions as Applied in
   Judicial Reasoning.” *Yale Law Journal*, 23(1), 16–59.
   <https://doi.org/10.2307/785533>;
   <http://hdl.handle.net/20.500.13051/11079>.
2. Hohfeld, W. N. (1917). “Fundamental Legal Conceptions as Applied in Judicial
   Reasoning.” *Yale Law Journal*, 26(8), 710–770.
   <https://doi.org/10.2307/786270>.
3. Martín-Chozas, P., & Revenko, A. (2021). “Thesaurus Enhanced Extraction of
   Hohfeld's Relations from Spanish Labour Law.” DeepOntoNLP 2021,
   *CEUR-WS* 2918, 30–38. <https://ceur-ws.org/Vol-2918/paper4.pdf>.
4. Francesconi, E. (2016). “Semantic Model for Legal Resources: Annotation and
   Reasoning over Normative Provisions.” *Semantic Web*, 7(3), 255–265.
   <https://doi.org/10.3233/SW-140150>.
5. Peters, W., & Wyner, A. (2016). “Legal Text Interpretation: Identifying
   Hohfeldian Relations from Text.” *LREC 2016*, 379–384.
   <https://aclanthology.org/L16-1059/>.
6. Sartor, G. (2006). “Fundamental Legal Concepts: A Formal and Teleological
   Characterisation.” *Artificial Intelligence and Law*, 14(1–2), 101–142.
   <https://doi.org/10.1007/s10506-006-9009-x>.
7. Rubino, R., Rotolo, A., & Sartor, G. (2006). “An OWL Ontology of
   Fundamental Legal Concepts.” *JURIX 2006*, 101–110.
   <https://dl.acm.org/doi/10.5555/1563577.1563589>.
8. Hoekstra, R., Breuker, J., Di Bello, M., & Boer, A. (2009). “LKIF Core:
   Principled Ontology Development for the Legal Domain.” In *Law, Ontologies
   and the Semantic Web*, 21–52. Artifact:
   <https://github.com/RinkeHoekstra/lkif-core>.
9. Slootweg, P., Rutledge, L., Wedemeijer, L., & Joosten, S. (2016). “The
   Implementation of Hohfeldian Legal Concepts with Semantic Web
   Technologies.” <https://www.ai.rug.nl/~verheij/AI4J/papers/AI4J_paper_21_slootweg.pdf>;
   thesis <http://hdl.handle.net/1820/7185>.
10. Van Engers, T. M., & Nijssen, S. (2014). “Connecting People:
    Semantic-Conceptual Modeling for Laws and Regulations.” *EGOV 2014*,
    133–146. <https://doi.org/10.1007/978-3-662-44426-9_11>.
11. Griffo, C., Almeida, J. P. A., Guizzardi, G., & colleagues (2015–2018).
    UFO-L project and legal-relation patterns.
    <https://nemo.inf.ufes.br/en/projetos/ufo-l/>.
12. Herstein, O. (2023). “Legal Rights.” *Stanford Encyclopedia of
    Philosophy*, §3. <https://plato.stanford.edu/entries/legal-rights/>.
13. Wenar, L., & Cruft, R. (2025 revision). “Rights.” *Stanford Encyclopedia
    of Philosophy*, §2.1. <https://plato.stanford.edu/entries/rights/>.
14. OASIS (2021). *LegalRuleML Core Specification Version 1.0*.
    <https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/legalruleml-core-spec-v1.0.html>;
    RDFS artifacts
    <https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/rdfs/>.
15. W3C (2018). *ODRL Information Model 2.2* and *ODRL Vocabulary &
    Expression 2.2*. <https://www.w3.org/TR/odrl-model/>;
    <https://www.w3.org/TR/odrl-vocab/>.
16. Argüelles Terrón, G., Martín-Chozas, P., & Rodríguez-Doncel, V. (2023).
    “Event Extraction and Semantic Representation from Spanish Workers'
    Statute Using Large Language Models.” *JURIX 2023*, FAIAP 379, 329–334.
    <https://doi.org/10.3233/FAIA230983>; extended thesis
    <https://oa.upm.es/75904/>.
17. Zomerdijk, A. (2018). *Semantic Web Ontology Design Patterns for the
    Hohfeld Semantic-Conceptual Model*. Open Universiteit master's thesis.
    <https://research.ou.nl/en/studentTheses/semantic-web-ontology-design-patterns-for-the-hohfeld-semantic-co/>.
18. Allen, L. E., & Saxon, C. S. (1995). “Better Language, Better Thought,
    Better Communication: The A-Hohfeld Language for Legal Analysis.”
    *ICAIL 1995*, 219–228. <https://doi.org/10.1145/222092.222245>.
19. Allen, L. E., & Saxon, C. S. (1997). “Achieving Fluency in Modernized and
    Formalized Hohfeld.” *ICAIL 1997*, 19–28.
    <https://doi.org/10.1145/261618.261623>.
20. Siena, A., Mylopoulos, J., Perini, A., & Susi, A. (2009–2010). Nòmos
    framework publications; formal account:
    <https://doi.org/10.48550/arXiv.1002.3711>.
21. Gangemi, A., Sagri, M.-T., & Tiscornia, D. (2005). “A Constructive
    Framework for Legal Ontologies.” CLO artifact:
    <http://www.loa-cnr.it/ontologies/CLO/CoreLegal.owl>.
22. Mustafa, D. M., Lange, C., Guizzardi, G., Collarana, D., Quix, C., &
    Decker, S. (2026). “What Does ODRL Mean? A Cross-Level Ontological
    Grounding of Permissions, Prohibitions, and Duties in UFO-L.” FOIS 2026,
    to appear. <https://arxiv.org/abs/2606.24344>; artifact
    <https://w3id.org/odrl-legal/>; software
    <https://doi.org/10.5281/zenodo.21137744>.
23. Martín-Chozas, P., Montiel-Ponsoda, E., Vázquez, K., &
    Rodríguez-Doncel, V. (2020). *Labour Law Terminology*. Zenodo.
    <https://doi.org/10.5281/zenodo.3843561>.
