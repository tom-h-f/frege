from dataclasses import dataclass
from enum import Enum

# Each language groups the mainstream notations for one logical category. Every
# operation is a list of interchangeable symbols, canonical notation first, so a
# consumer can render with `[0]` and still recognise any of the alternates.


@dataclass
class PropositionalLogicLanguage:
    IMPLIES = ["⇒", "→", "⊃", "->", "=>", "implies"]
    IFF = ["⇔", "↔", "≡", "<->", "<=>", "iff", "if and only if"]
    NOT = ["¬", "~", "!", "′", "not"]
    AND = ["∧", "·", "&", "&&", "/\\", "and"]
    OR = ["∨", "+", "∥", "||", "\\/", "or"]
    XOR = ["⊕", "⊻", "↮", "≢", "^", "xor"]
    NAND = ["↑", "|", "⊼", "nand"]
    NOR = ["↓", "⊽", "nor"]
    TRUE = ["⊤", "T", "1"]
    FALSE = ["⊥", "F", "0"]


@dataclass
class FirstOrderLogicLanguage:
    FOR_ALL = ["∀"]
    EXISTS = ["∃"]
    EXISTS_UNIQUE = ["∃!"]
    DOMAIN_OF_DISCOURSE = ["𝔻"]


@dataclass
class ModalLogicLanguage:
    NECESSARILY = ["□", "◻"]
    POSSIBLY = ["◇", "◊"]


@dataclass
class MetalogicLanguage:
    PROVES = ["⊢"]
    MODELS = ["⊨"]
    NOT_PROVES = ["⊬"]
    NOT_MODELS = ["⊭"]
    EQUIVALENT = ["≡", "⟚", "⇔"]
    THEREFORE = ["∴"]
    BECAUSE = ["∵"]
    DEFINED_AS = ["≔", "≜", "≝", ":="]


class Symbol(Enum):
    """A connective the parser and element tree understand.

    The value is the canonical character used when rendering a formula;
    `notations` is every interchangeable spelling the tokenizer will accept.
    """

    NOT = "¬"
    AND = "∧"
    OR = "∨"
    IMPLIES = "→"
    IFF = "⇔"

    @property
    def notations(self) -> list[str]:
        return _NOTATIONS[self]

    @property
    def precedence(self) -> int:
        """How tightly the operator binds; higher binds tighter than lower."""
        return _PRECEDENCE[self]

    def __str__(self) -> str:
        return self.value


_NOTATIONS = {
    Symbol.NOT: PropositionalLogicLanguage.NOT,
    Symbol.AND: PropositionalLogicLanguage.AND,
    Symbol.OR: PropositionalLogicLanguage.OR,
    Symbol.IMPLIES: PropositionalLogicLanguage.IMPLIES,
    Symbol.IFF: PropositionalLogicLanguage.IFF,
}

_PRECEDENCE = {
    Symbol.NOT: 50,
    Symbol.AND: 40,
    Symbol.OR: 30,
    Symbol.IMPLIES: 2,
    Symbol.IFF: 1,
}
