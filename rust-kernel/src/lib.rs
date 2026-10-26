//! HYB-01 native-boundary probe, not a production issuance or policy engine.
//! Input bytes are hashed exactly; domain canonicalisation is a later gate.
use pyo3::prelude::*;
use sha2::{Digest, Sha256};

#[pyfunction]
fn sha256_hex(payload: &[u8]) -> String {
    let result = Sha256::digest(payload);
    result.iter().map(|byte| format!("{byte:02x}")).collect()
}

#[pymodule]
fn baobab_tdoc_kernel(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(sha256_hex, module)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn known_sha256_vector() {
        assert_eq!(sha256_hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }
}
