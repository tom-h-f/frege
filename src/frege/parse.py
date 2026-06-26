from dataclasses import dataclass
from enum import Enum, auto

from frege.element import And, Element, IfAndOnlyIf, Implies, Not, Or, Variable
from frege.formula import Formula
from frege.symbol import Symbol
from frege.theory import Theory


class ParseError(ValueError):
    """Raised when an input string is not valid frege syntax."""


class TokenKind(Enum):
    VARIABLE = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    IMPLIES = auto()
    IFF = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEP = auto()
    EOF = auto()

    def symbol(self) -> Symbol | None:
        match self:
            case self.NOT:
                return Symbol.NOT
            case self.AND:
                return Symbol.AND
            case self.OR:
                return Symbol.OR
            case self.IMPLIES:
                return Symbol.IMPLIES
            case self.IFF:
                return Symbol.IFF
        return None

    def as_token(self) -> Token:
        return Token(self, str(self.symbol()))


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str


_SEPARATORS = {";", "\n"}

# Every notation that spells a connective, split by how it is lexed. Symbolic
# notations (`->`, `∧`, `&&`) are punctuation matched greedily mid-stream; word
# notations (`implies`, `and`) are alphanumeric and so are matched as whole
# identifiers, case-insensitively, to avoid swallowing variables. Each TokenKind
# exposes its Symbol's full notation list, so adding a spelling is just data.
_NOTATIONS = [
    (notation, kind)
    for kind in TokenKind
    if (symbol := kind.symbol()) is not None
    for notation in symbol.notations
]
_SYMBOLS = {notation: kind for notation, kind in _NOTATIONS if not notation.isalnum()}
_KEYWORDS = {notation.lower(): kind for notation, kind in _NOTATIONS if notation.isalnum()}
_MAX_SYMBOL_LEN = max(len(notation) for notation in _SYMBOLS)


def _match_symbol(s: str, i: int) -> str | None:
    # Longest match first so `->` wins over a hypothetical `-` and `<=>` over `=>`.
    for length in range(min(_MAX_SYMBOL_LEN, len(s) - i), 0, -1):
        candidate = s[i : i + length]
        if candidate in _SYMBOLS:
            return candidate
    return None


def tokenize(s: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(s):
        char = s[i]
        t = None
        if char in _SEPARATORS:
            t = Token(TokenKind.SEP, char)
            i += 1
        elif char.isspace():
            i += 1
            continue
        elif char == "(":
            t = Token(TokenKind.LPAREN, char)
            i += 1
        elif char == ")":
            t = Token(TokenKind.RPAREN, char)
            i += 1
        elif (symbol := _match_symbol(s, i)) is not None:
            t = _SYMBOLS[symbol].as_token()
            i += len(symbol)
        elif char.isalnum():
            start = i
            while i < len(s) and s[i].isalnum():
                i += 1
            word = s[start:i]
            keyword = _KEYWORDS.get(word.lower())
            t = keyword.as_token() if keyword is not None else Token(TokenKind.VARIABLE, word)

        if t is None:
            raise ParseError(f"unexpected character {char!r}")
        tokens.append(t)

    tokens.append(Token(TokenKind.EOF, ""))
    return tokens


class _Parser:
    """Recursive-descent parser over a flat token list.

    The grammar, loosest-binding rule first. Each rule is one method below; a
    rule calls the next-tighter rule for its operands, so the call chain encodes
    operator precedence (¬ binds tightest, → loosest):

        theory      := formula (SEP formula)*
        formula     := implication
        implication := disjunction (IMPLIES implication)?   # right-associative
        disjunction := conjunction (OR conjunction)*        # left-associative
        conjunction := negation (AND negation)*             # left-associative
        negation    := NOT negation | primary
        primary     := VARIABLE | LPAREN formula RPAREN

    `_pos` indexes the next unconsumed token; `_peek` looks at it without
    consuming, `_advance` consumes and returns it.
    """

    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._pos = 0

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, kind: TokenKind) -> Token:
        token = self._peek()
        if token.kind is not kind:
            raise ParseError(f"expected {kind.name}, got {token.kind.name}")
        return self._advance()

    def theory(self) -> list[Element]:
        roots = [self.formula()]
        while self._peek().kind is TokenKind.SEP:
            self._advance()
            if self._peek().kind is TokenKind.EOF:
                break
            roots.append(self.formula())
        return roots

    def formula(self) -> Element:
        return self._implication()

    def _implication(self) -> Element:
        left = self._disjunction()
        # Right-associative: recurse on _implication so `A → B → C` nests as `A → (B → C)`
        if self._peek().kind is TokenKind.IMPLIES:
            self._advance()
            return Implies(left, self._implication())
        elif self._peek().kind is TokenKind.IFF:
            self._advance()
            return IfAndOnlyIf(left, self._implication())

        return left

    def _disjunction(self) -> Element:
        node = self._conjunction()
        # Left-associative, binds looser than AND and tighter than IMPLIES.
        while self._peek().kind is TokenKind.OR:
            self._advance()
            node = Or(node, self._conjunction())
        return node

    def _conjunction(self) -> Element:
        node = self._negation()
        # Left-associative: loop instead of recursing so `A & B & C` nests as
        # `(A & B) & C`, folding each new operand onto the accumulated node.
        while self._peek().kind is TokenKind.AND:
            self._advance()
            node = And(node, self._negation())
        return node

    def _negation(self) -> Element:
        # Prefix unary operator: recurse on itself so `¬¬A` stacks.
        if self._peek().kind is TokenKind.NOT:
            self._advance()
            return Not(self._negation())
        return self._primary()

    def _primary(self) -> Element:
        # The leaves of the grammar. A parenthesised group re-enters `formula`,
        # so brackets reset precedence back to the loosest level.
        token = self._peek()
        if token.kind is TokenKind.VARIABLE:
            self._advance()
            return Variable(token.value)
        if token.kind is TokenKind.LPAREN:
            self._advance()
            inner = self.formula()
            self._expect(TokenKind.RPAREN)
            return inner
        raise ParseError(f"unexpected {token.kind.name}")

    def expect_end(self) -> None:
        # Called after a complete parse to reject leftover tokens (e.g. `A B`),
        # which otherwise parse the first formula and silently drop the rest.
        if self._peek().kind is not TokenKind.EOF:
            raise ParseError(f"unexpected trailing {self._peek().kind.name}")

    def is_root_node(self, node: Element) -> bool:
        for f in self.theory():
            if f == node:
                return True
        return False


def parse_element(s: str) -> Element:
    parser = _Parser(tokenize(s))
    root = parser.formula()
    parser.expect_end()
    # An Element is a single atom; anything with a connective is a Formula.
    if not isinstance(root, Variable):
        raise ParseError("expected a single element, got a compound formula")
    return root


def parse_formula(s: str) -> Formula:
    parser = _Parser(tokenize(s))
    root = parser.formula()
    parser.expect_end()
    return Formula(root)


def parse_theory(s: str) -> Theory:
    parser = _Parser(tokenize(s))
    roots = parser.theory()
    parser.expect_end()
    return Theory([Formula(root) for root in roots])


def parse(s: str, mode: str | None = None) -> Element | Formula | Theory:
    # Explicit mode forces the return type; an unknown mode is a caller error.
    if mode == "element":
        return parse_element(s)
    if mode == "formula":
        return parse_formula(s)
    if mode == "theory":
        return parse_theory(s)
    if mode is not None:
        raise ParseError(f"unknown mode {mode!r}")

    # Auto-detect: parse the most general shape (a theory), then narrow to the
    # tightest type the input actually warrants - a bare atom collapses to an
    # Element, a lone connective formula to a Formula, the rest stay a Theory.
    parser = _Parser(tokenize(s))
    roots = parser.theory()
    parser.expect_end()
    if len(roots) > 1:
        return Theory([Formula(root) for root in roots])
    root = roots[0]
    if isinstance(root, Variable):
        return root
    return Formula(root)
