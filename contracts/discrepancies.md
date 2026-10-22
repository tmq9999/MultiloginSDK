# Contract discrepancies

Evidence: Postman collection export and audit dated 2026-10-22; no live Multilogin calls.

| Issue | Status | Evidence / treatment |
|---|---|---|
| 8 requests use baseUrl | open | 2026-10-23 CLI globals var get baseUrl reports variable absent. Endpoint paths independently match published vendor reference; resolve through vendor documentation before implementing affected folders. |
| Cloud to Local points to local_to_cloud | blocked | Both exported URL paths identical; defer both direction helpers. |
| Mobile import confirm absent | blocked | Validate description references confirm, but no matching request ID. Do not invent it. |
| HTTP vs envelope status | resolved for parser | Saved signin/refresh/folders/core examples: HTTP500 with envelope200. Runtime HTTP status wins; keep negative fixtures. |
| Quick v3 canvas_noise: typo | resolved for serializer | Request body has trailing colon, but same request's description required-fields block names canvas_noise. Profile Metas response independently uses canvas_noise. Use explicit canvas_noise field; reject canvas_noise:. |
| Browser Core List GET body/query ambiguous | blocked | Both present in export; defer operation. |
| Object response placeholders | blocked | Many examples status.http_code=0 and data placeholders; defer models. |
| Rate limit values absent | open | No reliable quota in collection; no hard-coded rate quota. |
