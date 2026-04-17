# Workflow - New Feature

When to use:
Use this workflow for a capability that is not yet implemented in the product.

## Step 1 - Define the feature in project language

Read:
- `context/product_vision.md`
- `context/functional_requirements.md`
- `context/user_stories.md`
- `context/actors_and_processes.md`
- `context/traceability_matrix.md`

Create a brief internal feature note that states:
- user problem
- target actor
- related RF, HU, RN, CT, RNF
- expected UI and API impact

## Step 2 - Fit it into the real product flow

For this project, every feature should be placed in one of these areas:
- authentication and role entry
- contractor profile
- contracts
- liquidation wizard
- floor protection decision
- accountant review
- contractor confirmation
- PDF generation
- historical audit trail
- normative parameter management
- contractor compliance verification
- historical comparison
- MFA for accountant access

If it does not fit any of them, validate whether it is really in scope.

Priority future workstreams already recognized by project context:
- administrator-managed normative parameters
- contractor compliance verification for third parties
- accountant MFA
- historical comparison between periods

## Step 3 - Design implementation

Backend design should identify:
- router updates in `backend/src/api/routers/`
- schema updates in `backend/src/api/schemas/`
- repository or model updates in `backend/src/infrastructure/`
- service updates in `backend/src/application/services/`

Frontend design should identify:
- page updates in `frontend/src/pages/`
- components in `frontend/src/components/liquidacion/`
- API client updates in `frontend/src/api/`
- state changes in `frontend/src/store/`

Also decide:
- Does it affect append-only history?
- Does it affect accountant authorization?
- Does it affect confirmation before PDF?
- Does it introduce or depend on a new actor such as administrator or entidad contratante?
- Does it require new tests?

## Step 4 - Implement incrementally

Recommended order:
1. backend model and API
2. frontend API bindings
3. UI and state
4. tests
5. context documentation

## Step 5 - Validate with repo-native checks

Backend:
- `python -m ruff check backend/src backend/tests`
- `python -m pytest backend/tests -v`

Frontend:
- `npm run test -- --reporter=verbose`
- `npm run build`

Use coverage validation when the feature meaningfully changes backend logic.

## Step 6 - Update context

If the feature changes product behavior, update the relevant files in `context/`, especially:
- `functional_requirements.md`
- `user_stories.md`
- `actors_and_processes.md`
- `data_model.md`
- `diagramas.md`
- `traceability_matrix.md`
