"""A tiny propositional-logic core: build formulas, evaluate them, derive truth tables."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

Assignment = dict[str, bool]


class Expr:
    """Base class for propositional formulas."""

    def __or__(self, other: Expr) -> Or:
        return Or(self, other)

    def __and__(self, other: Expr) -> And:
        return And(self, other)

    def __invert__(self) -> Not:
        return Not(self)


@dataclass(frozen=True)
class Var(Expr):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Not(Expr):
    operand: Expr

    def __str__(self) -> str:
        return f"~{self.operand}"


@dataclass(frozen=True)
class And(Expr):
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


@dataclass(frozen=True)
class Or(Expr):
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


def variables(expr: Expr) -> set[str]:
    """Return the set of variable names occurring in ``expr``."""
    match expr:
        case Var(name):
            return {name}
        case Not(operand):
            return variables(operand)
        case And(left, right) | Or(left, right):
            return variables(left) | variables(right)
        case _:
            raise TypeError(f"unknown expression node: {expr!r}")


def evaluate(expr: Expr, assignment: Assignment) -> bool:
    """Evaluate ``expr`` under a mapping of variable name to truth value."""
    match expr:
        case Var(name):
            return assignment[name]
        case Not(operand):
            return not evaluate(operand, assignment)
        case And(left, right):
            return evaluate(left, assignment) and evaluate(right, assignment)
        case Or(left, right):
            return evaluate(left, assignment) or evaluate(right, assignment)
        case _:
            raise TypeError(f"unknown expression node: {expr!r}")


def truth_table(expr: Expr) -> list[tuple[Assignment, bool]]:
    """Return every assignment over ``expr``'s variables paired with its result."""
    names = sorted(variables(expr))
    rows: list[tuple[Assignment, bool]] = []
    for combo in product([False, True], repeat=len(names)):
        assignment = dict(zip(names, combo, strict=True))
        rows.append((assignment, evaluate(expr, assignment)))
    return rows
