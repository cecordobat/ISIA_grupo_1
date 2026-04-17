# Workflow - Test Generation

When to use:
Use this workflow when new logic is added, an existing flow changes, a bug is fixed, or CI fails because coverage or regression protection is insufficient.

## Step 1 - Determine what changed

Classify the test need:
- pure calculation logic
- repository behavior
- API endpoint behavior
- liquidation wizard behavior
- accountant review and confirmation flow
- session, login, logout, or protected route behavior

Map the change to the real test locations in this repo:
- `backend/tests/unit/engine/`
- `backend/tests/integration/`
- `frontend/src/pages/`
- frontend component or flow tests already present

## Step 2 - Choose the right test layer

Use backend unit tests when:
- validating IBC, contributions, withholding, invariants, or pure calculation logic

Use backend integration tests when:
- validating auth, profiles, contracts, accountant access, append-only history, repositories, or API routes

Use frontend tests when:
- validating register, login, logout, wizard navigation, guarded routes, profile editing, or visible flow behavior

## Step 3 - Project-specific rules for tests

- Monetary values must use `Decimal` on backend
- CT-01 to CT-04 should remain explicitly protected
- History must remain append-only
- Review and confirmation should be tested separately
- If a PDF rule depends on confirmation, cover that behavior
- If a contador can access only authorized profiles, test authorization boundaries

## Step 4 - Implement tests in the repo structure

Backend examples:
- engine tests in `backend/tests/unit/engine/`
- endpoint and repository tests in `backend/tests/integration/`

Frontend examples:
- end-to-end style flow tests in `frontend/src/pages/AppFlow.test.tsx`
- component-level behavior in relevant page or component test files

## Step 5 - Validate with CI-like commands

Backend lint:
- `python -m ruff check backend/src backend/tests`

Backend tests:
- `python -m pytest backend/tests -v`

Backend coverage:
- run from `backend/`
- `python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=80`

Frontend:
- `npm run test -- --reporter=verbose`
- `npm run build`

## Step 6 - Close the loop

If tests were added because a requirement was missing or unclear, update the related files in `context/`.

If coverage failed in CI, ensure the final local verification reproduces the same command used in `.github/workflows/ci.yml`.
