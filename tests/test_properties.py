"""Property-based tests: logical laws must hold for every assignment."""

# TODO: use `hypothesis` to evaluate property-based tests like the de morgen laws

# from hypothesis import given
# from hypothesis import strategies as st

# from frege import Var, evaluate

# a, b = Var("A"), Var("B")

# assignments = st.fixed_dictionaries({"A": st.booleans(), "B": st.booleans()})
#
# @given(assignments)
# def test_de_morgan_and(assignment):
#    assert evaluate(~(a & b), assignment) == evaluate(~a | ~b, assignment)


# @given(assignments)
# def test_de_morgan_or(assignment):
#    assert evaluate(~(a | b), assignment) == evaluate(~a & ~b, assignment)
