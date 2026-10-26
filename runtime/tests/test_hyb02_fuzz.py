"""Deterministic adversarial fuzz corpus for PyO3 boundary; reproducible seed.
This is bounded mutation testing, not coverage-guided libFuzzer qualification.
"""
import hashlib
import random
import string
import unittest
from baobab_tdoc_kernel import sha256_hex, validate_identifier, validate_axis, transition_candidate

class KernelFuzzTests(unittest.TestCase):
 def test_deterministic_mutation_corpus(self):
  rng = random.Random(0xBADA02)
  alphabet = string.ascii_letters + string.digits + "_-./: " + "\u00e9\u0000"
  kinds = ["trade_document_id","document_version_id","content_artifact_id","document_relationship_id","document_type"]
  axes = ["lifecycle_state","verification_state","temporal_validity_state","document_family"]
  for index in range(3000):
   value = "".join(rng.choices(alphabet, k=rng.randrange(0,180)))
   kind = kinds[index % len(kinds)]
   axis = axes[index % len(axes)]
   self.assertIsInstance(validate_identifier(kind,value),bool)
   self.assertIsInstance(validate_axis(axis,value),bool)
   self.assertIsInstance(transition_candidate("DRAFT","ISSUED"),bool)
   data = value.encode("utf-8")
   self.assertEqual(sha256_hex(data),hashlib.sha256(data).hexdigest())
 def test_input_limits_and_unknown_fields(self):
  for function,args in (
   (validate_identifier,("trade_document_id","a"*4097)),
   (validate_axis,("document_family","a"*4097)),
   (transition_candidate,("DRAFT","a"*4097)),
   (validate_identifier,("unknown","abc")),
   (validate_axis,("unknown","ISSUED")),
  ):
   with self.assertRaises(ValueError): function(*args)
 def test_binary_mutation(self):
  rng = random.Random(0xA11CE)
  for size in (0,1,2,3,31,32,33,255,256,257,4096,65536):
   data = rng.randbytes(size)
   self.assertEqual(sha256_hex(data),hashlib.sha256(data).hexdigest())
