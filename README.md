# frege

A small, typed library for propositional logic and formal systems.

## Install

```sh
uv add frege
```

## Quickstart

```python
from frege import Var, evaluate, truth_table

a, b = Var("A"), Var("B")
formula = (a & ~b) | b          # operators build the expression tree

evaluate(formula, {"A": True, "B": False})   # -> True

for assignment, result in truth_table(formula):
    print(assignment, result)
```

Run the bundled example:

```sh
uv run python examples/propositional_logic.py
```

## Development

All tasks run through plain `uv` commands:

```sh
uv sync                          # install the project + dev dependencies
uv run pytest                    # run tests with coverage
uv run ruff check .              # lint
uv run ruff format .             # format (use --check in CI)
uv run ty check                  # type check
uv run python examples/propositional_logic.py
```

Drop throwaway scripts in `playground/` (git-ignored) to experiment.

## Releasing

Releases publish to PyPI via GitHub Actions trusted publishing (OIDC, no tokens):

```sh
# bump version in pyproject.toml, commit, then:
git tag v0.1.0
git push origin v0.1.0
```

The tag triggers `.github/workflows/release.yml`, which builds and uploads to PyPI.
A one-time PyPI *pending publisher* must be configured first: at
<https://pypi.org/manage/account/publishing> add project `frege`, owner `tom-h-f`,
repository `frege`, workflow `release.yml`, environment `pypi`.
