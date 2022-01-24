import dataclasses
import enum

from typing import Iterator, Optional

from pylox import errors

__all__ = [
    'scan',
    'Scanner',
    'TokenType',
    'Literal',
]


Literal = (int | float | str | bool | None)


class TokenType(enum.Enum):
  # Single character tokens
  LEFT_PAREN = enum.auto()
  RIGHT_PAREN = enum.auto()
  LEFT_BRACE = enum.auto()
  RIGHT_BRACE = enum.auto()
  COMMA = enum.auto()
  DOT = enum.auto()
  MINUS = enum.auto()
  PLUS = enum.auto()
  SEMICOLON = enum.auto()
  SLASH = enum.auto()
  STAR = enum.auto()

  # One or two character tokens
  BANG = enum.auto()
  BANG_EQUAL = enum.auto()
  EQUAL = enum.auto()
  EQUAL_EQUAL = enum.auto()
  GREATER = enum.auto()
  GREATER_EQUAL = enum.auto()
  LESS = enum.auto()
  LESS_EQUAL = enum.auto()

  # Literals
  IDENTIFIER = enum.auto()
  STRING = enum.auto()
  NUMBER = enum.auto()

  # Keywords
  AND = "and"
  CLASS = "class"
  ELSE = "else"
  FALSE = "false"
  FUN = "fun"
  FOR = "for"
  IF = "if"
  NIL = "nil"
  OR = "or"
  PRINT = "print"
  RETURN = "return"
  SUPER = "super"
  THIS = "this"
  TRUE = "true"
  VAR = "var"
  WHILE = "while"
  
  # Miscellaneous
  EOF = enum.auto()


@dataclasses.dataclass(frozen=True)
class Token:
  type: TokenType
  lexeme: str
  literal: Optional[Literal]
  line: int

  def __str__(self):
    if self.literal:
      return f'{self.type.name} {self.lexeme} {self.literal}'
    return f'{self.type.name} {self.lexeme}'


def is_digit(c: str) -> bool:
  return '0' <= c <= '9'


def is_alpha(c: str) -> bool:
  return (c >= 'a' and c <= 'z') or (c > 'A' and c <= 'Z') or c == '_'


def is_alphanumeric(c: str) -> bool:
  return is_alpha(c) or is_digit(c)


@dataclasses.dataclass
class Scanner:
  lox: 'Lox'
  source: str

  def __post_init__(self):
    self.reset()

  def reset(self):
    self.start = 0
    self.current = 0
    self.line = 1

  def is_at_end(self) -> bool:
    return self.current >= len(self.source)

  def _make_token(self,
      token_type: TokenType,
      literal: Optional[Literal] = None) -> Token:
    text = self.source[self.start:self.current]
    return Token(token_type, text, literal, self.line)

  def advance(self) -> str:
    char, self.current = self.source[self.current], self.current + 1
    return char

  def match(self, expected: str) -> bool:
    if self.is_at_end():
      return False
    if self.source[self.current] != expected:
      return False
    self.current += 1
    return True

  def peek(self) -> str:
    if self.is_at_end():
      return '\0'
    return self.source[self.current]

  def peek_next(self) -> str:
    if self.current + 1 >= len(self.source):
      return '\0'
    return self.source[self.current + 1]

  def string(self, quote_char: str) -> Token:
    while self.peek() != quote_char and not self.is_at_end():
      if self.peek() == '\n':
        print('increment here')
        self.line += 1
      self.advance()

    if self.is_at_end():
      self.lox.error(self.line, f'Unterminated string.')
      value = self.source[self.start + 1:self.current]
      return self._make_token(TokenType.STRING, value)

    self.advance()
    value = self.source[self.start + 1:self.current - 1]
    return self._make_token(TokenType.STRING, value)

  def number(self) -> Token:
    while is_digit(self.peek()):
      self.advance()
    if self.peek() == '.' and is_digit(self.peek_next()):
      self.advance()
      while is_digit(self.peek()):
        self.advance()
    return self._make_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

  def identifier(self) -> Token:
    while is_alphanumeric(self.peek()):
      self.advance()
    text = self.source[self.start:self.current]
    try:
      token_type = TokenType(text)
    except ValueError:
      token_type = TokenType.IDENTIFIER
    return self._make_token(token_type)

  def scan_token(self) -> Iterator[Token]:
    c = self.advance()
    match c:
      case '(':
        yield self._make_token(TokenType.LEFT_PAREN)
      case ')':
        yield self._make_token(TokenType.RIGHT_PAREN)
      case '{':
        yield self._make_token(TokenType.LEFT_BRACE)
      case '}':
        yield self._make_token(TokenType.RIGHT_BRACE)
      case ',':
        yield self._make_token(TokenType.COMMA)
      case '.':
        yield self._make_token(TokenType.DOT)
      case '-':
        yield self._make_token(TokenType.MINUS)
      case '+':
        yield self._make_token(TokenType.PLUS)
      case ';':
        yield self._make_token(TokenType.SEMICOLON)
      case '*':
        yield self._make_token(TokenType.STAR)
      case '!':
        if self.match('='):
          yield self._make_token(TokenType.BANG_EQUAL)
          return
        yield self._make_token(TokenType.BANG)
      case '=':
        if self.match('='):
          yield self._make_token(TokenType.EQUAL_EQUAL)
          return
        yield self._make_token(TokenType.EQUAL)
      case '<':
        if self.match('='):
          yield self._make_token(TokenType.LESS_EQUAL)
          return
        yield self._make_token(TokenType.LESS)
      case '>':
        if self.match('='):
          yield self._make_token(TokenType.GREATER_EQUAL)
          return
        yield self._make_token(TokenType.GREATER)
      case '/':
        if self.match('/'):
          while self.peek() != '\n' and not self.is_at_end():
            self.advance()
        else:
          yield self._make_token(TokenType.SLASH)
      case ' ' | '\r' | '\t':
        return
      case '\n':
        self.line += 1
        return
      case '"' | "'":
        yield self.string(c)
      case _:
        if is_digit(c):
          yield self.number()
          return
        elif is_alpha(c):
          yield self.identifier()
          return

  def scan_tokens(self) -> Iterator[Token]:
    while not self.is_at_end():
      self.start = self.current
      yield from self.scan_token()
    yield Token(TokenType.EOF, "", None, self.line)


def scan(lox: 'Lox', source: str) -> Iterator[Token]:
  return Scanner(lox, source).scan_tokens()
