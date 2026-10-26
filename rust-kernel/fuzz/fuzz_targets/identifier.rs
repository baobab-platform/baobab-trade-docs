#![no_main]
use libfuzzer_sys::fuzz_target;
use baobab_tdoc_kernel::{check_id, type_code};

fuzz_target!(|data: &[u8]| {
    // Malformed UTF-8 must never cause a panic or an accidental acceptance.
    if let Ok(value) = std::str::from_utf8(data) {
        for (prefix, minimum) in [("tdoc_", 8), ("tdocv_", 9), ("tdoca_", 9), ("tdocr_", 9)] {
            let actual = check_id(value, prefix, minimum);
            let expected = (minimum..=63).contains(&value.len())
                && value.starts_with(prefix)
                && value.as_bytes()[prefix.len()..].iter().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit());
            assert_eq!(actual, expected);
        }
        let bytes = value.as_bytes();
        let expected = (2..=64).contains(&bytes.len())
            && bytes[0].is_ascii_uppercase()
            && bytes[1..].iter().all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || *c == b'_');
        assert_eq!(type_code(value), expected);
    }
});
