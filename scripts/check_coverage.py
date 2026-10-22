"""Validate registry integrity; implemented operations require collected pytest IDs."""

import ast
import json
import re
import sys
from pathlib import Path


def check_coverage(registry: Path) -> list[str]:
    rows = json.loads(registry.read_text())
    errors: list[str] = []
    ids = [r.get("request_id") for r in rows]
    if len(rows) != 125 or len(set(ids)) != 125:
        errors.append("Expected 125 unique request IDs")
    audit = (
        Path(__file__).resolve().parents[1]
        / "docs/research/2026-10-22-multilogin-api-audit.md"
    )
    if audit.exists():
        expected = set(re.findall(r"^ID: `([^`]+)`$", audit.read_text(), re.M))
        if set(ids) != expected:
            errors.append("Request IDs differ from reviewed audit")
    by_id = {r.get("request_id"): r for r in rows}
    for r in rows:
        name = str(r.get("request_id"))
        if r.get("status") not in {"implemented", "alias", "deferred", "blocked"}:
            errors.append(f"{name}: invalid status")
        if not r.get("reason"):
            errors.append(f"{name}: missing reason")
        if r.get("status") == "implemented" and (
            not r.get("test_ids") or r.get("service") == "unresolved"
        ):
            errors.append(f"{name}: unverified implementation")
        if r.get("status") == "implemented":
            for test_id in r.get("test_ids", []):
                file_name, _, function_name = test_id.partition("::")
                path = Path(__file__).resolve().parents[1] / file_name
                if not path.is_file():
                    errors.append(f"{name}: missing test file")
                    continue
                definitions = {
                    n.name
                    for n in ast.walk(ast.parse(path.read_text()))
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                if function_name not in definitions:
                    errors.append(f"{name}: missing test function")
        if r.get("status") == "alias":
            target = by_id.get(r.get("alias_of"), {})
            if target.get("status") != "implemented" or any(
                r.get(k) != target.get(k) for k in ["method", "path", "service"]
            ):
                errors.append(f"{name}: invalid alias")
    return errors


if __name__ == "__main__":
    issues = check_coverage(
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path("contracts/operations.json")
    )
    print("\n".join(issues) if issues else "PASS: 125 request IDs accounted for")
    sys.exit(bool(issues))
