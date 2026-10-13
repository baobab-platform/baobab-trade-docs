"""Run from an unrelated directory with only the installed reference wheel.

No repository imports, Shared checkout, credentials, issuer or database required.
Original bytes/inventory and executable negative validators must survive packaging.
"""
import hashlib
import json
import sys
from importlib.resources import files
from pathlib import Path

from reference import legal_actor_issuance
from reference.shared_contracts import PROVENANCE, ContractViolation, validate_contract

root = files("reference.shared_contracts").joinpath("data")
def inventory(node, prefix=""):
    found = set()
    for item in node.iterdir():
        path = prefix + item.name
        if item.is_dir():
            found.update(inventory(item, path + "/"))
        else:
            found.add(path)
    return found
assert inventory(root) == set(PROVENANCE["files"]) | {"provenance.json"}
assert Path(legal_actor_issuance.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), "source tree imported instead of installed wheel"
for path, digest in PROVENANCE["files"].items():
    assert hashlib.sha256(root.joinpath(path).read_bytes()).hexdigest() == digest
cases = json.loads(Path(sys.argv[1]).read_bytes())
for case in cases:
    try:
        validate_contract(case["contract"], case["instance"])
        accepted = True
    except ContractViolation:
        accepted = False
    assert accepted == case["valid"], case["name"]
print(f"Installed reference wheel verified: {len(PROVENANCE['files'])} files, {len(cases)} wire cases")
