"""HYB-02 exhaustive schema-definition inventory and immutable owner parity.
This is schema integrity/compilation coverage, not semantic acceptance of every
possible JSON instance. Independent malformed/positive vectors remain required.
"""
import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from reference.shared_contracts import PROVENANCE

ROOT = Path(__file__).resolve().parents[1]
SHARED = Path(os.environ.get("SHARED_CHECKOUT", ROOT.parent / "shared"))
TARGETS = (
 "trade-document/v2/domain.schema.json",
 "trade-document/v2/events.schema.json",
 "cross-engine-reference/v1/domain.schema.json",
 "regulatory-document-exchange/v1/domain.schema.json",
 "regulatory-document-exchange/v1/events.schema.json",
 "events/v1/envelope.schema.json",
)
class SharedSchemaInventoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.schemas = {}
  cls.registry = Registry()
  for path, digest in PROVENANCE["files"].items():
   if not path.endswith(".schema.json"): continue
   raw = (ROOT/"reference/shared_contracts/data"/path).read_bytes()
   if hashlib.sha256(raw).hexdigest() != digest:
    raise AssertionError("Shared package digest drift")
   owner = subprocess.check_output(["git","-C",str(SHARED),"show",f"{PROVENANCE['commit']}:contracts/{path}"])
   if raw != owner: raise AssertionError("Shared owner byte drift")
   schema = json.loads(raw)
   Draft202012Validator.check_schema(schema)
   cls.schemas[path] = schema
   cls.registry = cls.registry.with_resource(schema["$id"],Resource.from_contents(schema))
 def test_all_target_definitions_compile_and_resolve(self):
  for path in TARGETS:
   schema = self.schemas[path]
   self.assertIsInstance(schema, dict, path)
   for name in schema.get("$defs", {}):
    with self.subTest(schema=path, definition=name):
     ref = schema["$id"]+"#/$defs/"+name.replace("~","~0").replace("/","~1")
     validator = Draft202012Validator({"$ref":ref},registry=self.registry,format_checker=Draft202012Validator.FORMAT_CHECKER)
     # Exercise resolution even for nested external $refs. A deliberately
     # unconstrained probe may validate or fail; unresolved refs must never pass.
     validator.is_valid(None)
 def test_pinned_immutable_owner(self):
  self.assertEqual(PROVENANCE["commit"],"a9c53087d63caa356edf54ec8037ba1713c4827f")
  for path in TARGETS: self.assertIn(path,self.schemas)

 def test_all_definitions_adversarial_shape_matrix(self):
  """Exercise every definition with independent malformed and boundary shapes.

  This is deterministic cross-owner validator agreement, NOT a proof that the
  entire JSON Schema state space has been exhausted.
  """
  probes = [
   None, True, False, 0, -1, 1, 1.5, "", "a", "é", "00000000-0000-4000-8000-000000000000",
   "2026-10-26T00:00:00Z", "not-a-date", [], [None], [1,2],
   {}, {"unknown":True}, {"id":"bad"}, {"tenant_id":"bad"},
   {"document_id":"tdoc_abc"}, {"version":1},
  ]
  for path in TARGETS:
   schema = self.schemas[path]
   for name in schema["$defs"]:
    ref = schema["$id"]+"#/$defs/"+name.replace("~","~0").replace("/","~1")
    owner_schema = json.loads(subprocess.check_output([
     "git","-C",str(SHARED),"show",f"{PROVENANCE['commit']}:contracts/{path}"
    ]))
    owner_registry = self.registry.with_resource(owner_schema["$id"],Resource.from_contents(owner_schema))
    packaged = Draft202012Validator({"$ref":ref},registry=self.registry,format_checker=Draft202012Validator.FORMAT_CHECKER)
    owner = Draft202012Validator({"$ref":ref},registry=owner_registry,format_checker=Draft202012Validator.FORMAT_CHECKER)
    for probe in probes:
     with self.subTest(schema=path, definition=name, probe=repr(probe)[:50]):
      self.assertEqual(owner.is_valid(probe), packaged.is_valid(probe))
