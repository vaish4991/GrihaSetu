# GrihaSetu AI — updated submission checklist

## Repository update

The original GitLab repository is:

`https://gitlab.com/reshmavaishnavi2006/grihasetu-ai`

From the project folder, run:

```bash
git status
git add .
git commit -m "Expand end-to-end mortgage underwriting demo"
git push
```

If Git reports there is nothing to commit, verify whether the new files are present in the repository and whether the current branch is `main`.

## Files to check in GitLab

- `app.py`
- `core/engine.py`
- `core/integrations.py`
- `core/underwriting.py`
- `core/demo.py`
- `tests/test_engine.py`
- `tests/test_underwriting.py`
- `README.md`
- `DEMO_SCRIPT.md`
- `docs/policy_assumptions.md`
- `GrihaSetu_AI_Solution_Deck.pptx`

## Local quality checks

```bash
python -m py_compile app.py core/*.py
python -m pytest -q
streamlit run app.py
```

Expected automated test result: **11 passed**.

## Final hackathon form

- GitLab Profile: `https://gitlab.com/reshmavaishnavi2006`
- GitLab Submission: `https://gitlab.com/reshmavaishnavi2006/grihasetu-ai`
- Upload the latest `GrihaSetu_AI_Solution_Deck.pptx` separately if the form asks for a deck.
- Add actual team names and actual contributions to the final slide before submitting.

## Important prototype limitations

All external source connectors are synthetic. This app does not access a live credit bureau, bank/account aggregator, KYC/AML service or property registry. It does not verify uploaded documents, use a trained ML model or certify regulatory compliance. Approve/reject/refer outcomes are simulated demo recommendations, not a real lending decision.
