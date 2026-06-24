"""Build a propositional formula and print its full truth table.

Run with: uv run python examples/propositional_logic.py
"""

from frege import Var, truth_table, variables


def main() -> None:
    a, b = Var("A"), Var("B")
    formula = (a & ~b) | b

    names = sorted(variables(formula))
    header = "  ".join(names) + "  | " + str(formula)
    print(header)
    print("-" * len(header))
    for assignment, result in truth_table(formula):
        cells = "  ".join("T" if assignment[name] else "F" for name in names)
        print(f"{cells}  | {'T' if result else 'F'}")


if __name__ == "__main__":
    main()
