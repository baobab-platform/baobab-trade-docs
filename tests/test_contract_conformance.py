"""Synthetic owner/reference compatibility, independent of live authority proof."""
import hashlib
import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from reference.shared_contracts import PROVENANCE, ContractViolation, validate_contract

ROOT = Path(__file__).resolve().parents[1]
SHARED = Path(os.environ.get("SHARED_CHECKOUT", ROOT.parent / "shared"))
CASES = json.loads((ROOT / "tests/fixtures/authority-contract-cases.json").read_bytes())


class ContractConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = yaml.safe_load((ROOT / "contracts.lock.yaml").read_bytes())
        cls.registry = Registry()
        # Independent owner read: do not validate one generated copy with another.
        for path in cls.lock["contracts"]:
            raw = subprocess.check_output(["git", "-C", str(SHARED), "show", f"{cls.lock['source']['commit']}:{path}"])
            if path.endswith(".schema.json"):
                schema = json.loads(raw)
                cls.registry = cls.registry.with_resource(schema["$id"], Resource.from_contents(schema))

    def test_all_vectors_match_immutable_owner_and_reference(self):
        for case in CASES:
            with self.subTest(case=case["name"]):
                owner = Draft202012Validator({"$ref": PROVENANCE["entries"][case["contract"]]},
                    registry=self.registry, format_checker=Draft202012Validator.FORMAT_CHECKER)
                self.assertEqual(owner.is_valid(case["instance"]), case["valid"])
                if case["valid"]:
                    validate_contract(case["contract"], case["instance"])
                else:
                    with self.assertRaises(ContractViolation):
                        validate_contract(case["contract"], case["instance"])

    def test_generated_inventory_bytes_and_provenance_match_owner(self):
        spec = importlib.util.spec_from_file_location("sync", ROOT / "scripts/sync_contracts.py")
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        owned = sync.generate(SHARED)
        actual = {str(p.relative_to(sync.TARGET)): p.read_bytes()
                  for p in sync.TARGET.rglob("*") if p.is_file()}
        self.assertEqual(actual, owned)
        self.assertEqual(PROVENANCE["commit"], self.lock["source"]["commit"])
        self.assertEqual(PROVENANCE["repository"], self.lock["source"]["repository"])
        self.assertEqual(set(PROVENANCE["files"]), {p.removeprefix("contracts/") for p in self.lock["contracts"]})
        for path, digest in PROVENANCE["files"].items():
            self.assertEqual(hashlib.sha256(owned[path]).hexdigest(), digest)

    def test_registry_pin_is_not_workload_activation(self):
        workloads = yaml.safe_load(subprocess.check_output(["git", "-C", str(SHARED), "show",
            f"{self.lock['source']['commit']}:contracts/identity/v1/workload-registry.yaml"]))["workloads"]
        staging = workloads["baobab-trade-docs-legal-actor-assessor-staging"]
        self.assertEqual(staging["status"], "PROVISIONED")
        self.assertEqual(staging["context_purposes"], ["RUNTIME"])
        self.assertEqual(set(staging["allowed_scopes"]), {"context:resolve", "legal-actor:assess"})
        profile = yaml.safe_load((ROOT / ".baobab/rtd-conformance.yaml").read_bytes())
        self.assertEqual(profile["repository"]["maturity"], "ARCHITECTURE_ONLY")
        self.assertEqual(profile["shared"]["commit"], PROVENANCE["commit"])
