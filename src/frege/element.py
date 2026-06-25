from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field

from frege.symbol import Symbol

# Binds tighter than any connective, so atoms are never parenthesised.
_ATOM_PRECEDENCE = max(symbol.precedence for symbol in Symbol) + 1


@dataclass(frozen=True)
class Element(ABC):
    # Set when this element is built into a parent's `children()`; the root of a
    # tree keeps `None`. Excluded from equality/hash (so value semantics and set
    # membership are unchanged, and there is no child -> parent -> child
    # recursion) and from repr (so printing only ever descends). Single-valued:
    # an instance reused under two parents records only the last one - the parser
    # never shares instances, so real parse trees are unaffected.
    parent: Element | None = field(default=None, compare=False, repr=False, kw_only=True)

    @abstractmethod
    def symbol(self) -> Symbol | None:
        """The connective symbol for this `Element`, or None for an atom."""

    def children(self) -> tuple[Element, ...]:
        """The direct operands of this element; empty for an atom."""
        return ()

    def precedence(self) -> int:
        symbol = self.symbol()
        return symbol.precedence if symbol is not None else _ATOM_PRECEDENCE

    def __post_init__(self) -> None:
        for child in self.children():
            object.__setattr__(child, "parent", self)

    def ancestors(self) -> Iterator[Element]:
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def root(self) -> Element:
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    @abstractmethod
    def _render(self) -> str:
        """This element's text with no outer parentheses of its own."""

    def _wraps_equal_precedence_child(self, child: Element) -> bool:
        """Whether `child`, an operand of equal precedence, needs parens."""
        return False

    def _needs_parens(self) -> bool:
        parent = self.parent
        if parent is None:
            return False
        if self.precedence() != parent.precedence():
            return self.precedence() < parent.precedence()
        return parent._wraps_equal_precedence_child(self)

    def __str__(self) -> str:
        text = self._render()
        return f"({text})" if self._needs_parens() else text


@dataclass(frozen=True)
class LeftAssociativeElement(Element):
    left: Element
    right: Element

    def children(self) -> tuple[Element, ...]:
        return (self.left, self.right)

    def _wraps_equal_precedence_child(self, child: Element) -> bool:
        return child is self.right

    def _render(self) -> str:
        return f"{self.left} {self.symbol()} {self.right}"


@dataclass(frozen=True)
class RightAssociativeElement(Element):
    left: Element
    right: Element

    def children(self) -> tuple[Element, ...]:
        return (self.left, self.right)

    def _wraps_equal_precedence_child(self, child: Element) -> bool:
        return child is self.left

    def _render(self) -> str:
        return f"{self.left} {self.symbol()} {self.right}"


@dataclass(frozen=True)
class PrefixElement(Element):
    operand: Element

    def children(self) -> tuple[Element, ...]:
        return (self.operand,)

    def _render(self) -> str:
        return f"{self.symbol()}{self.operand}"


@dataclass(frozen=True)
class Variable(Element):
    name: str

    def symbol(self) -> Symbol | None:
        return None

    def _render(self) -> str:
        return self.name


@dataclass(frozen=True)
class Not(PrefixElement):
    operand: Element

    def symbol(self) -> Symbol | None:
        return Symbol.NOT


@dataclass(frozen=True)
class And(LeftAssociativeElement):
    def symbol(self) -> Symbol | None:
        return Symbol.AND


@dataclass(frozen=True)
class Or(LeftAssociativeElement):
    def symbol(self) -> Symbol | None:
        return Symbol.OR


@dataclass(frozen=True)
class Implies(RightAssociativeElement):
    # Antecedent
    left: Element
    # Consequent
    right: Element

    def symbol(self) -> Symbol | None:
        return Symbol.IMPLIES


@dataclass(frozen=True)
class IfAndOnlyIf(RightAssociativeElement):
    # Antecedent
    left: Element
    # Consequent
    right: Element

    def symbol(self) -> Symbol | None:
        return Symbol.IFF
