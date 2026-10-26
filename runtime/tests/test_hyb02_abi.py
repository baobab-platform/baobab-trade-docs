"""HYB-02 Python 3.14 native ABI smoke test; CI must run per target platform."""
import importlib.machinery
import platform
import sys
import unittest
import baobab_tdoc_kernel as kernel

class NativeAbiTests(unittest.TestCase):
 def test_supported_cpython_314_only(self):
  self.assertEqual(sys.implementation.name, "cpython")
  self.assertEqual(sys.version_info[:2], (3,14))
  self.assertIn(platform.machine().lower(), {"x86_64","aarch64","amd64","arm64"})
  native_functions = [kernel.sha256_hex, kernel.validate_identifier, kernel.validate_axis, kernel.transition_candidate]
  self.assertTrue(all(callable(fn) for fn in native_functions))
  native_modules = {getattr(fn, "__module__", "") for fn in native_functions}
  self.assertTrue(native_modules, "Native PyO3 exports must be present")
  import importlib
  self.assertTrue(any(any(str(getattr(importlib.import_module(name), "__file__", "")).endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES) for name in native_modules), native_modules)
 def test_no_unqualified_free_threaded_mode(self):
  self.assertFalse(getattr(sys, "_is_gil_enabled", lambda: True)() is False, "free-threaded Python needs independent qualification")
 def test_exports(self):
  for symbol in ("sha256_hex","validate_identifier","validate_axis","transition_candidate"):
   self.assertTrue(callable(getattr(kernel,symbol)))
