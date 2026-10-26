#![no_main]
use baobab_tdoc_kernel::transition_wire;
use libfuzzer_sys::fuzz_target;

const STATES: [&str; 6] = ["DRAFT", "ISSUED", "SUPERSEDED", "VOIDED", "WITHDRAWN", "ARCHIVED"];

fuzz_target!(|data: &[u8]| {
    let cut = data.iter().position(|b| *b == 0).unwrap_or(data.len());
    let (left, right) = data.split_at(cut);
    let right = right.strip_prefix(&[0]).unwrap_or(right);
    if let (Ok(from), Ok(to)) = (std::str::from_utf8(left), std::str::from_utf8(right)) {
        let actual = transition_wire(from, to);
        if !STATES.contains(&from) || !STATES.contains(&to) {
            assert_eq!(actual, None);
        } else {
            let expected = matches!((from, to),
                ("DRAFT", "ISSUED" | "VOIDED") |
                ("ISSUED", "SUPERSEDED" | "VOIDED" | "WITHDRAWN") |
                ("SUPERSEDED" | "VOIDED" | "WITHDRAWN", "ARCHIVED"));
            assert_eq!(actual, Some(expected));
        }
    }
});
