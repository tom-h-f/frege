"""Build a propositional formula and print its full truth table.

Run with: uv run python examples/propositional_logic.py
"""

import sys

from frege import parse


def main() -> None:
    expr = sys.argv[1]
    print(parse(expr))


if __name__ == "__main__":
    main()
