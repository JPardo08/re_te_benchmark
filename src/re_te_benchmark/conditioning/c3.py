"""Load and structurally validate the provisional C3 TBox.

The checked-in Turtle file is an ontology artifact. It is not an extractor
payload. This module parses a restricted Turtle subset and checks the axiom
profile. It does not run an OWL reasoner. The experimental projection is built
later from axioms that profile accepts, and absence of an axiom is not projected
as its negation.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from re_te_benchmark.conditioning.c2 import (
    canonical_dumps,
    content_sha256,
    load_c1_labels,
    load_c2_package,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = REPO_ROOT / "schemas" / "c3" / "c3_ontology_v1.json"
ONTOLOGY_PATH = REPO_ROOT / "schemas" / "c3" / "c3_ontology_v1.ttl"
C1_PATH = REPO_ROOT / "schemas" / "c1" / "hohfeld_labels.json"

PACKAGE_ID = "C3_ONTOLOGY_V1"
PACKAGE_VERSION = "1.0.0"
ONTOLOGY_IRI = "urn:example:re-te-benchmark:c3:first-order-position:v1"
VOCABULARY_IRI = ONTOLOGY_IRI + "#"
C2_CONTENT_SHA256 = (
    "037ab7bcf9691310f5a56a1bb7c635f6c230bdc270d37d5cc9578c88afb76d24"
)
C2_PAYLOAD_SHA256 = (
    "314a220d1916c260ff6f94c731225c43a39fa8136719794586298d47fdbe57fc"
)
ONTOLOGY_SHA256 = (
    "5dfac3fae2f74aa9aa1f22efb2d41531b10eba43117f67fdfd8601cd4209d397"
)
PACKAGE_CONTENT_SHA256 = (
    "fbccf154a4b822476e73ecca10c306536ab70c08383e5d4a972ead8e9e4776e7"
)
POSITIONS = ("Duty", "Right", "Privilege", "NoRight")
CORRELATIVE_RANGE = {
    "Duty": "Right",
    "Right": "Duty",
    "Privilege": "NoRight",
    "NoRight": "Privilege",
}
OPPOSITE_RANGE = {
    "Duty": "Privilege",
    "Right": "NoRight",
    "Privilege": "Duty",
    "NoRight": "Right",
}
CATEGORY_CLASSES = (
    "FirstOrderPosition",
    "Party",
    "Act",
    "Polarity",
    "NormativeContent",
    "NormativeStatement",
)
FORBIDDEN_CLASS_NAMES = (
    "Power",
    "Liability",
    "Immunity",
    "Disability",
    "LegalAgent",
    "LegalEntity",
    "LegalConcept",
    "Prohibition",
    "Permission",
    "Obligation",
)
_SIGNATURE_RE = re.compile(
    r"Legal(?:Agent|Entity|Concept)-Legal(?:Agent|Entity|Concept)"
)
_FORBIDDEN_TEXT = (
    "owl:imports",
    "owl:equivalentProperty",
    "owl:complementOf",
    "owl:someValuesFrom",
    "owl:qualifiedCardinality",
    "owl:minCardinality",
    "owl:maxCardinality",
    "owl:cardinality",
    "owl:hasValue",
    "swrl:",
    "sh:NodeShape",
    "LegalAgent",
    "LegalEntity",
    "LegalConcept",
    "subvenciones",
    "desgravaciones",
    "Estatuto",
    "subject = bearer",
    "object = counterpart",
    "e1 = bearer",
    "e2 = counterpart",
)

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL = "http://www.w3.org/2002/07/owl#"
ALLOWED_IRI_PREFIXES = (
    VOCABULARY_IRI,
    ONTOLOGY_IRI,
    RDF,
    RDFS,
    OWL,
)


class C3OntologyError(ValueError):
    """The C3 TBox or its package record is not valid."""


@dataclass(frozen=True)
class Term:
    """One RDF term produced by the restricted Turtle parser."""

    kind: str
    value: str
    lang: str | None = None
    datatype: str | None = None

    def __str__(self) -> str:
        if self.kind == "literal":
            return json.dumps(self.value, ensure_ascii=False)
        return self.value


def iri(value: str) -> Term:
    """Build an IRI term."""
    return Term("iri", value)


def h(local: str) -> Term:
    """Build a term in the provisional vocabulary."""
    return iri(VOCABULARY_IRI + local)


RDF_TYPE = iri(RDF + "type")
RDF_FIRST = iri(RDF + "first")
RDF_REST = iri(RDF + "rest")
RDF_NIL = iri(RDF + "nil")


class Graph:
    """A triple list from one restricted Turtle document."""

    def __init__(self, prefixes: dict[str, str], triples: list[tuple[Term, Term, Term]]):
        self.prefixes = prefixes
        self.triples = triples

    def objects(self, subject: Term, predicate: Term) -> list[Term]:
        """Return objects of subject/predicate in document order."""
        return [
            obj
            for subj, pred, obj in self.triples
            if subj == subject and pred == predicate
        ]

    def one(self, subject: Term, predicate: Term) -> Term:
        """Return the single object or raise."""
        found = self.objects(subject, predicate)
        if len(found) != 1:
            raise C3OntologyError(
                f"Expected one value of {predicate} on {subject}, found {len(found)}."
            )
        return found[0]

    def subjects_of_type(self, type_term: Term) -> list[Term]:
        """Return subjects explicitly typed with type_term."""
        return [subj for subj, pred, obj in self.triples if pred == RDF_TYPE and obj == type_term]

    def collection(self, node: Term) -> list[Term]:
        """Expand an rdf:List into its item terms."""
        items: list[Term] = []
        seen: set[Term] = set()
        current = node
        while current != RDF_NIL:
            if current in seen:
                raise C3OntologyError("RDF list is cyclic.")
            seen.add(current)
            items.append(self.one(current, RDF_FIRST))
            current = self.one(current, RDF_REST)
        return items


class _Parser:
    """Recursive-descent parser for the Turtle subset used by this package."""

    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.index = 0
        self.line = 1
        self.prefixes: dict[str, str] = {}
        self.triples: list[tuple[Term, Term, Term]] = []
        self.blank_count = 0

    def parse(self) -> Graph:
        while True:
            self._skip()
            if self._eof():
                break
            if self._consume_word("@prefix"):
                self._prefix_directive()
            elif self._starts_with("@base"):
                self._fail("@base is outside the supported Turtle subset.")
            else:
                subject = self._read_subject()
                self._predicate_object_list(subject)
                self._expect(".")
        return Graph(self.prefixes, self.triples)

    def _eof(self) -> bool:
        return self.index >= self.length

    def _peek(self) -> str:
        if self._eof():
            self._fail("Unexpected end of Turtle input.")
        return self.text[self.index]

    def _advance(self) -> str:
        char = self._peek()
        self.index += 1
        if char == "\n":
            self.line += 1
        return char

    def _starts_with(self, token: str) -> bool:
        return self.text.startswith(token, self.index)

    def _consume_word(self, word: str) -> bool:
        if not self._starts_with(word):
            return False
        after = self.index + len(word)
        if after < self.length and (self.text[after].isalnum() or self.text[after] in "_-"):
            return False
        self.index = after
        return True

    def _skip(self) -> None:
        while not self._eof():
            char = self.text[self.index]
            if char in " \t\r\n":
                self._advance()
                continue
            if char == "#":
                while not self._eof() and self.text[self.index] != "\n":
                    self._advance()
                continue
            break

    def _expect(self, token: str) -> None:
        self._skip()
        if not self._starts_with(token):
            self._fail(f"Expected {token!r}.")
        self.index += len(token)
        if token == "\n":
            self.line += 1

    def _fail(self, message: str) -> None:
        raise C3OntologyError(f"Turtle line {self.line}: {message}")

    def _prefix_directive(self) -> None:
        self._skip()
        name = self._read_prefix_name()
        self._expect(":")
        self._skip()
        value = self._read_iriref()
        self._expect(".")
        self.prefixes[name] = value

    def _read_prefix_name(self) -> str:
        start = self.index
        if self._eof() or not self.text[self.index].isalpha():
            self._fail("Expected a prefix name.")
        self._advance()
        while not self._eof() and (self.text[self.index].isalnum() or self.text[self.index] == "-"):
            self._advance()
        return self.text[start:self.index]

    def _read_iriref(self) -> str:
        if self._peek() != "<":
            self._fail("Expected an IRI in angle brackets.")
        self._advance()
        start = self.index
        while not self._eof() and self.text[self.index] != ">":
            if self.text[self.index] in " \n\r":
                self._fail("IRI contains whitespace.")
            self._advance()
        value = self.text[start:self.index]
        self._expect(">")
        return value

    def _read_prefixed_iri(self) -> Term:
        prefix = self._read_prefix_name()
        self._expect(":")
        if prefix not in self.prefixes:
            self._fail(f"Undeclared prefix {prefix!r}.")
        start = self.index
        if self._eof() or not (self.text[self.index].isalnum() or self.text[self.index] == "_"):
            self._fail("Expected a prefixed local name.")
        self._advance()
        while not self._eof() and (
            self.text[self.index].isalnum() or self.text[self.index] in "_-"
        ):
            self._advance()
        return iri(self.prefixes[prefix] + self.text[start:self.index])

    def _read_iri(self) -> Term:
        self._skip()
        if self._peek() == "<":
            return iri(self._read_iriref())
        return self._read_prefixed_iri()

    def _fresh_blank(self) -> Term:
        self.blank_count += 1
        return Term("blank", f"b{self.blank_count}")

    def _emit(self, subject: Term, predicate: Term, obj: Term) -> None:
        self.triples.append((subject, predicate, obj))

    def _read_subject(self) -> Term:
        self._skip()
        char = self._peek()
        if char == "[":
            return self._read_blank()
        if char == "(":
            return self._read_collection()
        return self._read_iri()

    def _read_blank(self) -> Term:
        self._expect("[")
        node = self._fresh_blank()
        self._skip()
        if self._starts_with("]"):
            self._expect("]")
            return node
        self._predicate_object_list(node)
        self._expect("]")
        return node

    def _read_collection(self) -> Term:
        self._expect("(")
        items: list[Term] = []
        while True:
            self._skip()
            if self._starts_with(")"):
                self._expect(")")
                break
            items.append(self._read_object())
        if not items:
            return RDF_NIL
        head = self._fresh_blank()
        current = head
        for offset, item in enumerate(items):
            self._emit(current, RDF_FIRST, item)
            if offset == len(items) - 1:
                self._emit(current, RDF_REST, RDF_NIL)
            else:
                nxt = self._fresh_blank()
                self._emit(current, RDF_REST, nxt)
                current = nxt
        return head

    def _predicate_object_list(self, subject: Term) -> None:
        while True:
            self._skip()
            if self._starts_with("]") or self._starts_with("."):
                break
            predicate = self._read_verb()
            self._object_list(subject, predicate)
            self._skip()
            if self._starts_with(";"):
                self._expect(";")
                self._skip()
                if self._starts_with("]") or self._starts_with("."):
                    break
                continue
            break

    def _read_verb(self) -> Term:
        self._skip()
        if self._consume_word("a"):
            return RDF_TYPE
        return self._read_iri()

    def _object_list(self, subject: Term, predicate: Term) -> None:
        while True:
            obj = self._read_object()
            self._emit(subject, predicate, obj)
            self._skip()
            if self._starts_with(","):
                self._expect(",")
                continue
            break

    def _read_object(self) -> Term:
        self._skip()
        char = self._peek()
        if char == "[":
            return self._read_blank()
        if char == "(":
            return self._read_collection()
        if char == '"':
            return self._read_literal()
        return self._read_iri()

    def _read_literal(self) -> Term:
        self._expect('"')
        chars: list[str] = []
        while not self._eof():
            char = self._advance()
            if char == "\\":
                escaped = self._advance()
                chars.append({"\\": "\\", '"': '"', "n": "\n", "t": "\t"}.get(escaped, escaped))
                continue
            if char == '"':
                break
            chars.append(char)
        else:
            self._fail("Unterminated string.")
        value = "".join(chars)
        lang = None
        datatype = None
        if self._starts_with("@"):
            self._advance()
            start = self.index
            while not self._eof() and self.text[self.index].isalpha():
                self._advance()
            lang = self.text[start:self.index]
            if not lang:
                self._fail("Expected a language tag.")
        elif self._starts_with("^^"):
            self.index += 2
            datatype = self._read_iri().value
        return Term("literal", value, lang, datatype)


def parse_turtle(text: str) -> Graph:
    """Parse the restricted Turtle subset used by C3_ONTOLOGY_V1."""
    return _Parser(text).parse()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _without_integrity(package: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in package.items() if key != "integrity"}


def load_ontology_text(path: Path = ONTOLOGY_PATH) -> str:
    """Return the ontology document exactly as stored."""
    if not path.is_file():
        raise C3OntologyError(f"C3 ontology file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def load_c3_package(path: Path = PACKAGE_PATH) -> dict[str, Any]:
    """Load the checked-in C3 package record."""
    if not path.is_file():
        raise C3OntologyError(f"C3 package file does not exist: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise C3OntologyError("C3 package must be a JSON object.")
    return document


def _literal(graph: Graph, subject: Term, predicate: Term) -> str:
    term = graph.one(subject, predicate)
    if term.kind != "literal":
        raise C3OntologyError(f"{predicate} on {subject} is not a literal.")
    return term.value


def _types(graph: Graph, subject: Term) -> list[Term]:
    return graph.objects(subject, RDF_TYPE)


def _require_type(graph: Graph, subject: Term, type_term: Term) -> None:
    if type_term not in _types(graph, subject):
        raise C3OntologyError(f"{subject} is not declared as {type_term}.")


def _named_superclasses(graph: Graph, subject: Term) -> list[Term]:
    found = []
    for obj in graph.objects(subject, iri(RDFS + "subClassOf")):
        if obj.kind == "iri":
            found.append(obj)
    return found


def _restrictions(graph: Graph, subject: Term) -> list[Term]:
    found = []
    for obj in graph.objects(subject, iri(RDFS + "subClassOf")):
        if obj.kind == "blank":
            found.append(obj)
    return found


def _restriction_profile(graph: Graph, blank: Term) -> tuple[Term, Term]:
    _require_type(graph, blank, iri(OWL + "Restriction"))
    on_property = graph.one(blank, iri(OWL + "onProperty"))
    target = graph.one(blank, iri(OWL + "allValuesFrom"))
    predicates = {pred for subj, pred, _obj in graph.triples if subj == blank}
    allowed = {
        RDF_TYPE,
        iri(OWL + "onProperty"),
        iri(OWL + "allValuesFrom"),
    }
    if predicates != allowed:
        raise C3OntologyError(
            f"Restriction {blank} uses predicates outside the supported profile."
        )
    return on_property, target


def _member_lists(graph: Graph, type_term: Term) -> list[list[Term]]:
    lists = []
    for subject in graph.subjects_of_type(type_term):
        lists.append(graph.collection(graph.one(subject, iri(OWL + "members"))))
    return lists


def _has_property_disjoint(graph: Graph, left: Term, right: Term) -> bool:
    predicate = iri(OWL + "propertyDisjointWith")
    return right in graph.objects(left, predicate) or left in graph.objects(right, predicate)


def _forbid_external_iris(graph: Graph) -> None:
    for subject, predicate, obj in graph.triples:
        for term in (subject, predicate, obj):
            if term.kind != "iri":
                continue
            if term == RDF_NIL:
                continue
            if not any(
                term.value == prefix or term.value.startswith(prefix)
                for prefix in ALLOWED_IRI_PREFIXES
            ):
                raise C3OntologyError(f"IRI outside the provisional vocabulary: {term.value}")


def _validate_graph(graph: Graph) -> None:
    expected_prefixes = {
        "h": VOCABULARY_IRI,
        "owl": OWL,
        "rdf": RDF,
        "rdfs": RDFS,
    }
    if graph.prefixes != expected_prefixes:
        raise C3OntologyError(
            "C3 ontology prefixes differ from the provisional vocabulary profile."
        )
    ontology = iri(ONTOLOGY_IRI)
    _require_type(graph, ontology, iri(OWL + "Ontology"))
    if _literal(graph, ontology, h("namespaceStatus")) != "PROVISIONAL_NOT_PUBLISHED":
        raise C3OntologyError("Ontology namespace status is not provisional.")
    if _literal(graph, ontology, h("approvalStatus")) != "PENDING_HUMAN_APPROVAL":
        raise C3OntologyError("Ontology approval status is not pending.")
    if _literal(graph, ontology, h("artifactRole")) != "TBOX_ONLY":
        raise C3OntologyError("Ontology artifact role is not TBOX_ONLY.")
    if _literal(graph, ontology, h("c2PackageId")) != "C2_SCHEMA_V1":
        raise C3OntologyError("Ontology C2 package id does not match C2_SCHEMA_V1.")
    if _literal(graph, ontology, h("c2ContentSha256")) != C2_CONTENT_SHA256:
        raise C3OntologyError("Ontology C2 content hash does not match the pinned hash.")
    if _literal(graph, ontology, h("c2PayloadSha256")) != C2_PAYLOAD_SHA256:
        raise C3OntologyError("Ontology C2 payload hash does not match the pinned hash.")
    _forbid_external_iris(graph)

    forbidden_predicates = [
        iri(OWL + name)
        for name in (
            "imports",
            "equivalentProperty",
            "complementOf",
            "someValuesFrom",
            "qualifiedCardinality",
            "minCardinality",
            "maxCardinality",
            "cardinality",
            "hasValue",
            "sameAs",
        )
    ]
    for _subject, predicate, _obj in graph.triples:
        if predicate in forbidden_predicates:
            raise C3OntologyError(f"Forbidden axiom predicate {predicate.value}.")

    root = h("FirstOrderPosition")
    _require_type(graph, root, iri(OWL + "Class"))
    equivalents = graph.objects(root, iri(OWL + "equivalentClass"))
    if len(equivalents) != 1:
        raise C3OntologyError("FirstOrderPosition must have exactly one union equivalence.")
    union_node = equivalents[0]
    _require_type(graph, union_node, iri(OWL + "Class"))
    members = graph.collection(graph.one(union_node, iri(OWL + "unionOf")))
    if members != [h(name) for name in POSITIONS]:
        raise C3OntologyError("The union does not list the four C1 positions in C1 order.")
    equivalent_count = sum(
        1 for _s, predicate, _o in graph.triples if predicate == iri(OWL + "equivalentClass")
    )
    if equivalent_count != 1:
        raise C3OntologyError("The only class equivalence must be the scoped union.")

    disjoint_lists = _member_lists(graph, iri(OWL + "AllDisjointClasses"))
    if [h(name) for name in POSITIONS] not in disjoint_lists:
        raise C3OntologyError("The four position classes are not declared pairwise disjoint.")
    if [h(name) for name in CATEGORY_CLASSES] not in disjoint_lists:
        raise C3OntologyError("Category classes are not declared pairwise disjoint.")
    if len(disjoint_lists) != 2:
        raise C3OntologyError("Unexpected disjointness axiom.")

    for name in POSITIONS:
        klass = h(name)
        _require_type(graph, klass, iri(OWL + "Class"))
        if _named_superclasses(graph, klass) != [root]:
            raise C3OntologyError(f"{name} is not a direct subclass of FirstOrderPosition only.")
        restrictions = {
            _restriction_profile(graph, blank) for blank in _restrictions(graph, klass)
        }
        expected = {
            (h("correlatesWith"), h(CORRELATIVE_RANGE[name])),
            (h("oppositeOf"), h(OPPOSITE_RANGE[name])),
        }
        if restrictions != expected:
            raise C3OntologyError(f"{name} does not have the expected type restrictions.")

    for name in (*CATEGORY_CLASSES, *POSITIONS):
        if name == "FirstOrderPosition":
            continue
        declared = h(name)
        if iri(OWL + "Class") not in _types(graph, declared) and name in CATEGORY_CLASSES:
            raise C3OntologyError(f"{name} is not declared as a class.")

    for forbidden in FORBIDDEN_CLASS_NAMES:
        if h(forbidden) in graph.subjects_of_type(iri(OWL + "Class")):
            raise C3OntologyError(f"Forbidden class is declared: {forbidden}.")
        if any(term.value.endswith("#" + forbidden) for _s, _p, term in graph.triples if term.kind == "iri"):
            raise C3OntologyError(f"Forbidden name appears as an IRI: {forbidden}.")

    _require_property(
        graph,
        "hasBearer",
        functional=False,
        domain=root,
        range_term=h("Party"),
    )
    _require_property(
        graph,
        "hasCounterpart",
        functional=False,
        domain=root,
        range_term=h("Party"),
    )
    if _has_property_disjoint(graph, h("hasBearer"), h("hasCounterpart")):
        raise C3OntologyError(
            "Bearer and counterpart must not be property-disjoint. "
            "Distinct roles do not require distinct individuals."
        )
    _require_property(
        graph,
        "hasNormativeContent",
        functional=False,
        domain=root,
        range_term=h("NormativeContent"),
    )
    _require_property(
        graph,
        "hasAct",
        functional=False,
        domain=h("NormativeContent"),
        range_term=h("Act"),
    )
    _require_property(
        graph,
        "hasPolarity",
        functional=True,
        domain=h("NormativeContent"),
        range_term=h("Polarity"),
    )
    _require_property(
        graph,
        "expressedBy",
        functional=False,
        domain=root,
        range_term=h("NormativeStatement"),
    )
    _require_property(
        graph,
        "correlatesWith",
        functional=False,
        domain=root,
        range_term=root,
        symmetric=True,
        irreflexive=True,
    )
    _require_property(
        graph,
        "oppositeOf",
        functional=False,
        domain=root,
        range_term=root,
        symmetric=True,
        irreflexive=True,
    )
    if not _has_property_disjoint(graph, h("correlatesWith"), h("oppositeOf")):
        raise C3OntologyError("Correlative and opposite relations are not property-disjoint.")

    for local in ("Performance", "Forbearance"):
        individual = h(local)
        if iri(OWL + "NamedIndividual") not in _types(graph, individual):
            raise C3OntologyError(f"{local} is not a named individual.")
        if h("Polarity") not in _types(graph, individual):
            raise C3OntologyError(f"{local} is not a polarity.")
    if h("Performance") not in graph.objects(h("Forbearance"), iri(OWL + "differentFrom")):
        raise C3OntologyError("Performance and Forbearance are not declared different.")

    functional = {
        local
        for local in (
            "hasBearer",
            "hasCounterpart",
            "hasNormativeContent",
            "hasAct",
            "correlatesWith",
            "oppositeOf",
            "expressedBy",
        )
        if iri(OWL + "FunctionalProperty") in _types(graph, h(local))
    }
    if functional:
        raise C3OntologyError(
            "Bearer, counterpart, content, act, correlative, and opposite "
            "properties must not be functional: " + ", ".join(sorted(functional))
        )


def _require_property(
    graph: Graph,
    local: str,
    *,
    functional: bool,
    domain: Term,
    range_term: Term,
    symmetric: bool = False,
    irreflexive: bool = False,
) -> None:
    prop = h(local)
    _require_type(graph, prop, iri(OWL + "ObjectProperty"))
    is_functional = iri(OWL + "FunctionalProperty") in _types(graph, prop)
    if is_functional != functional:
        raise C3OntologyError(f"{local} functionality does not match the profile.")
    if symmetric != (iri(OWL + "SymmetricProperty") in _types(graph, prop)):
        raise C3OntologyError(f"{local} symmetry does not match the profile.")
    if irreflexive != (iri(OWL + "IrreflexiveProperty") in _types(graph, prop)):
        raise C3OntologyError(f"{local} irreflexivity does not match the profile.")
    if graph.objects(prop, iri(RDFS + "domain")) != [domain]:
        raise C3OntologyError(f"{local} domain is not the expected abstract class.")
    if graph.objects(prop, iri(RDFS + "range")) != [range_term]:
        raise C3OntologyError(f"{local} range is not the expected abstract class.")


def _validate_package_shape(package: dict[str, Any]) -> None:
    if package.get("package_id") != PACKAGE_ID:
        raise C3OntologyError("C3 package_id is not C3_ONTOLOGY_V1.")
    if package.get("package_version") != PACKAGE_VERSION:
        raise C3OntologyError("C3 package_version is not 1.0.0.")
    if package.get("artifact_role") != "TBOX_ONLY":
        raise C3OntologyError("C3 package is not marked TBOX_ONLY.")
    if package.get("experimental_condition_status") != "NOT_EXECUTABLE":
        raise C3OntologyError("C3 package must remain experimentally non-executable.")
    for forbidden_key in ("payload", "model_payload", "prompt", "examples"):
        if forbidden_key in package:
            raise C3OntologyError(f"C3 package contains extractor field {forbidden_key!r}.")
    namespace = package.get("namespace")
    if not isinstance(namespace, dict):
        raise C3OntologyError("C3 namespace record is missing.")
    if namespace.get("iri") != ONTOLOGY_IRI or namespace.get("status") != "PROVISIONAL_NOT_PUBLISHED":
        raise C3OntologyError("C3 namespace is not the pending provisional URN.")
    if namespace.get("approval") != "PENDING_HUMAN_APPROVAL":
        raise C3OntologyError("C3 namespace approval is not pending.")
    dependency = package.get("c2_dependency")
    if not isinstance(dependency, dict):
        raise C3OntologyError("C3 package has no C2 dependency.")
    if dependency.get("content_sha256") != C2_CONTENT_SHA256:
        raise C3OntologyError("C3 package pins a different C2 content hash.")
    if dependency.get("payload_sha256") != C2_PAYLOAD_SHA256:
        raise C3OntologyError("C3 package pins a different C2 payload hash.")
    labels = package.get("c1_dependency", {}).get("labels")
    if labels != list(POSITIONS):
        raise C3OntologyError("C3 package does not pin the C1 label order.")


def _validate_live_dependencies(package: dict[str, Any]) -> None:
    c2_package = load_c2_package()
    if c2_package["integrity"]["content_sha256"] != C2_CONTENT_SHA256:
        raise C3OntologyError("Live C2 content hash differs from the pinned C3 dependency.")
    if c2_package["integrity"]["payload_sha256"] != C2_PAYLOAD_SHA256:
        raise C3OntologyError("Live C2 payload hash differs from the pinned C3 dependency.")
    if content_sha256(c2_package) != C2_CONTENT_SHA256:
        raise C3OntologyError("Recomputed C2 content hash differs from the pinned dependency.")
    if load_c1_labels() != list(POSITIONS):
        raise C3OntologyError("Live C1 labels differ from the four position classes.")
    c1_document = json.loads(C1_PATH.read_text(encoding="utf-8"))
    if c1_document.get("version") != package["c1_dependency"]["version"]:
        raise C3OntologyError("C1 version does not match the C3 dependency record.")


def _reject_forbidden_text(text: str, label: str) -> None:
    for marker in _FORBIDDEN_TEXT:
        if marker in text:
            raise C3OntologyError(f"{label} contains forbidden marker {marker!r}.")
    if _SIGNATURE_RE.search(text):
        raise C3OntologyError(f"{label} contains an observed relation signature.")


def validate_c3_ontology(
    package: dict[str, Any] | None = None,
    ontology_text: str | None = None,
    *,
    require_integrity: bool = True,
) -> Graph:
    """Validate the package record, the Turtle profile, and the live C2 hashes."""
    document = package if package is not None else load_c3_package()
    text = ontology_text if ontology_text is not None else load_ontology_text()
    if not isinstance(document, dict):
        raise C3OntologyError("C3 package must be a JSON object.")
    _validate_package_shape(document)
    _reject_forbidden_text(text, "C3 ontology")
    _reject_forbidden_text(canonical_dumps(document), "C3 package")
    ontology_hash = _sha256(text)
    recorded = document.get("ontology", {}).get("sha256")
    if recorded != ontology_hash:
        raise C3OntologyError("C3 ontology sha256 does not match the Turtle bytes.")
    if ontology_hash != ONTOLOGY_SHA256:
        raise C3OntologyError("C3 ontology bytes differ from the pinned 1.0.1 hash.")
    graph = parse_turtle(text)
    _validate_graph(graph)
    _validate_live_dependencies(document)
    if require_integrity:
        integrity = document.get("integrity")
        if not isinstance(integrity, dict):
            raise C3OntologyError("C3 integrity block must be an object.")
        if integrity.get("content_sha256") != content_sha256(document):
            raise C3OntologyError("C3 content_sha256 does not match the canonical package bytes.")
        if integrity.get("content_sha256") != PACKAGE_CONTENT_SHA256:
            raise C3OntologyError("C3 content hash differs from the pinned manifest hash.")
    return graph


def attach_integrity(package: dict[str, Any], ontology_text: str) -> dict[str, Any]:
    """Return a copy whose ontology and content hashes match the given bytes."""
    body = _without_integrity(package)
    ontology = dict(body.get("ontology", {}))
    ontology["sha256"] = _sha256(ontology_text)
    body["ontology"] = ontology
    provisional = dict(body)
    provisional["integrity"] = {
        "canonicalization": "json.dumps ensure_ascii=false indent=2 trailing-newline",
        "content_sha256": content_sha256(provisional),
    }
    return provisional


def _local_name(term: Term) -> str:
    if term.kind != "iri" or not term.value.startswith(VOCABULARY_IRI):
        raise C3OntologyError(f"Formal projection expected a vocabulary IRI, found {term}.")
    return term.value[len(VOCABULARY_IRI) :]


def _prefixed(local: str) -> str:
    return "h:" + local


def _has_owl_predicate(graph: Graph, name: str) -> bool:
    predicate = iri(OWL + name)
    return any(pred == predicate for _subject, pred, _obj in graph.triples)


def _series(items: list[str]) -> str:
    if not items:
        raise C3OntologyError("Formal projection cannot render an empty list.")
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _typed_locals(graph: Graph, type_term: Term) -> list[str]:
    names = []
    for subject in graph.subjects_of_type(type_term):
        if subject.kind == "iri" and subject.value.startswith(VOCABULARY_IRI):
            names.append(_local_name(subject))
    return names


def _reject_unselected_constructs(graph: Graph) -> None:
    for name in (
        "someValuesFrom",
        "minCardinality",
        "maxCardinality",
        "cardinality",
        "qualifiedCardinality",
        "oneOf",
        "complementOf",
        "imports",
        "equivalentProperty",
    ):
        if _has_owl_predicate(graph, name):
            raise C3OntologyError(
                f"The TBox contains owl:{name}. The projection does not drop or negate it."
            )


def _axiom(
    identifier: str,
    owl: str,
    natural: str,
    *,
    status: str = "ASSERTED_AXIOM",
    included: bool = True,
    note: str = "",
) -> dict[str, Any]:
    return {
        "id": identifier,
        "status": status,
        "owl": owl,
        "natural": natural,
        "included": included,
        "note": note,
    }


def _unspecified(identifier: str, note: str) -> dict[str, Any]:
    return _axiom(identifier, "", "", status="UNSPECIFIED", included=False, note=note)


def select_axioms(graph: Graph) -> list[dict[str, Any]]:
    """Select asserted TBox axioms for the experimental projection.

    Absence of an axiom is recorded separately and is not turned into a negative
    axiom. This function does not run a reasoner.
    """
    _reject_unselected_constructs(graph)
    root = "FirstOrderPosition"
    subclasses = [
        _local_name(subject)
        for subject, predicate, obj in graph.triples
        if predicate == iri(RDFS + "subClassOf")
        and obj == h(root)
        and subject.kind == "iri"
    ]
    union_node = graph.one(h(root), iri(OWL + "equivalentClass"))
    union = [
        _local_name(item)
        for item in graph.collection(graph.one(union_node, iri(OWL + "unionOf")))
    ]
    if subclasses != list(POSITIONS) or union != list(POSITIONS):
        raise C3OntologyError("The union and the subclass list are not the four C1 classes.")
    disjoint_lists = [
        [_local_name(item) for item in members]
        for members in _member_lists(graph, iri(OWL + "AllDisjointClasses"))
    ]
    if sorted(disjoint_lists) != sorted([list(POSITIONS), list(CATEGORY_CLASSES)]):
        raise C3OntologyError("The disjointness axioms are not the two expected lists.")

    records: list[dict[str, Any]] = []
    for name in _typed_locals(graph, iri(OWL + "Class")):
        records.append(
            _axiom(
                f"class-declaration-{name}",
                f"Declaration(Class({_prefixed(name)}))",
                f"{name} is a class.",
            )
        )
    for name in subclasses:
        records.append(
            _axiom(
                f"subclass-{name}-{root}",
                f"SubClassOf({_prefixed(name)} {_prefixed(root)})",
                f"{name} is a subclass of {root}.",
            )
        )
    records.append(
        _axiom(
            "equivalent-classes-FirstOrderPosition",
            "EquivalentClasses("
            + _prefixed(root)
            + " ObjectUnionOf("
            + " ".join(_prefixed(name) for name in union)
            + "))",
            f"{root} is exactly the union of {_series(union)}.",
        )
    )
    for members in disjoint_lists:
        label = "positions" if members == list(POSITIONS) else "categories"
        records.append(
            _axiom(
                f"disjoint-classes-{label}",
                "DisjointClasses(" + " ".join(_prefixed(name) for name in members) + ")",
                f"{_series(members)} are pairwise disjoint.",
            )
        )

    properties = _typed_locals(graph, iri(OWL + "ObjectProperty"))
    for name in properties:
        prop = h(name)
        types = set(graph.objects(prop, RDF_TYPE))
        records.append(
            _axiom(
                f"property-declaration-{name}",
                f"Declaration(ObjectProperty({_prefixed(name)}))",
                f"{name} is an object property.",
            )
        )
        records.append(
            _axiom(
                f"domain-{name}",
                "ObjectPropertyDomain("
                + _prefixed(name)
                + " "
                + _prefixed(_local_name(graph.one(prop, iri(RDFS + "domain"))))
                + ")",
                f"{name} has domain {_local_name(graph.one(prop, iri(RDFS + 'domain')))}.",
            )
        )
        records.append(
            _axiom(
                f"range-{name}",
                "ObjectPropertyRange("
                + _prefixed(name)
                + " "
                + _prefixed(_local_name(graph.one(prop, iri(RDFS + "range"))))
                + ")",
                f"{name} has range {_local_name(graph.one(prop, iri(RDFS + 'range')))}.",
            )
        )
        if iri(OWL + "SymmetricProperty") in types:
            records.append(
                _axiom(
                    f"symmetric-{name}",
                    f"SymmetricObjectProperty({_prefixed(name)})",
                    f"{name} is symmetric.",
                )
            )
        if iri(OWL + "IrreflexiveProperty") in types:
            records.append(
                _axiom(
                    f"irreflexive-{name}",
                    f"IrreflexiveObjectProperty({_prefixed(name)})",
                    f"{name} is irreflexive.",
                )
            )
        if iri(OWL + "FunctionalProperty") in types:
            if name == "hasPolarity":
                functional_text = (
                    f"{name} is functional, meaning one content is linked to "
                    "no more than one distinct polarity."
                )
            else:
                functional_text = (
                    f"{name} is functional, meaning one subject is linked to "
                    "no more than one distinct object."
                )
            records.append(
                _axiom(
                    f"functional-{name}",
                    f"FunctionalObjectProperty({_prefixed(name)})",
                    functional_text,
                )
            )

    for subject, predicate, obj in graph.triples:
        if predicate != iri(OWL + "propertyDisjointWith"):
            continue
        left = _local_name(subject)
        right = _local_name(obj)
        records.append(
            _axiom(
                f"disjoint-properties-{left}-{right}",
                f"DisjointObjectProperties({_prefixed(left)} {_prefixed(right)})",
                f"{left} and {right} are disjoint properties.",
            )
        )

    for name in POSITIONS:
        for blank in _restrictions(graph, h(name)):
            prop, filler = _restriction_profile(graph, blank)
            prop_name = _local_name(prop)
            filler_name = _local_name(filler)
            records.append(
                _axiom(
                    f"all-values-{name}-{prop_name}",
                    "SubClassOf("
                    + _prefixed(name)
                    + " ObjectAllValuesFrom("
                    + _prefixed(prop_name)
                    + " "
                    + _prefixed(filler_name)
                    + "))",
                    f"If a position of class {name} is linked by {prop_name}, "
                    f"every linked individual is a {filler_name}.",
                )
            )

    for name in _typed_locals(graph, iri(OWL + "NamedIndividual")):
        records.append(
            _axiom(
                f"individual-declaration-{name}",
                f"Declaration(NamedIndividual({_prefixed(name)}))",
                f"{name} is a named individual.",
            )
        )
    for subject, predicate, obj in graph.triples:
        if predicate != RDF_TYPE or obj != h("Polarity") or subject.kind != "iri":
            continue
        name = _local_name(subject)
        records.append(
            _axiom(
                f"class-assertion-{name}-Polarity",
                f"ClassAssertion({_prefixed('Polarity')} {_prefixed(name)})",
                f"{name} is a Polarity.",
            )
        )
    for subject, predicate, obj in graph.triples:
        if predicate != iri(OWL + "differentFrom"):
            continue
        left = _local_name(subject)
        right = _local_name(obj)
        records.append(
            _axiom(
                f"different-{left}-{right}",
                f"DifferentIndividuals({_prefixed(left)} {_prefixed(right)})",
                f"{left} is different from {right}.",
            )
        )
    return records


def audit_axiom_records(graph: Graph) -> list[dict[str, Any]]:
    """Return selected axioms plus records that an absent axiom was not negated."""
    selected = select_axioms(graph)
    functional = {
        record["id"].removeprefix("functional-")
        for record in selected
        if record["id"].startswith("functional-")
    }
    symmetric = {
        record["id"].removeprefix("symmetric-")
        for record in selected
        if record["id"].startswith("symmetric-")
    }
    audit = [
        _unspecified(
            "namespace-status",
            "The ontology IRI is provisional. The namespaceStatus annotation stays out of the experimental projection.",
        )
    ]
    for name in ("hasBearer", "hasCounterpart", "hasNormativeContent", "hasAct", "expressedBy", "correlatesWith", "oppositeOf"):
        if name not in functional:
            audit.append(
                _unspecified(
                    f"functionality-unspecified-{name}",
                    f"No functional axiom is declared for {name}. Absence is not an assertion that the property is non-functional.",
                )
            )
        if name not in symmetric and name not in {"correlatesWith", "oppositeOf"}:
            audit.append(
                _unspecified(
                    f"symmetry-unspecified-{name}",
                    f"No symmetry axiom is declared for {name}. Absence is not an assertion that the property is asymmetric.",
                )
            )
    audit.extend(
        [
            _unspecified(
                "existential-restrictions-unspecified",
                "No owl:someValuesFrom axiom is declared. Absence does not assert that a correlative or opposite link is impossible.",
            ),
            _unspecified(
                "polarity-enumeration-unspecified",
                "No owl:oneOf axiom closes Polarity. Absence does not forbid another polarity individual.",
            ),
            _unspecified(
                "minimum-cardinality-unspecified",
                "No minimum cardinality is declared. Absence does not assert that a value is forbidden.",
            ),
        ]
    )
    return selected + audit


def render_owl_functional(records: list[dict[str, Any]]) -> str:
    """Serialize included axioms in OWL 2 Functional-Style Syntax."""
    lines = [
        f"Prefix(h:=<{VOCABULARY_IRI}>)",
        "Prefix(owl:=<http://www.w3.org/2002/07/owl#>)",
        "Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)",
        "Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)",
        f"Ontology(<{ONTOLOGY_IRI}>",
    ]
    for record in records:
        if record["status"] != "ASSERTED_AXIOM" or record["included"] is not True:
            continue
        if not record["owl"]:
            raise C3OntologyError(f"Included axiom {record['id']} has no OWL expression.")
        lines.append("  " + record["owl"])
    lines.append(")")
    return "\n".join(lines) + "\n"


def render_formal_natural(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Paraphrase only the axioms included in the OWL projection."""
    rendered = []
    for record in records:
        if record["included"] is not True:
            continue
        if record["status"] != "ASSERTED_AXIOM" or not record["natural"]:
            raise C3OntologyError(f"Included axiom {record['id']} has no natural-language paraphrase.")
        rendered.append({"id": record["id"], "text": record["natural"]})
    return rendered


def _extend_c2_payload(key: str, value: Any) -> dict[str, Any]:
    from re_te_benchmark.conditioning.c2 import model_payload as project_c2_payload

    payload = project_c2_payload()
    if key in payload:
        raise C3OntologyError(f"C2 payload already contains {key!r}.")
    payload[key] = value
    return payload


def c3_model_payload() -> dict[str, Any]:
    """Return the C2 payload plus OWL Functional-Style Syntax. This does not enable C3."""
    graph = validate_c3_ontology()
    return _extend_c2_payload("owl_functional", render_owl_functional(select_axioms(graph)))


def c3_nl_model_payload() -> dict[str, Any]:
    """Return the C2 payload plus paraphrases of the same included axioms."""
    graph = validate_c3_ontology()
    return _extend_c2_payload("formal_natural", render_formal_natural(select_axioms(graph)))
