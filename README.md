# frege

A small, typed library for various systems of logic.

## Install

```sh
uv add frege
```

## Quickstart

```python
# TODO
```

Run the bundled example:

```sh
# TODO
uv run python examples/TODO.py
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
## Goals

1. Parsing of logical expressions from 'standard' syntax into a typed representation.
    - Have: `¬` (prefix), `∧` (left-assoc), `→` (right-assoc).
    - Still need `∨` (left-assoc, slots between `∧` and `→`) to complete propositional syntax.
    - `↔` and `⊕` are non-associative: `A ↔ B ↔ C` is ambiguous, so chaining
      should be rejected (parse exactly two operands). This is a new associativity
      case the current precedence-climbing parser does not yet handle.
2. Generation of truth tables from Formulae/Theories
    - For normalization (CNF/DNF) the nested-binary tree for the associative
      `∧`/`∨` becomes awkward; consider flattening to n-ary nodes (`And([...])`).
3. Parsing of latex/mathjax/typst logical expressions
4. Support for various notation forms.
    - Polish/prefix (`Cpq`, `Kpq`) and postfix/RPN have no associativity or
      precedence; they are a separate parse mode, not a new operator level.
      The `mode=` dispatch and `Symbol`-driven tokenizer give a seam for a
      `notation=` axis.
5. Generation of truth trees for viewing the structure of a logical formula or theory.
    a. https://en.wikipedia.org/wiki/Method_of_analytic_tableaux
6. `Syllogism` class
7. Support for Systems of Logic
    a. Aristotelian (see Syllogism impl as prerequisite)
    b. Classical
    c. Propositional
    d. First-Order
        - Quantifiers `∀x. φ`, `∃x. φ` are binders, not binary operators: they
          bind a variable and grab maximal scope to the right. Forces a `Term`
          grammar (predicates `P(x)`, functions `f(g(x))`, application) below the
          `Formula` grammar. This reshapes the type model: `Element` will sit
          alongside a `Term` type.
    e. Modal
        - `□` / `◇` are prefix unary, stackable like `¬`; cheap to add as a new
          method at the same precedence level.
    f. Higher order
        - Adds `λ` binders and left-associative application; builds on the
          first-order `Term` grammar.
    g. Deviant (Intuitionistic, Multi-valued logics, Paraconsistent logics)
8. Computational representations of Model Theory, Proof Theory, Set Theory and Computability Theory.
9. Axiom listing and ability to add/modify/remove them.

