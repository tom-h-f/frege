from frege.element import And, Implies, Not, Variable
from frege.parse import parse_formula
from frege.symbol import Symbol


def test_variable_str():
    assert str(Variable("A")) == "A"


def test_not_str():
    assert str(Not(Variable("A"))) == "¬A"


def test_implies_str():
    assert str(Implies(Variable("A"), Variable("B"))) == "A → B"


def test_minimal_parens():
    cases = {
        "A & B": "A ∧ B",
        "¬(A & B)": "¬(A ∧ B)",
        "¬A & B": "¬A ∧ B",
        "(A || B) & C": "(A ∨ B) ∧ C",
        "A || B & C": "A ∨ B ∧ C",
        "A → B → C": "A → B → C",
        "(A → B) → C": "(A → B) → C",
        "A & B → C": "A ∧ B → C",
        "¬¬A": "¬¬A",
    }
    for source, expected in cases.items():
        assert str(parse_formula(source)) == expected


def test_value_equality():
    assert Not(Variable("A")) == Not(Variable("A"))
    assert Variable("A") != Variable("B")


def test_symbol():
    assert Variable("A").symbol() is None
    assert Not(Variable("A")).symbol() is Symbol.NOT
    assert Implies(Variable("A"), Variable("B")).symbol() is Symbol.IMPLIES


def test_children_are_linked_to_parent():
    a, b = Variable("A"), Variable("B")
    conjunction = And(a, b)
    assert a.parent is conjunction
    assert b.parent is conjunction
    assert conjunction.parent is None


def test_walk_up_to_root():
    root = parse_formula("A & B → C").root()
    conjunction = root.left
    leaf_a = conjunction.left

    assert root.parent is None
    assert conjunction.parent is root
    assert list(leaf_a.ancestors()) == [conjunction, root]
    assert leaf_a.root() is root


def test_parent_excluded_from_equality_and_hash():
    # Same structure under different parents stays equal and collapses in a set.
    And(Variable("A"), Variable("B"))
    Implies(Variable("A"), Variable("B"))
    assert Not(Variable("A")) == Not(Variable("A"))
    assert len({Not(Variable("A")), Not(Variable("A"))}) == 1
