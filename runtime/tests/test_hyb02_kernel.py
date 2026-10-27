"""Independent Python reference vectors for Shared trade-document/v2 (HYB-02)."""
import hashlib
import re
import unittest
from baobab_tdoc_kernel import sha256_hex, validate_identifier, validate_axis, transition_candidate

PATTERNS = {
 "trade_document_id": (r"tdoc_[a-z0-9]+", 8, 63),
 "document_version_id": (r"tdocv_[a-z0-9]+", 9, 63),
 "content_artifact_id": (r"tdoca_[a-z0-9]+", 9, 63),
 "document_relationship_id": (r"tdocr_[a-z0-9]+", 9, 63),
 "document_type": (r"[A-Z][A-Z0-9_]{1,63}", 2, 64),
}
AXES = {
 "lifecycle_state": {"DRAFT","ISSUED","SUPERSEDED","VOIDED","WITHDRAWN","ARCHIVED"},
 "verification_state": {"UNVERIFIED","PENDING","VERIFIED","FAILED","DISPUTED","UNKNOWN"},
 "temporal_validity_state": {"NOT_YET_EFFECTIVE","CURRENTLY_VALID","EXPIRED","REVOKED","UNKNOWN"},
 "document_family": {"TRADE","TRANSPORT","CUSTOMS","REGULATORY","PROCUREMENT","FINANCIAL","INSURANCE","QUALITY","WAREHOUSE","PAYMENT","CONTRACT","IDENTITY_SUPPORTING","OTHER"},
}
class KernelDifferentialTests(unittest.TestCase):
 def test_identifiers(self):
  values = ["", "tdoc_abc", "tdocv_abc", "tdoca_abc", "tdocr_abc", "tdoc_A", "tdoc_0", "tdoc_", "INVOICE", "A_", "A", "a_", "A"*65, "tdoc_"+"a"*59, "tdoc_"+"a"*58, "é"]
  for kind, (pattern, minimum, maximum) in PATTERNS.items():
   for value in values:
    with self.subTest(kind=kind, value=value[:20]):
     expected = minimum <= len(value.encode()) <= maximum and re.fullmatch(pattern, value, flags=re.ASCII) is not None
     self.assertEqual(validate_identifier(kind,value), expected)
 def test_axes(self):
  values = set().union(*AXES.values()) | {"", "ISSUE", "issued", "UNKNOWN ", "é"}
  for axis, allowed in AXES.items():
   for value in values:
    with self.subTest(axis=axis, value=value):
     self.assertEqual(validate_axis(axis,value), value in allowed)
 def test_denial(self):
  with self.assertRaises(ValueError): validate_identifier("tenant_id","tdoc_abc")
  with self.assertRaises(ValueError): validate_axis("authority","ISSUED")
  with self.assertRaises(ValueError): transition_candidate("UNKNOWN","ISSUED")
 def test_exact_bytes(self):
  for payload in (b"", b"abc", b"0", bytes(range(256)), "é".encode(), "e\u0301".encode()):
   self.assertEqual(sha256_hex(payload), hashlib.sha256(payload).hexdigest())
 def test_transitions_not_authority(self):
  self.assertTrue(transition_candidate("DRAFT","ISSUED"))
  self.assertFalse(transition_candidate("ISSUED","DRAFT"))
  self.assertFalse(transition_candidate("ARCHIVED","ISSUED"))
