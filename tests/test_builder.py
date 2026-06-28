import pytest

from frege import Formula, parse_formula
from frege.element import And, Implies, Variable


def test_conj_defaults_left_to_previous():
    assert str(Formula().var("A").conj("B").conj("C")) == "A ∧ B ∧ C"


def test_mixed_connectives_render_minimal_parens():
    assert str(Formula().var("A").conj("B").implies("C")) == "A ∧ B → C"


def test_neg_wraps_previous():
    assert str(Formula().var("A").neg()) == "¬A"


def test_builder_matches_parser():
    assert Formula().var("A").conj("B") == parse_formula("A & B").root()
    assert Formula().var("A").disj("B") == parse_formula("A || B").root()
    assert Formula().var("A").iff("B") == parse_formula("A <-> B").root()


def test_explicit_left_starts_empty_formula():
    assert Formula().conj("B", "A") == parse_formula("A & B").root()


def test_element_operands_are_accepted():
    assert Formula().conj("B", Variable("A")) == parse_formula("A & B").root()


def test_conj_without_previous_raises():
    with pytest.raises(ValueError):
        Formula().conj("B")


def test_var_on_non_empty_formula_raises():
    with pytest.raises(ValueError):
        Formula().var("A").var("B")


def test_builder_returns_created_element_class():
    assert isinstance(Formula().var("A"), Variable)
    assert isinstance(Formula().var("A").conj("B"), And)
    assert isinstance(Formula().var("A").implies("B"), Implies)


def test_extends_at_rightmost_operand_by_precedence():
    conjunction = Formula().var("A").implies("B").conj("C")
    assert str(conjunction) == "B ∧ C"
    assert str(conjunction.root()) == "A → B ∧ C"
    assert conjunction.root() == parse_formula("A → (B ∧ C)").root()


def test_extending_keeps_owning_formula_in_sync():
    f = Formula()
    f.var("A").conj("B").conj("C")
    assert str(f) == "A ∧ B ∧ C"


def test_extending_from_last_keeps_formula_in_sync():
    f = Formula()
    f.var("P")
    for name in ("Q", "R", "S"):
        f.last().conj(name)
    assert str(f) == "P ∧ Q ∧ R ∧ S"


def test_last_is_rightmost_operand():
    f = Formula()
    f.var("A").implies("B").conj("C")
    assert f.last() == Variable("C")
