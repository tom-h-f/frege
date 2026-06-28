from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from frege.symbol import Symbol

if TYPE_CHECKING:
    from frege.formula import Formula

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

    # The Formula this element is being built into, set as a builder method
    # returns it so further chaining keeps the owning Formula in sync. Excluded
    # from equality/hash/repr for the same reasons as `parent`.
    _formula: Formula | None = field(default=None, compare=False, repr=False, kw_only=True)

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

    def var(self, name: str) -> Element:
        raise ValueError("formula already has a root; nothing to attach a bare variable to")

    def conj(self, right: Element | str) -> Element:
        return self._extend(And, Symbol.AND.precedence, right_associative=False, right=right)

    def disj(self, right: Element | str) -> Element:
        return self._extend(Or, Symbol.OR.precedence, right_associative=False, right=right)

    def implies(self, right: Element | str) -> Element:
        return self._extend(Implies, Symbol.IMPLIES.precedence, right_associative=True, right=right)

    def iff(self, right: Element | str) -> Element:
        return self._extend(IfAndOnlyIf, Symbol.IFF.precedence, right_associative=True, right=right)

    def neg(self) -> Element:
        root = self.root()
        created = Not(self)
        return _commit(root, _replace(root, self, created), created)

    def _extend(
        self,
        kind: Callable[[Element, Element], Element],
        precedence: int,
        *,
        right_associative: bool,
        right: Element | str,
    ) -> Element:
        root = self.root()
        new_root, created = _insert_binary(
            root, kind, precedence, right_associative, _coerce_operand(right)
        )
        return _commit(root, new_root, created)

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
class PlaceholderElement(Element):
    def symbol(self) -> Symbol:
        return Symbol.EMPTY

    def _render(self) -> str:
        return str(self.symbol())


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


def _coerce_operand(value: Element | str) -> Element:
    return value if isinstance(value, Element) else Variable(value)


def _commit(old_root: Element, new_root: Element, created: Element) -> Element:
    """Point the owning Formula (if any) at `new_root`, then return `created`.

    The owner is read off `old_root`, which a Formula always stamps when it
    adopts a tree, so any node in that tree extends back to the same Formula.
    """
    owner = old_root._formula
    if owner is not None:
        owner._adopt(new_root)
        object.__setattr__(created, "_formula", owner)
    return created


def _is_binary(element: Element) -> bool:
    return isinstance(element, (LeftAssociativeElement, RightAssociativeElement))


def _insert_binary(
    root: Element,
    kind: Callable[[Element, Element], Element],
    precedence: int,
    right_associative: bool,
    right: Element,
) -> tuple[Element, Element]:
    """Splice a new binary connective onto the right spine of `root`.

    Descends through any operand that binds looser than the new connective so it
    attaches as deep as its precedence allows: `A → B` then a conjunction yields
    `A → (B ∧ C)`, not `(A → B) ∧ C`. Returns the rebuilt root and the new node.
    """
    target = root
    while _is_binary(target) and (
        target.precedence() < precedence
        or (target.precedence() == precedence and right_associative)
    ):
        target = target.right  # type: ignore[attr-defined]
    created = kind(target, right)
    return _replace(root, target, created), created


def _replace(node: Element, old: Element, new: Element) -> Element:
    if node is old:
        return new
    children = node.children()
    rebuilt = tuple(_replace(child, old, new) for child in children)
    if all(after is before for after, before in zip(rebuilt, children, strict=True)):
        return node
    fields = [field.name for field in dataclasses.fields(node) if field.name not in _META_FIELDS]
    return dataclasses.replace(node, **dict(zip(fields, rebuilt, strict=True)))


def _rightmost(element: Element) -> Element:
    while element.children():
        element = element.children()[-1]
    return element


_META_FIELDS = {"parent", "_formula"}
