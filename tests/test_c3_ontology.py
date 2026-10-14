"""Structural checks for the provisional C3 TBox.

The conflict helper below applies only explicit types and explicitly stored
links. It is not an OWL 2 DL reasoner, and a passing fixture does not mean a
reasoner accepted the ontology.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from re_te_benchmark.conditioning import c3  # noqa: E402
from re_te_benchmark.conditioning.c2 import load_c2_package  # noqa: E402
from re_te_benchmark.conditioning.c3 import (  # noqa: E402
    C2_CONTENT_SHA256,
    C2_PAYLOAD_SHA256,
    C3OntologyError,
    RDF_TYPE,
    Term,
    attach_integrity,
    canonical_dumps,
    h,
    iri,
    load_c3_package,
    load_ontology_text,
    parse_turtle,
    validate_c3_ontology,
)


FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "c3"
OWL = "http://www.w3.org/2002/07/owl#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"


def _ancestors(tbox: c3.Graph) -> dict[Term, set[Term]]:
    direct: dict[Term, set[Term]] = {}
    subclass = iri(RDFS + "subClassOf")
    for subject, predicate, obj in tbox.triples:
        if predicate == subclass and subject.kind == "iri" and obj.kind == "iri":
            direct.setdefault(subject, set()).add(obj)
    cache: dict[Term, set[Term]] = {}

    def walk(node: Term) -> set[Term]:
        if node in cache:
            return cache[node]
        found: set[Term] = set()
        for parent in direct.get(node, ()):
            found.add(parent)
            found.update(walk(parent))
        cache[node] = found
        return found

    for node in direct:
        walk(node)
    return cache


def _disjoint_pairs(tbox: c3.Graph) -> set[frozenset[Term]]:
    pairs: set[frozenset[Term]] = set()
    for subject in tbox.subjects_of_type(iri(OWL + "AllDisjointClasses")):
        members = tbox.collection(tbox.one(subject, iri(OWL + "members")))
        for index, left in enumerate(members):
            for right in members[index + 1 :]:
                pairs.add(frozenset((left, right)))
    return pairs


def _is_disjoint(
    left: Term,
    right: Term,
    pairs: set[frozenset[Term]],
    ancestors: dict[Term, set[Term]],
) -> bool:
    if left == right:
        return False
    left_nodes = {left, *ancestors.get(left, set())}
    right_nodes = {right, *ancestors.get(right, set())}
    return any(
        frozenset((one, other)) in pairs
        for one in left_nodes
        for other in right_nodes
        if one != other
    )


def explicit_assertion_conflicts(tbox: c3.Graph, abox: c3.Graph) -> set[str]:
    """Return conflict codes for fully explicit fixture assertions.

    Missing links are not conflicts. Symmetric properties are not expanded.
    Unique-name consequences are reported only when owl:differentFrom is stored.
    """
    ancestors = _ancestors(tbox)
    disjoint = _disjoint_pairs(tbox)
    subclass = iri(RDFS + "subClassOf")
    restrictions: dict[Term, list[tuple[Term, Term]]] = {}
    for subject, predicate, obj in tbox.triples:
        if predicate != subclass or obj.kind != "blank":
            continue
        restrictions.setdefault(subject, []).append(
            (
                tbox.one(obj, iri(OWL + "onProperty")),
                tbox.one(obj, iri(OWL + "allValuesFrom")),
            )
        )
    functional = {
        subject
        for subject in tbox.subjects_of_type(iri(OWL + "FunctionalProperty"))
    }
    irreflexive = {
        subject
        for subject in tbox.subjects_of_type(iri(OWL + "IrreflexiveProperty"))
    }
    property_disjoint: set[frozenset[Term]] = set()
    different: set[frozenset[Term]] = set()
    combined = list(tbox.triples) + list(abox.triples)
    types: dict[Term, set[Term]] = {}
    links: dict[Term, set[tuple[Term, Term]]] = {}
    for subject, predicate, obj in combined:
        if predicate == RDF_TYPE and obj.kind == "iri":
            types.setdefault(subject, set()).add(obj)
        elif predicate == iri(OWL + "differentFrom"):
            different.add(frozenset((subject, obj)))
        else:
            links.setdefault(predicate, set()).add((subject, obj))
    for subject, predicate, obj in tbox.triples:
        if predicate == iri(OWL + "propertyDisjointWith"):
            property_disjoint.add(frozenset((subject, obj)))

    codes: set[str] = set()
    for type_set in types.values():
        ordered = list(type_set)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if _is_disjoint(left, right, disjoint, ancestors):
                    codes.add("class_disjoint")
    for subject, type_set in types.items():
        for type_term in type_set:
            for prop, target in restrictions.get(type_term, ()):
                for link_subject, link_object in links.get(prop, ()):
                    if link_subject != subject:
                        continue
                    object_types = types.get(link_object, set())
                    if not object_types:
                        continue
                    if any(
                        obj_type == target or target in ancestors.get(obj_type, set())
                        for obj_type in object_types
                    ):
                        continue
                    if any(
                        _is_disjoint(obj_type, target, disjoint, ancestors)
                        for obj_type in object_types
                    ):
                        codes.add("universal_type")
    for prop in irreflexive:
        if any(subject == obj for subject, obj in links.get(prop, ())):
            codes.add("irreflexive")
    for pair in property_disjoint:
        left, right = tuple(pair)
        shared = links.get(left, set()) & links.get(right, set())
        if shared:
            codes.add("property_disjoint")
    for prop in functional:
        grouped: dict[Term, set[Term]] = {}
        for subject, obj in links.get(prop, ()):
            grouped.setdefault(subject, set()).add(obj)
        for objects in grouped.values():
            ordered = list(objects)
            for index, left in enumerate(ordered):
                for right in ordered[index + 1 :]:
                    if frozenset((left, right)) in different:
                        codes.add("functional_clash")
    return codes


class C3OntologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = load_c3_package()
        cls.ontology_text = load_ontology_text()
        cls.graph = validate_c3_ontology(cls.package, cls.ontology_text)
        cls.tbox = parse_turtle(cls.ontology_text)

    def _fixture(self, name: str) -> c3.Graph:
        return parse_turtle((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    def test_package_is_tbox_only_and_not_executable(self) -> None:
        self.assertEqual(self.package["artifact_role"], "TBOX_ONLY")
        self.assertEqual(self.package["experimental_condition_status"], "NOT_EXECUTABLE")
        self.assertEqual(
            self.package["namespace"]["status"],
            "PROVISIONAL_NOT_PUBLISHED",
        )
        self.assertFalse(hasattr(c3, "model_payload"))
        for key in ("payload", "prompt", "examples"):
            self.assertNotIn(key, self.package)

    def test_c2_and_c1_hashes_are_pinned_to_the_live_packages(self) -> None:
        live = load_c2_package()
        self.assertEqual(live["integrity"]["content_sha256"], C2_CONTENT_SHA256)
        self.assertEqual(live["integrity"]["payload_sha256"], C2_PAYLOAD_SHA256)
        self.assertEqual(
            self.package["c2_dependency"]["content_sha256"],
            C2_CONTENT_SHA256,
        )
        self.assertEqual(
            self.package["c2_dependency"]["payload_sha256"],
            C2_PAYLOAD_SHA256,
        )
        self.assertEqual(
            self.package["c1_dependency"]["labels"],
            ["Duty", "Right", "Privilege", "NoRight"],
        )

    def test_integrity_is_deterministic(self) -> None:
        rebuilt = attach_integrity(copy.deepcopy(self.package), self.ontology_text)
        self.assertEqual(canonical_dumps(rebuilt), canonical_dumps(self.package))
        self.assertEqual(
            rebuilt["ontology"]["sha256"],
            "5dfac3fae2f74aa9aa1f22efb2d41531b10eba43117f67fdfd8601cd4209d397",
        )

    def test_restricted_parser_reads_a_blank_restriction(self) -> None:
        graph = parse_turtle(
            "@prefix ex: <urn:example:re-te-benchmark:c3:parser#> .\n"
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
            "ex:Item a owl:Class ;\n"
            "  owl:equivalentClass [ a owl:Class ; owl:unionOf ( ex:One ex:Two ) ] .\n"
        )
        equivalents = [
            obj
            for subject, predicate, obj in graph.triples
            if predicate.value.endswith("equivalentClass")
        ]
        self.assertEqual(graph.collection(graph.one(equivalents[0], iri(OWL + "unionOf"))), [
            iri("urn:example:re-te-benchmark:c3:parser#One"),
            iri("urn:example:re-te-benchmark:c3:parser#Two"),
        ])

    def test_withdrawn_role_and_act_axioms_are_absent(self) -> None:
        bearer = h("hasBearer")
        counterpart = h("hasCounterpart")
        disjoint = iri(OWL + "propertyDisjointWith")
        pairs = {
            frozenset((subject, obj))
            for subject, predicate, obj in self.tbox.triples
            if predicate == disjoint
        }
        self.assertNotIn(frozenset((bearer, counterpart)), pairs)
        self.assertNotIn(
            iri(OWL + "FunctionalProperty"),
            self.tbox.objects(h("hasAct"), RDF_TYPE),
        )
        self.assertIn(
            iri(OWL + "FunctionalProperty"),
            self.tbox.objects(h("hasPolarity"), RDF_TYPE),
        )
        self.assertIn("functional_polarity", self.package["implemented_commitments"])
        self.assertNotIn(
            "bearer_counterpart_property_disjointness",
            self.package["implemented_commitments"],
        )
        self.assertNotIn("functional_act_and_polarity", self.package["implemented_commitments"])
        withdrawn = {item["id"] for item in self.package["withdrawn_commitments"]}
        self.assertEqual(
            withdrawn,
            {"bearer_counterpart_property_disjointness", "functional_act"},
        )

    def test_explicit_consistent_fixtures_have_no_local_conflict(self) -> None:
        for name in (
            "consistent_unswapped.ttl",
            "consistent_absent_correlative.ttl",
            "consistent_opposite_different_act.ttl",
            "consistent_same_party.ttl",
            "consistent_two_acts.ttl",
        ):
            self.assertEqual(
                explicit_assertion_conflicts(self.tbox, self._fixture(name)),
                set(),
                name,
            )
        unswapped = (FIXTURE_DIR / "consistent_unswapped.ttl").read_text(encoding="utf-8")
        self.assertEqual(unswapped.count("h:hasBearer fx:party-north"), 2)

    def test_explicit_inconsistent_fixtures_report_the_local_axiom(self) -> None:
        cases = {
            "inconsistent_correlative_type.ttl": {"universal_type"},
            "inconsistent_self_and_overlap.ttl": {
                "irreflexive",
                "universal_type",
                "property_disjoint",
            },
            "inconsistent_two_classes_and_polarities.ttl": {
                "class_disjoint",
                "functional_clash",
            },
        }
        for name, expected in cases.items():
            found = explicit_assertion_conflicts(self.tbox, self._fixture(name))
            self.assertTrue(expected <= found, f"{name}: {found}")

    def test_fixtures_do_not_reuse_benchmark_labels_or_statute_text(self) -> None:
        for path in FIXTURE_DIR.glob("*.ttl"):
            text = path.read_text(encoding="utf-8")
            for marker in (
                "LegalAgent",
                "LegalEntity",
                "LegalConcept",
                "Estatuto",
                "trabajador",
                "empresa",
                "subvenciones",
            ):
                self.assertNotIn(marker, text, path.name)

    def test_drifted_ontology_hash_fails_closed(self) -> None:
        mutated = dict(self.package)
        mutated["ontology"] = dict(self.package["ontology"])
        mutated["ontology"]["sha256"] = "0" * 64
        with self.assertRaises(C3OntologyError):
            validate_c3_ontology(mutated, self.ontology_text, require_integrity=False)

    def test_experimental_manifest_remains_not_ready(self) -> None:
        manifest = (PROJECT_ROOT / "schemas" / "conditioning_conditions.json").read_text(
            encoding="utf-8"
        )
        self.assertIn('"readiness": "NOT_READY"', manifest)
        spec = (PROJECT_ROOT / "docs" / "CONDITIONING_SPEC.md").read_text(encoding="utf-8")
        self.assertIn("C3_ONTOLOGY_V1", spec)
        self.assertIn("PROVISIONAL_NOT_PUBLISHED", spec)
        self.assertIn("not an extractor payload", spec)
        questions = self.package["competency_questions"]
        self.assertEqual(
            [question["id"] for question in questions],
            [
                "CQ-COV",
                "CQ-COR-TYPE",
                "CQ-COR-WRONG",
                "CQ-NO-COR",
                "CQ-NORIGHT",
                "CQ-SYM",
                "CQ-NO-INVERSION",
                "CQ-POLARITY",
                "CQ-SAME-PARTY",
                "CQ-ACTS",
                "CQ-VOCAB",
            ],
        )
        for question in questions:
            self.assertIn(question["id"], spec)


if __name__ == "__main__":
    unittest.main()
