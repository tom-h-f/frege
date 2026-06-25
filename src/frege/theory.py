from frege.formula import Formula


class Theory:
    def __init__(self, formulae: list[Formula] | None = None):
        self._formulae = [] if formulae is None else list(formulae)

    def formulae(self) -> list[Formula]:
        return self._formulae

    def __len__(self) -> int:
        return len(self._formulae)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Theory) and self._formulae == other._formulae

    def __str__(self) -> str:
        return "; ".join(str(formula) for formula in self._formulae)

    def __repr__(self) -> str:
        return f"Theory({self._formulae!r})"
