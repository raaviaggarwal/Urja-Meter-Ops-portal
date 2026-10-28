# Historical Audit Snapshot — Superseded

This file preserves the purpose of the earlier audit while correcting its
status. Its previous sections A–F described an earlier repository state and
included assertions that are no longer accurate or were not supported by
evidence. Use [README.md](README.md), [docs/PROTOCOL.md](docs/PROTOCOL.md),
[openapi.json](openapi.json), and the current source for the present state.

## Corrected current findings

- **API implementation:** The FastAPI service is implemented in `app.py` and
  reads the local `meter-export.json`. Its routes include health, meter
  listing/search/detail/status/query, nearby search, hierarchy, transformer
  groups, export, and metadata. The previous “zero endpoints implemented”
  statement is obsolete.
- **Local data and live portal counts:** The export contains 403 records.
  The authenticated portal listing was observed to show 403 total. Historical
  notes that report 405 are **unverified historical claims**; the reason for
  that older count is not established.
- **Authentication:** Earlier statements that the login protocol, required
  headers, or session-cookie behavior were verified are **historical and
  unverified**. The user manually signed in for the Phase 2.1 browser
  investigation, but the login submission was not captured. The successful
  login request, authentication mechanism, and session expiry remain unknown.
- **Portal client:** No verified live portal client is implemented. The API
  serves the local export and does not authenticate to or refresh from the
  portal.
- **OpenAPI:** `openapi.json` exists at the repository root, parses as valid
  OpenAPI 3.1 JSON, and contains 10 documented `/api` operations with unique
  operation IDs. `/health` is intentionally excluded from the generated
  schema.
- **Protocol documentation:** The portal evidence is in
  [docs/PROTOCOL.md](docs/PROTOCOL.md). It distinguishes observed live-portal
  behavior from measurements of the local export and leaves unresolved
  behavior explicitly unknown.
- **README and reflection:** The README now links to the protocol and OpenAPI
  files and includes setup, examples, assumptions, trade-offs, omissions,
  improvements, and answers to all five reflection questions in the
  assignment.
- **Tests:** In the recorded regression run, 17 pytest tests passed with a
  temporary runtime-only TestClient compatibility shim. Without the shim,
  pytest collection failed in that environment with
  `TypeError: Client.__init__() got an unexpected keyword argument 'app'`.
  Separate HTTP regression checks covered the primary routes, including
  installed query total 238 and zone filtering for `Z-01`. These results are
  historical validation evidence, not tests run during the documentation
  reconciliation.

## Claims in the superseded audit that should not be relied on

- The earlier count of 405 portal meters and its proposed explanations were
  not confirmed by the later 403-record listing observation.
- Authentication and session details in prior audit notes conflict with the
  captured Phase 2.1 evidence and remain unverified.
- Statements that `openapi.json` or the API implementation were missing
  describe an earlier state and are obsolete.
- Earlier audit lists of files to remove were recommendations at that time;
  the later Phase 7 cleanup has since removed the approved files described
  below.
- The previous assertion that no credentials or session secrets existed in
  tracked or untracked material is not re-certified here. This documentation
  update did not inspect secret values or perform a new secrets audit.
- **Security cleanup status:** In the current worktree, `.env`, the assignment
  PDF, login experiments, tracked Python bytecode, backup/debug outputs, and
  exploratory scripts have been removed from both the working tree and the
  current index. The real `meter-export.json` is intentionally retained
  locally but excluded from the index and ignored by Git.
- **Git history:** These working-tree and index removals do not erase earlier
  commits. The `.env` and assignment PDF remain in reachable history; history
  cleanup has not been performed. Do not publish until historical credential
  exposure and permission to redistribute the real dataset are resolved.
