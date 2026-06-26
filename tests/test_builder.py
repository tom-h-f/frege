import pytest

from frege import Formula, parse_formula
from frege.element import Variable


def test_conj_defaults_left_to_previous():
    assert str(Formula().var("A").conj("B").conj("C")) == "A ∧ B ∧ C"


def test_mixed_connectives_render_minimal_parens():
    assert str(Formula().var("A").conj("B").impl("C")) == "A ∧ B → C"


def test_neg_wraps_previous():
    assert str(Formula().var("A").neg()) == "¬A"


def test_builder_matches_parser():
    assert Formula().var("A").conj("B") == parse_formula("A & B")
    assert Formula().var("A").disj("B") == parse_formula("A || B")
    assert Formula().var("A").iff("B") == parse_formula("A <-> B")


def test_explicit_left_starts_empty_formula():
    assert Formula().conj("B", "A") == parse_formula("A & B")


def test_element_operands_are_accepted():
    assert Formula().conj("B", Variable("A")) == parse_formula("A & B")


def test_conj_without_previous_raises():
    with pytest.raises(ValueError):
        Formula().conj("B")


def test_var_on_non_empty_formula_raises():
    with pytest.raises(ValueError):
        Formula().var("A").var("B")
