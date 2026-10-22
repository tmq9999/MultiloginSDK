import json

from scripts.audit_collection import audit_collection
from scripts.check_coverage import check_coverage


def test_recursive_registry(tmp_path):
    p = tmp_path / "collection.json"
    p.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "name": "ADB",
                        "items": [
                            {
                                "id": "a",
                                "name": "info",
                                "method": "POST",
                                "url": "https://api.multilogin.com/info",
                                "headers": [
                                    {"key": "Authorization", "value": "secret"}
                                ],
                            },
                            {
                                "id": "b",
                                "name": "again",
                                "method": "POST",
                                "url": "https://api.multilogin.com/info",
                            },
                        ],
                    }
                ]
            }
        )
    )
    rows = audit_collection(p)
    assert [r["request_id"] for r in rows] == ["a", "b"]
    assert rows[0]["service"] == "cloud"
    assert "secret" not in json.dumps(rows)
    assert rows[1]["alias_of"] == "a"


def test_missing_duplicate_and_wrong_alias(tmp_path):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps([{"request_id": "x"}, {"request_id": "x"}]))
    assert check_coverage(p)


def test_full_registry():
    from pathlib import Path

    rows = json.loads(Path("contracts/operations.json").read_text())
    assert len(rows) == len({r["request_id"] for r in rows}) == 125
    assert check_coverage(Path("contracts/operations.json")) == []


def test_implemented_test_id_must_exist(tmp_path):
    from pathlib import Path

    rows = json.loads(Path("contracts/operations.json").read_text())
    rows[0].update(
        status="implemented",
        test_ids=["tests/contract/test_access.py::test_does_not_exist"],
    )
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(rows))
    assert any("test" in issue.lower() for issue in check_coverage(p))
