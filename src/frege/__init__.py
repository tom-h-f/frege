"""frege: a small library for propositional logic and formal systems."""

from frege.logic import (
    And,
    Assignment,
    Expr,
    Not,
    Or,
    Var,
    evaluate,
    truth_table,
    variables,
)

__all__ = [
    "And",
    "Assignment",
    "Expr",
    "Not",
    "Or",
    "Var",
    "evaluate",
    "truth_table",
    "variables",
]
