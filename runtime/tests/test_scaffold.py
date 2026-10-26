"""HYB-01 is intentionally non-issuing; probe actual native import and DB."""
from django.db import connection
from django.test import SimpleTestCase
from tdoc_runtime.kernel import kernel_probe

class RustIntegrationTests(SimpleTestCase):
    def test_native_wheel_loaded(self):
        self.assertEqual(kernel_probe(), "rust-pyo3-ok")

class DatabaseBackendTests(SimpleTestCase):
    def test_postgresql_17_is_connected(self):
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            version = int(cursor.fetchone()[0])
        self.assertGreaterEqual(version, 170000)
        self.assertLess(version, 180000)
