"""Validate registry integrity; implemented operations require collected pytest IDs."""
import json
import sys
from pathlib import Path


def check_coverage(registry: Path) -> list[str]:
    rows = json.loads(registry.read_text())
    errors: list[str] = []
    ids = [r.get('request_id') for r in rows]
    if len(rows) != 125 or len(set(ids)) != 125:
        errors.append('Expected 125 unique request IDs')
    by_id = {r.get('request_id'): r for r in rows}
    for r in rows:
        name = str(r.get('request_id'))
        if r.get('status') not in {'implemented', 'alias', 'deferred', 'blocked'}:
            errors.append(f'{name}: invalid status')
        if not r.get('reason'):
            errors.append(f'{name}: missing reason')
        if r.get('status') == 'implemented' and (not r.get('test_ids') or r.get('service') == 'unresolved'):
            errors.append(f'{name}: unverified implementation')
        if r.get('status') == 'alias':
            target = by_id.get(r.get('alias_of'), {})
            if target.get('status') != 'implemented' or any(r.get(k) != target.get(k) for k in ['method', 'path', 'service']):
                errors.append(f'{name}: invalid alias')
    return errors


if __name__ == '__main__':
    issues = check_coverage(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('contracts/operations.json'))
    print('\n'.join(issues) if issues else 'PASS: 125 request IDs accounted for')
    sys.exit(bool(issues))
