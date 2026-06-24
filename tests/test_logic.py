from frege import And, Not, Or, Var, evaluate, truth_table, variables


def test_variables_collects_names():
    expr = (Var("A") & ~Var("B")) | Var("C")
    assert variables(expr) == {"A", "B", "C"}


def test_evaluate_basic():
    a, b = Var("A"), Var("B")
    assert evaluate(a & b, {"A": True, "B": True}) is True
    assert evaluate(a & b, {"A": True, "B": False}) is False
    assert evaluate(a | b, {"A": False, "B": True}) is True
    assert evaluate(~a, {"A": False}) is True


def test_operator_overloads_build_nodes():
    a, b = Var("A"), Var("B")
    assert a & b == And(a, b)
    assert a | b == Or(a, b)
    assert ~a == Not(a)


def test_truth_table_covers_all_rows():
    table = truth_table(Var("A") | Var("B"))
    assert len(table) == 4
    results = {tuple(sorted(assign.items())): value for assign, value in table}
    assert results[(("A", False), ("B", False))] is False
    assert results[(("A", True), ("B", False))] is True


def test_str_renders_formula():
    assert str(Var("A") & ~Var("B")) == "(A & ~B)"
