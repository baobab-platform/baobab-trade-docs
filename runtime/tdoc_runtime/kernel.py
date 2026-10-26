"""Narrow native boundary; startup fails if the Rust wheel is absent."""
from baobab_tdoc_kernel import sha256_hex

def kernel_probe() -> str:
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    actual = sha256_hex(b"abc")
    if actual != expected:
        raise RuntimeError("TDOC Rust kernel integrity probe failed")
    return "rust-pyo3-ok"
