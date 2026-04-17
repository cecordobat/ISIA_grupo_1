# Workflow - Change Request

When to use:
Use this workflow when a stakeholder requests a change to logic, UX, validation, permissions, audit trail, or an already implemented feature.

## Step 0 - Classify the request

Input:
- Requested change

Decision:
- Regulatory change: follow `regulatory_change_flow.md`
- New feature not present yet: follow `feature_flow.md`
- Bug fix or adjustment to an existing flow: stay in this workflow
- Change to an invariant: stop and escalate because invariants are non-negotiable without architectural approval

## Step 1 - Validate against project context

Review before coding:
- `context/srs_overview.md`
- `context/functional_requirements.md`
- `context/user_stories.md`
- `context/business_rules.md`
- `context/invariantes.md`
- `context/traceability_matrix.md`

Goal:
- Confirm whether the request aligns with RF, RN, CT, RNF, and invariants
- Detect whether it changes the contractor flow, accountant flow, history model, or normative parameters
- Detect whether it closes one of the documented pending gaps: admin parameters, contractor verification, MFA, or historical comparison

Output:
- Short impact note with affected requirements and risks

## Step 2 - Identify affected modules

Typical backend locations:
- `backend/src/api/routers/`
- `backend/src/application/services/`
- `backend/src/infrastructure/repositories/`
- `backend/src/infrastructure/models/`
- `backend/src/api/schemas/`

Typical frontend locations:
- `frontend/src/pages/`
- `frontend/src/components/liquidacion/`
- `frontend/src/api/`
- `frontend/src/store/`

Typical documentation locations:
- `context/`
- `Prompts_Proyecto.md`

Output:
- List of touched files
- Whether the change affects data model, API contract, UI flow, tests, or documentation

## Step 3 - Implement

Implementation rules for this project:
- Respect append-only history for `LiquidacionPeriodo`
- Never mutate historical liquidations
- Keep review and confirmation as separate records
- Preserve the calculation order:
  incomes -> costs -> IBC -> floor decision -> contributions -> withholding -> summary -> history
- Keep monetary calculations on `Decimal`
- Do not hardcode legal parameters that belong in normative tables

## Step 4 - Verify

Backend checks:
- `python -m ruff check backend/src backend/tests`
- `python -m pytest backend/tests -v`

If coverage-sensitive:
- `python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=80` from `backend/`

Frontend checks:
- `npm run test -- --reporter=verbose`
- `npm run build`

## Step 5 - Update project truth

If the change modifies scope, rules, or flow, update:
- `context/` files
- `Prompts_Proyecto.md` if it came from a user prompt worth recording

If the change affects the end-to-end flow, reflect it in:
- contractor flow
- accountant review flow
- administrator flow if introduced
- entidad contratante flow if introduced
- confirmation rules
- PDF generation rule
- historical behavior
