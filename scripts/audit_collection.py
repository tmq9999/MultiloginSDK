"""Extract non-secret operation metadata from a local Postman V3 export."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

HOSTS = {'api.multilogin.com': 'cloud', 'launcher.mlx.yt:45001': 'launcher', 'cookies.multilogin.com': 'cookies'}


def audit_collection(source: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: dict[tuple[str, str, str], str] = {}

    def walk(node: dict, group: str = '') -> None:
        for item in node.get('items', []):
            if 'items' in item:
                walk(item, '/'.join(filter(None, [group, item['name']])))
                continue
            raw_url = item['url']
            url = urlsplit(raw_url.replace('{{baseUrl}}', 'https://unresolved.invalid'))
            service = HOSTS.get(url.netloc, 'unresolved')
            path = re.sub(r':([a-zA-Z_]+)', r'{\1}', url.path)
            operation = re.sub(r'[^a-z0-9]+', '_', item['name'].lower()).strip('_')
            key = (service, item['method'], path)
            alias = seen.get(key)
            seen.setdefault(key, item['id'])
            rows.append(dict(request_id=item['id'], name=item['name'], group=group,
                             operation=operation, service=service, method=item['method'], path=path,
                             body_kind=item.get('body', {}).get('type'), read_only=False,
                             status='blocked' if service == 'unresolved' else 'deferred',
                             reason='Unresolved baseUrl' if service == 'unresolved' else 'Not implemented',
                             test_ids=[], alias_of=alias))
    walk(json.loads(source.read_text()))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, default=Path('contracts/operations.json'))
    args = parser.parse_args()
    args.output.write_text(json.dumps(audit_collection(args.source), indent=2) + '\n')
