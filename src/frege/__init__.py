"""frege: a small library for propositional logic and formal systems."""

from frege.element import (
    And,
    Element,
    Implies,
    Not,
    Or,
    Variable,
)
from frege.formula import Formula
from frege.parse import (
    ParseError,
    parse,
    parse_element,
    parse_formula,
    parse_theory,
)
from frege.symbol import (
    FirstOrderLogicLanguage,
    MetalogicLanguage,
    ModalLogicLanguage,
    PropositionalLogicLanguage,
    Symbol,
)
from frege.theory import Theory

__all__ = [
    "Element",
    "Variable",
    "Not",
    "And",
    "Or",
    "Implies",
    "Formula",
    "Theory",
    "Symbol",
    "PropositionalLogicLanguage",
    "FirstOrderLogicLanguage",
    "ModalLogicLanguage",
    "MetalogicLanguage",
    "parse",
    "parse_element",
    "parse_formula",
    "parse_theory",
    "ParseError",
]
