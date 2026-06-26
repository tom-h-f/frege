from frege.element import (
    And,
    Element,
    IfAndOnlyIf,
    Implies,
    Not,
    Or,
    PlaceholderElement,
    Variable,
)


def _coerce_operand(value: Element | str) -> Element:
    return value if isinstance(value, Element) else Variable(value)


class Formula:
    _root: Element

    def __init__(self, root: Element | None = None):
        self._root = root if root is not None else PlaceholderElement()

    def root(self) -> Element:
        return self._root

    def elements(self) -> set[Element]:
        return _walk(self._root)

    def _previous(self) -> Element:
        if isinstance(self._root, PlaceholderElement):
            raise ValueError("no previous element to combine with")
        return self._root

    def _binary(
        self,
        kind: type[Element],
        right: Element | str,
        left: Element | str | None,
    ) -> Formula:
        left_el = _coerce_operand(left) if left is not None else self._previous()
        self._root = kind(left_el, _coerce_operand(right))
        return self

    def var(self, name: str) -> Formula:
        if not isinstance(self._root, PlaceholderElement):
            raise ValueError("formula already has a root; nothing to attach a bare variable to")
        self._root = Variable(name)
        return self

    def conj(self, right: Element | str, left: Element | str | None = None) -> Formula:
        return self._binary(And, right, left)

    def disj(self, right: Element | str, left: Element | str | None = None) -> Formula:
        return self._binary(Or, right, left)

    def implies(self, right: Element | str, left: Element | str | None = None) -> Formula:
        return self._binary(Implies, right, left)

    def iff(self, right: Element | str, left: Element | str | None = None) -> Formula:
        return self._binary(IfAndOnlyIf, right, left)

    def neg(self, operand: Element | str | None = None) -> Formula:
        target = _coerce_operand(operand) if operand is not None else self._previous()
        self._root = Not(target)
        return self

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
