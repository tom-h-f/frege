from collections.abc import Callable

from frege.element import (
    And,
    Element,
    IfAndOnlyIf,
    Implies,
    Not,
    Or,
    PlaceholderElement,
    Variable,
    _coerce_operand,
    _insert_binary,
    _rightmost,
)
from frege.symbol import Symbol


class Formula:
    _root: Element

    def __init__(self, root: Element | None = None):
        self._adopt(root if root is not None else PlaceholderElement())

    def root(self) -> Element:
        return self._root

    def last(self) -> Element:
        """The rightmost, furthest-descended operand: where the next op attaches."""
        return _rightmost(self._root)

    def elements(self) -> set[Element]:
        return _walk(self._root)

    def _adopt(self, root: Element) -> Element:
        self._root = root
        object.__setattr__(root, "_formula", self)
        return root

    def _binary(
        self,
        kind: Callable[[Element, Element], Element],
        precedence: int,
        right_associative: bool,
        right: Element | str,
        left: Element | str | None,
    ) -> Element:
        if left is not None:
            return self._adopt(kind(_coerce_operand(left), _coerce_operand(right)))
        if isinstance(self._root, PlaceholderElement):
            raise ValueError("no previous element to combine with")
        new_root, created = _insert_binary(
            self._root, kind, precedence, right_associative, _coerce_operand(right)
        )
        self._adopt(new_root)
        object.__setattr__(created, "_formula", self)
        return created

    def var(self, name: str) -> Element:
        if not isinstance(self._root, PlaceholderElement):
            raise ValueError("formula already has a root; nothing to attach a bare variable to")
        return self._adopt(Variable(name))

    def conj(self, right: Element | str, left: Element | str | None = None) -> Element:
        return self._binary(And, Symbol.AND.precedence, False, right, left)

    def disj(self, right: Element | str, left: Element | str | None = None) -> Element:
        return self._binary(Or, Symbol.OR.precedence, False, right, left)

    def implies(self, right: Element | str, left: Element | str | None = None) -> Element:
        return self._binary(Implies, Symbol.IMPLIES.precedence, True, right, left)

    def iff(self, right: Element | str, left: Element | str | None = None) -> Element:
        return self._binary(IfAndOnlyIf, Symbol.IFF.precedence, True, right, left)

    def neg(self, operand: Element | str | None = None) -> Element:
        if operand is not None:
            return self._adopt(Not(_coerce_operand(operand)))
        if isinstance(self._root, PlaceholderElement):
            raise ValueError("no previous element to negate")
        return self._adopt(Not(self._root))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Formula) and self._root == other._root

    def __hash__(self) -> int:
        return hash(self._root)

    def __str__(self) -> str:
        return str(self._root)

    def __repr__(self) -> str:
        return f"Formula({self._root!r})"


def _walk(element: Element) -> set[Element]:
    found: set[Element] = {element}
    for child in element.children():
        found |= _walk(child)
    return found
