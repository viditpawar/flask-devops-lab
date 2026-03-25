# Contributing

Thanks for helping improve this project.

This repo is a Flask app plus CI/CD and Azure deployment examples. Good contributions include bug fixes, test improvements, pipeline hardening, and clearer documentation.

## Quick start

```bash
git clone https://github.com/viditpawar/azure-devops-python-cicd.git
cd azure-devops-python-cicd

python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## Development workflow

1. Create a branch from `main`.
2. Make your change in small, focused commits.
3. Run checks locally.
4. Open a pull request with a short explanation.

Example branch names:

- `fix/health-endpoint-timeout`
- `feat/add-azure-login-step`
- `docs/update-deployment-guide`

## Run checks locally

```bash
python -m pytest tests -v
flake8 .
bandit -r .
pip-audit
```

If one of these tools is missing, install it in your virtual environment.

## Pull request expectations

Please include:

- What changed
- Why it changed
- How you tested it
- Any follow-up work needed

Keep PRs narrow when possible. Smaller PRs are easier to review and merge safely.

## Style guidelines

- Follow existing Python style in the repo.
- Add tests for behavior changes.
- Update docs when behavior changes.
- Avoid unrelated refactors in the same PR.

## CI/CD and infra changes

If you change `azure-pipelines.yml`, `.github/workflows/python-devops.yml`, or `infrastructure/*.bicep*`:

- Call out the impact in the PR description.
- Mention required secrets/service connections.
- Include validation steps (or why validation was skipped).

## Reporting issues

Open an issue with:

- Expected behavior
- Actual behavior
- Steps to reproduce
- Logs or screenshots if helpful

## License

By contributing, you agree your contributions are released under the repository license.
