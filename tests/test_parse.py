import pytest

from frege import (
    And,
    Formula,
    Implies,
    Not,
    ParseError,
    Theory,
    Variable,
    parse,
    parse_element,
    parse_formula,
    parse_theory,
)


def test_auto_atom_returns_element():
    assert parse("A") == Variable("A")


def test_auto_formula():
    result = parse("¬A → B")
    assert result == Formula(Implies(Not(Variable("A")), Variable("B")))


def test_auto_theory():
    result = parse("A → B; B → C")
    assert isinstance(result, Theory)
    assert len(result) == 2


def test_implication_is_right_associative():
    assert parse_formula("A → B → C") == parse_formula("A → (B → C)")


def test_parentheses_override_precedence():
    assert parse_formula("(A → B) → C") == Formula(
        Implies(Implies(Variable("A"), Variable("B")), Variable("C"))
    )


def test_negation_binds_tighter_than_implication():
    assert parse_formula("¬A → B") == Formula(Implies(Not(Variable("A")), Variable("B")))


def test_conjunction_is_left_associative():
    assert parse_formula("A & B & C") == Formula(
        And(And(Variable("A"), Variable("B")), Variable("C"))
    )


def test_conjunction_binds_tighter_than_implication():
    assert parse_formula("A & B → C") == Formula(
        Implies(And(Variable("A"), Variable("B")), Variable("C"))
    )


def test_negation_binds_tighter_than_conjunction():
    assert parse_formula("¬A & B") == Formula(And(Not(Variable("A")), Variable("B")))


def test_mode_theory_on_single_formula():
    result = parse("A → B", mode="theory")
    assert isinstance(result, Theory)
    assert len(result) == 1


def test_mode_element_rejects_compound():
    with pytest.raises(ParseError):
        parse("A → B", mode="element")


def test_parse_element_atom():
    assert parse_element("A") == Variable("A")


def test_theory_trailing_separator_is_ignored():
    assert len(parse_theory("A; B;")) == 2


@pytest.mark.parametrize("bad", ["A &", "→ A", "(", "A →", "A B"])
def test_bad_input_raises(bad):
    with pytest.raises(ParseError):
        parse(bad)
