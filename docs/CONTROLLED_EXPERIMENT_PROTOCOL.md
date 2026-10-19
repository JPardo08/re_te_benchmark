# Controlled experiment protocol

This document is the pre-pilot scoring and coverage protocol for the controlled
C0–C3 comparison. It does not change `re_te_evaluation`, the Gold, the
conditioning payloads, or the runner. Where the current runner cannot yet
represent a distinction required here, the distinction is a campaign rule
applied before evaluation. It is not a silent change to the evaluator.

The current instruction renderer is `common-instruction-shell-v2`.
`common-instruction-shell-v1` remains recorded and is not the text sent to a
model. C2 readiness stays `PARTIAL`. C3 readiness stays `NOT_READY` and
`NOT_EXECUTABLE`. This protocol does not make either condition ready.

## A. Cohort and metrics

### Cohort

The evaluation universe is the 36 canonical Hohfeld documents in
`datasets/teresia_hohfeld/canonical/documents.jsonl`, benchmark
`teresia_hohfeld` version `0.1.0`. Every condition sees that same list. A
condition does not drop a document to raise its F1.

The canonical annotation file contains 95 annotations. Eligibility is read
from the benchmark fields. It is not recomputed.

| Policy name in the evaluator | Benchmark field | Eligible annotations | Materialized triplet occurrences |
|---|---|---|---|
| `strict_inline` | `eligibility.complete_triplet_strict_inline` | 60 | 61 |
| `relation_type` | `eligibility.relation_type` | 95 | not a triplet support |
| `canonical_argument` | `eligibility.complete_triplet_with_missing_e2` | 85 | not a primary Gold support |

The 60 and the 61 are different counts. `strict_inline` marks 60 annotations
eligible. The evaluator then materializes one occurrence per object, so
`articulo_47#3`, which stores two inline objects, contributes two occurrences.
The resulting 61 occurrences are the Gold support of `strict_inline` when the
whole eligible set is scored. In the evaluator those two counts are
`counts.gold_eligible` and `counts.gold_eligible_occurrences`. The 61 are not
the denominator of F1.

Shell v2 tells the model to write one line per object and to repeat the
subject and the relation. That sentence is shared by C0, C1, C2, C3, and
C3-NL. It is not a Gold example and it does not name a label.

Strict Gold is present in 29 of the 36 documents. The seven documents without
a strict-inline annotation stay in the universe:

- `articulo_6`
- `articulo_9`
- `articulo_17`
- `articulo_28`
- `articulo_34`
- `articulo_50`
- `articulo_65`

Under `strict_inline` they contribute no false negatives. Any prediction in
them remains a false positive.

### Primary metric

The primary estimand is exact complete-triplet F1:

- metric family `triplet`;
- context mode `document`;
- eligibility policy `strict_inline`;
- matching `exact_multiset_v1`;
- normalization `unicode_nfc+outer_strip+lowercase_false`.

Matching is string equality after that normalizer. It does not use offsets.
Several literal occurrences of the same argument string in one article do not
change this score. They also do not identify which mention was copied.

A prediction that does not match an eligible Gold occurrence stays in the
prediction multiset and can be a false positive. Excluded Gold is not a false
negative. Predictions are not filtered with Gold.

Precision, recall, and F1 are the evaluator's zero-safe ratios. They are not
ratios over a fixed count of 61:

```text
precision = tp / (tp + fp), or 0 when tp + fp = 0
recall    = tp / (tp + fn), or 0 when tp + fn = 0
f1        = 2 * precision * recall / (precision + recall),
            or 0 when precision + recall = 0
```

`tp + fn` equals the Gold support of the occurrences actually submitted to
that run. For a run over the full `strict_inline` set, that support is 61
materialized occurrences from 60 annotations. `tp + fp` is the prediction
support and depends on what the model emitted. F1 has no denominator of its
own. A subset estimand states its own Gold support. It does not inherit 61.

### Secondary and non-comparable policies

`relation_type` is secondary predicate awareness. It ignores subject and
object. It is not a complete-triplet result. Shell v2 still withholds a line
when either argument is absent, so the 10 partial annotations cannot be
emitted by a model that follows the shell. Recall on all 95 labels is
therefore not pure predicate detection. Report that ceiling beside any
secondary number. A completed triple with the same label can match a partial
Gold label because the metric ignores arguments.

`canonical_argument` is not directly comparable under shell v2. The additional
25 annotations use a non-inline `MissingE2` object. The shell forbids
inventing an absent argument and forbids a line when an argument is absent.
Do not read a `canonical_argument` F1 as the effect of conditioning.

## B. Failures and coverage

Each document-condition attempt has exactly one principal execution state.
The ten categories are not ten exclusive labels. A signal that loses the
precedence contest is kept as `also_observed`. It is not deleted.

### The ten categories

1. Not attempted. Principal state. The frozen cohort included the document,
   but this campaign did not submit it. It is a coverage hole. It is not a
   model prediction of no relation. No generation diagnostic is inferred.
2. External infrastructure error. Principal state. After submission, the
   process, filesystem, scheduler, or machine failed before a model output
   existed. This failure is transient. It is not evidence about the
   condition.
3. Model execution error. Principal state. The extractor raised after the
   call started, and the failure is neither the configured timeout nor an
   external outage.
4. Timeout. Principal state. The configured time limit stopped the run
   before a completed generation. A timeout is not reclassified as a model
   execution error. This failure is transient.
5. Context blocked. Principal state. Preflight measured the rendered prompt
   against the model context budget and the reserved output budget, and the
   prompt does not fit. This check is deterministic: the same shell, slot,
   document, tokenizer, and budgets give the same result. Generation is not
   started. The conditioning slot is not shortened, and the prompt is not
   truncated, to make it fit. This can depend on conditioning length. It is
   an operational result of that condition, not a transient infrastructure
   failure and not randomly missing data.
6. Output truncated. Diagnostic attribute. The principal state is completed
   and the generation metadata reports that the output budget was reached.
   Valid lines are scored. The incomplete tail is not repaired. Truncation
   may co-occur with malformed lines and with an empty generation.
7. Completed empty generation. Diagnostic attribute. The principal state is
   completed and the output has no content lines. Under shell v2 this is a
   valid abstention. Absence of lines is not the same as a line that failed
   the parser.
8. Fully malformed output. Diagnostic summary. The principal state is
   completed, there is at least one content line, and every content line is
   rejected by the TSV parser. No triple is invented. The rejected lines are
   retained. This summary may co-occur with truncation.
9. Partially malformed output. Diagnostic summary. The principal state is
   completed, at least one valid line is scored, and at least one line is a
   parse issue. The raw output and every issue remain attached to the
   document. This summary may co-occur with truncation.
10. Evaluation contract abort. Export attribute. The exported file violates
    the evaluator contract, including an empty field after normalization.
    This attribute does not overwrite the principal state or the generation
    diagnostics. The score is not interpretable. Do not publish an F1 for
    that export.

The principal states are categories 1, 2, 3, 4, and 5, plus `completed`.
`completed` means generation returned output, including an empty string. It
is the state under which categories 6, 7, 8, and 9 are recorded. Categories
8 and 9 are summaries of two counts, valid lines and malformed lines. They
are not a second principal state. For an attempt that is not completed,
generation diagnostics are not applicable. They are not stored as false.

### Precedence

Exactly one principal state is assigned. The first match wins:

1. Category 1, not attempted, if the campaign did not submit the document.
2. Category 5, context blocked, if preflight says the prompt does not fit.
   Generation is not started, so this attempt cannot also time out or raise
   a model error.
3. Category 2, external infrastructure error, if the environment failed
   before a model output existed.
4. Category 4, timeout, if the configured time limit stopped the run.
5. Category 3, model execution error, if the extractor raised for another
   reason.
6. `completed`, if generation returned output.

Categories 6, 7, 8, and 9 do not enter this contest. They are attached to
`completed` and may all be present on the same attempt. Category 10 does not
enter it either. If the log supports two principal candidates, the one that
loses this order is stored in `also_observed` with its evidence.

### Retries

The retry rule is the same for every condition and every document.

- The transient failures authorized for retry are external infrastructure
  error and timeout. Each may be retried once, with the same shell, payload,
  checkpoint, tokenizer, decoding parameters, seed, and budgets.
- A context block is not retried. The identical configuration would not fit
  on the second attempt either. Do not truncate the conditioning slot, the
  instruction, or a selected part of the prompt in order to retry.
- The failed attempt is kept in the campaign log. A retry does not delete it.
- If the retry succeeds, the successful attempt is the one scored, and the
  log still shows the earlier failure and its diagnostics.
- If the retry fails, the last principal state stands and the earlier
  principal state remains visible as `also_observed`.
- A model execution error, a truncated generation, an empty generation, and
  malformed output are not retried. They are operational results.
- An evaluation contract abort is an export defect. Fix the export and rerun
  evaluation on the same predictions. Do not regenerate the model output to
  hide it.
- Do not retry a document in only one condition.

### Incomplete campaigns

If an external failure prevents a condition from being executed across the
cohort, that condition's campaign is `INCOMPLETE`. Repeat the unfinished
document-condition pairs when the external cause is gone. Do not drop those
documents from that condition, and do not publish the finished subset as the
cohort result.

A model error, a timeout, a context block, an empty generation, or a
malformed generation stays in the operational record. It is not recoded as
random missingness and it is not removed to improve F1. A context block is
not an external outage and does not by itself make the campaign
`INCOMPLETE`.

## C. Reports and estimands

Publish these separately. Do not substitute one for another.

### Coverage

For each condition, over the 36 documents:

- attempted;
- not attempted;
- counts of the principal states, which partition the 36 documents;
- diagnostic counts, which may overlap: output truncated, empty generation,
  fully malformed, partially malformed, and `also_observed`;
- parsed triples;
- invalid lines;
- triples that entered the evaluator;
- whether the export carries an evaluation contract abort.

The operational success count is the number of documents whose principal
state is completed. Truncation, an empty generation, and malformed lines
remain visible inside that count. An empty generation is a completed
generation and an empty prediction. A generation whose every content line is
malformed is a completed generation and a parse failure.

### Conservative operational F1

Universe: the 36 documents, and only when every document was attempted and no
external infrastructure failure remains. The Gold support of that universe
under `strict_inline` is the 61 materialized occurrences from the 60 eligible
annotations. That support is not the denominator of F1.

Score the predictions that were actually produced. A principal state that
produced no scored triples leaves the materialized occurrences of that
document as false negatives. The principal state and the diagnostic
attributes are reported beside the score. This applies to a model execution
error, to a timeout that persists after the one allowed retry, to a context
block, to a completed empty generation, and to a completed generation whose
every content line is malformed. Valid lines from a truncated or partially
malformed generation are scored; they are not discarded because another
diagnostic is present. An external infrastructure error does not enter this
estimand: the campaign stays `INCOMPLETE` until it is resolved. A document
not attempted does not enter it either. An evaluation contract abort blocks
publication.

In that complete universe, `tp + fn` equals 61. `tp + fp` is the number of
scored prediction occurrences. Precision, recall, and F1 then follow the
formulas in section A. F1 is not `tp / 61` and it is not a ratio whose
denominator is the Gold support.

This estimand is the end-to-end number only when every document was attempted
and no external failure remains. It still mixes scientific errors with
operational failures of the model run. The principal-state table and the
diagnostic table have to be read with it.

### F1 conditional on completed generation

Scored documents: those whose principal state is completed for that
condition, including documents flagged as truncated, empty, or malformed.
State the document count and the Gold support of that subset, meaning the
materialized `strict_inline` occurrences in those documents. That support is
not automatically 61, and it is not the F1 denominator. Precision, recall,
and F1 still use `tp`, `fp`, and `fn` from the submitted occurrences.
Excluded principal states are not attempted, external infrastructure error,
model execution error, timeout, and context blocked. An evaluation contract
abort blocks the report.

This is not the cohort result. Conditions with longer prompts can lose more
documents to a context block. The conditional score then describes an easier
or smaller subset. Say that when the number is reported.

### Paired secondary analysis

Scored documents: those whose principal state is completed in every condition
included in the comparison. A document in any other principal state in any
compared condition leaves the paired set.

This estimates a common-support contrast. It can favor the condition that
fails on the documents the others also fail, and it can hide a context-length
penalty that affects only one condition. It is not the end-to-end result for
the 36 documents. Report the intersection size, the Gold support inside that
intersection, the principal state that removed each excluded document, and
the diagnostic attributes of the documents that remain. The F1 on this
intersection uses the same precision, recall, and F1 formulas. Its Gold
support is not presumed to be 61.

## D. Compatibility with the current runner

Observed in the current `re_te_system` runner and export. The EXP.2 parser
rejects a whitespace-only field instead of exporting it as a triple:

- The evaluator reports `counts.gold_eligible` as the number of distinct
  eligible annotations and `counts.gold_eligible_occurrences` as the number
  of materialized occurrences. For this cohort those values are 60 and 61
  under `strict_inline`. Micro precision, recall, and F1 are computed from
  `tp`, `fp`, and `fn` with the zero-safe formulas in section A. The
  evaluator has no fixed F1 denominator of 61.
- `export_evaluation` writes subject, relation, and object. It does not write
  the principal state, diagnostic attributes, or parse issues.
- A finished empty output and a fully malformed output both export zero rows.
  The evaluator then sees no predictions. The campaign log has to preserve
  the empty-generation and malformed-line attributes, or those two outcomes
  collapse.
- An extractor exception still produces a prediction record. Without a
  separate principal state, an empty record looks like a completed empty
  generation.
- Output truncation is already a soft issue when `output_reached_limit` is
  true. The runner appends that issue without removing parse issues, so
  truncation and malformed lines can already coexist on one document. The
  runner does not repair the tail. The export drops both.
- The runner does not block an over-long prompt at preflight. The current Pythia, GoLLIE, UIE, REBEL, mREBEL, and GENIE extractors
  truncate the encoded input and record `truncated_input`. That is not the `context_blocked`
  state of this protocol: it selectively discards part of the rendered
  prompt, which can include conditioning, and then continues. A campaign
  that followed that behavior would violate the preflight rule. The runner
  also has no timeout stage. Timeout, context block, and infrastructure
  failure must be recorded by the campaign harness. They are not inferred
  from the TSV parser.
- A windowing exception omits the document from `predictions.jsonl`. The
  export then cannot distinguish it from a document that was not attempted.
  The campaign log has to keep that failure.
- The whitespace-only TSV rejection from EXP.2 prevents a blank field from
  reaching the evaluator as an empty string. An evaluation contract abort
  remains the outcome if some other export violates the contract. That abort
  stops the evaluation; it is not an F1 of zero.

No runner change is authorized by this document.

## E. Experimental identity freeze

Do not start inference until one manifest records all of the following for
every condition in the campaign.

- Git SHA of `re_te_benchmark`, `re_te_system`, and `re_te_evaluation`. A
  dirty tree is not an identity. Record content hashes if the tree is dirty,
  and do not call that SHA sufficient.
- Shell version `common-instruction-shell-v2` and the SHA-256 of
  `shell_template()`. Also record the SHA-256 of each conditioning slot
  actually inserted: C0 empty, C1 labels, C2 payload, C3 payload, C3-NL
  payload.
- Model checkpoint identifier and resolved revision.
- Tokenizer identifier and resolved revision.
- Decoding parameters that can change the output, including `do_sample`,
  beam count, temperature, top-p, and any other sampler setting in use.
- Seed, and whether `do_sample` is false. A seed does not create determinism
  when sampling is enabled.
- Prompt length in tokens for each document, the tokenizer used to measure
  it, and the context budget against which preflight compares that length.
  A prompt that does not fit is blocked. It is not solved by shortening the
  conditioning slot.
- Output budget, including `max_new_tokens`.
- Output-truncation policy: stop at the budget, keep valid lines, do not
  complete a partial line. This is independent of the preflight context
  block.
- Prediction contract version from `re_te_system`.
- Eligibility policy `strict_inline`, matching `exact_multiset_v1`, context
  `document`, and the default normalization policy above.
- The 36 document identifiers and the SHA-256 of
  `datasets/teresia_hohfeld/canonical/documents.jsonl` and
  `datasets/teresia_hohfeld/canonical/annotations.jsonl`.

C2 and C3 may appear in that freeze only as recorded, non-executable
payloads until their readiness changes by a separate decision.
