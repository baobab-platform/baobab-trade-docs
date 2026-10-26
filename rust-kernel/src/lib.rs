//! HYB-02 deterministic, side-effect-free documentary validation kernel.
//! Authority is NEVER inferred from a valid transition: IAM/CP and the Django
//! commit fence remain responsible for permission, freshness and persistence.
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use sha2::{Digest, Sha256};

const MAX_INPUT: usize = 4096;
const STATES: &[&str] = &["DRAFT", "ISSUED", "SUPERSEDED", "VOIDED", "WITHDRAWN", "ARCHIVED"];
const VERIFY: &[&str] = &["UNVERIFIED", "PENDING", "VERIFIED", "FAILED", "DISPUTED", "UNKNOWN"];
const VALIDITY: &[&str] = &["NOT_YET_EFFECTIVE", "CURRENTLY_VALID", "EXPIRED", "REVOKED", "UNKNOWN"];
const FAMILIES: &[&str] = &["TRADE", "TRANSPORT", "CUSTOMS", "REGULATORY", "PROCUREMENT", "FINANCIAL", "INSURANCE", "QUALITY", "WAREHOUSE", "PAYMENT", "CONTRACT", "IDENTITY_SUPPORTING", "OTHER"];

fn bounded(value: &str) -> PyResult<()> {
    if value.len() > MAX_INPUT { Err(PyValueError::new_err("TDOC_INPUT_TOO_LARGE")) } else { Ok(()) }
}
fn deny(code: &'static str) -> PyErr { PyValueError::new_err(code) }
fn check_id(value: &str, prefix: &str, min: usize) -> bool {
    let bytes = value.as_bytes();
    (min..=63).contains(&bytes.len()) && value.starts_with(prefix)
        && bytes[prefix.len()..].iter().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit())
}
fn type_code(value: &str) -> bool {
    let b = value.as_bytes();
    (2..=64).contains(&b.len()) && b[0].is_ascii_uppercase()
        && b[1..].iter().all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || *c == b'_')
}

/// Validate exact Shared trade-document/v2 identifier grammars.
#[pyfunction]
fn validate_identifier(kind: &str, value: &str) -> PyResult<bool> {
    bounded(kind)?; bounded(value)?;
    Ok(match kind {
        "trade_document_id" => check_id(value, "tdoc_", 8),
        "document_version_id" => check_id(value, "tdocv_", 9),
        "content_artifact_id" => check_id(value, "tdoca_", 9),
        "document_relationship_id" => check_id(value, "tdocr_", 9),
        "document_type" => type_code(value),
        _ => return Err(deny("TDOC_UNKNOWN_IDENTIFIER_KIND")),
    })
}

/// Enumerated values are wire-contract exact; no fallback or case normalization.
#[pyfunction]
fn validate_axis(axis: &str, value: &str) -> PyResult<bool> {
    bounded(axis)?; bounded(value)?;
    Ok(match axis {
        "lifecycle_state" => STATES.contains(&value),
        "verification_state" => VERIFY.contains(&value),
        "temporal_validity_state" => VALIDITY.contains(&value),
        "document_family" => FAMILIES.contains(&value),
        _ => return Err(deny("TDOC_UNKNOWN_AXIS")),
    })
}

/// A conservative *candidate* lifecycle guard, not an authorisation decision.
/// This deliberately refuses transitions whose governing documentary policy
/// has not yet been accepted/implemented. Verification/validity are separate.
#[pyfunction]
fn transition_candidate(from: &str, to: &str) -> PyResult<bool> {
    bounded(from)?; bounded(to)?;
    if !STATES.contains(&from) || !STATES.contains(&to) { return Err(deny("TDOC_UNKNOWN_LIFECYCLE_STATE")); }
    Ok(matches!((from, to),
        ("DRAFT", "ISSUED") | ("DRAFT", "VOIDED") |
        ("ISSUED", "SUPERSEDED") | ("ISSUED", "VOIDED") |
        ("ISSUED", "WITHDRAWN") |
        ("SUPERSEDED", "ARCHIVED") | ("VOIDED", "ARCHIVED") |
        ("WITHDRAWN", "ARCHIVED")))
}

/// SHA-256 over EXACT supplied bytes. No implicit JSON normalization, text
/// decoding, unicode NFC conversion or reserialization. Reject oversized FFI.
#[pyfunction]
fn sha256_hex(payload: &[u8]) -> PyResult<String> {
    if payload.len() > 16 * 1024 * 1024 { return Err(deny("TDOC_PAYLOAD_TOO_LARGE")); }
    let result = Sha256::digest(payload);
    Ok(result.iter().map(|byte| format!("{byte:02x}")).collect())
}

#[pymodule]
fn baobab_tdoc_kernel(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(sha256_hex, module)?)?;
    module.add_function(wrap_pyfunction!(validate_identifier, module)?)?;
    module.add_function(wrap_pyfunction!(validate_axis, module)?)?;
    module.add_function(wrap_pyfunction!(transition_candidate, module)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn digest_known_vector() {
        assert_eq!(sha256_hex(b"abc").unwrap(), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }
    #[test]
    fn exact_shared_identifier_edges() {
        for (kind,prefix,min) in [("trade_document_id","tdoc_",8),("document_version_id","tdocv_",9),("content_artifact_id","tdoca_",9),("document_relationship_id","tdocr_",9)] {
            assert!(!validate_identifier(kind,&format!("{}{}",prefix,"a".repeat(min-prefix.len()-1))).unwrap());
            assert!(validate_identifier(kind,&format!("{}{}",prefix,"a".repeat(min-prefix.len()))).unwrap());
            assert!(!validate_identifier(kind,&format!("{}{}",prefix,"a".repeat(64-prefix.len()))).unwrap());
            assert!(!validate_identifier(kind,&format!("{}{}",prefix,"A".repeat(min-prefix.len()))).unwrap());
        }
    }
    #[test]
    fn state_axes_and_transitions() {
        assert!(validate_axis("lifecycle_state","DRAFT").unwrap());
        assert!(!validate_axis("lifecycle_state","VERIFIED").unwrap());
        assert!(validate_axis("verification_state","VERIFIED").unwrap());
        assert!(transition_candidate("DRAFT","ISSUED").unwrap());
        assert!(!transition_candidate("ISSUED","DRAFT").unwrap());
        assert!(!transition_candidate("ISSUED","ISSUED").unwrap());
        assert!(transition_candidate("ISSUED","UNKNOWN").is_err());
    }
    #[test]
    fn deterministic_byte_digests() {
        assert_ne!(sha256_hex(b"\x00").unwrap(), sha256_hex(b"0").unwrap());
        assert_ne!(sha256_hex(b"\xc3\xa9").unwrap(), sha256_hex(b"e\xcc\x81").unwrap());
        assert!(sha256_hex(&vec![0;16*1024*1024+1]).is_err());
    }
}
