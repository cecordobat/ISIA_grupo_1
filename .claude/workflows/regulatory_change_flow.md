# Workflow - Regulatory Change

When to use:
Use this workflow when a law, decree, resolution, yearly parameter, or tax table changes.

Examples:
- new SMMLV
- new UVT
- change to withholding table
- change to CIIU presumptive costs
- change to ARL rates
- pension reform impact on contractor flow

## Step 1 - Identify the normative impact

Read and summarize:
- legal source
- effective date
- parameters that change
- whether the change affects only future liquidations

Cross-check with:
- `context/restrictions.md`
- `context/invariantes.md`
- `context/non_functional_requirements.md`

Output:
- concise impact note with affected rules and dates

## Step 2 - Map the change to the current implementation

In this repo, regulatory data currently affects:
- `backend/src/infrastructure/models/snapshot_normativo.py`
- `backend/src/infrastructure/models/tabla_ciiu.py`
- `backend/src/infrastructure/models/tabla_retencion_383.py`
- `backend/src/infrastructure/bootstrap.py`
- repositories that read normative parameters

Important rule:
- historical liquidations must not change
- new values apply only to future calculations
- snapshots used by existing liquidations remain immutable

## Step 3 - Implement without breaking auditability

Preferred behavior:
- add new rows or new vigencies
- do not rewrite historical records
- do not invalidate existing snapshots

If startup seeds are used:
- update seed/bootstrap logic carefully
- ensure it remains deterministic

If a broader admin flow is introduced later:
- keep the same principle of temporal validity and append-only history

## Step 4 - Validate calculations

Must verify:
- IBC floor and ceiling still behave correctly
- contributions still use Decimal-safe math
- withholding uses the correct table for the selected period
- historical liquidations still reproduce prior outputs

Recommended checks:
- `python -m pytest backend/tests -v`
- coverage run if core calculation paths changed

## Step 5 - Update project context

If the regulatory change alters requirements or future scope, update:
- `context/restrictions.md`
- `context/business_rules.md`
- `context/non_functional_requirements.md`
- `context/product_vision.md`
- `context/traceability_matrix.md` if needed

If the change affects future architecture, document that explicitly in context files.
