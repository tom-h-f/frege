from frege.element import And, Element, Implies, Not, Or, Variable


class Formula:
    def __init__(self, root: Element):
        self._root = root

    def root(self) -> Element:
        return self._root

    def elements(self) -> set[Element]:
        return _walk(self._root)

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
    match element:
        case Not(operand):
            found |= _walk(operand)
        case Implies(antecedent, consequent):
            found |= _walk(antecedent) | _walk(consequent)
        case And(left, right) | Or(left, right):
            found |= _walk(left) | _walk(right)
        case Variable():
            pass
    return found
