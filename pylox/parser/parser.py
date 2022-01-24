import dataclasses

from typing import List, Optional

from pylox.parser import ast
from pylox.parser import scanner

Token = scanner.Token
TokenType = scanner.TokenType


class ParseError(Exception):
  pass


@dataclasses.dataclass
class Parser:
  lox: 'Lox'
  tokens: List[Token]

  def __post_init__(self):
    self.current: int = 0

  def peek(self) -> Token:
    return self.tokens[self.current]

  def is_at_end(self) -> bool:
    return self.peek().type == TokenType.EOF

  def previous(self) -> Token:
    return self.tokens[self.current - 1]

  def advance(self) -> Token:
    if not self.is_at_end():
      self.current += 1
    return self.previous()

  def check(self, type: TokenType) -> bool:
    if self.is_at_end():
      return False
    return self.peek().type == type

  def match(self, *types: TokenType):
    for type in types:
      if self.check(type):
        self.advance()
        return True
    return False

  def error(self, token: Token, message: str):
    self.lox.token_error(token, message)
    return ParseError()

  def synchronize(self):
    self.advance()
    while not self.is_at_end():
      if self.previous().type == TokenType.SEMICOLON:
        return
      match self.peek().type:
        case (TokenType.CLASS | TokenType.FUN | TokenType.IF | TokenType.PRINT |
              TokenType.RETURN | TokenType.VAR | TokenType.WHILE):
          return
        case _:
          pass
      self.advance()

  def consume(self, type: TokenType, message: str) -> Token:
    if self.check(type):
      return self.advance()
    raise self.error(self.peek(), message)

  def parse(self) -> List[ast.Stmt]:
    statements = []
    while not self.is_at_end():
      statements.append(self.declaration())
    return statements

  def declaration(self) -> Optional[ast.Stmt]:
    try:
      if self.match(TokenType.FUN):
        return self.function('function')
      if self.match(TokenType.VAR):
        return self.var_declaration()
      return self.statement()
    except ParseError:
      self.synchronize()
      return

  def function(self, kind: str):
    name = self.consume(TokenType.IDENTIFIER, f'Expect {kind} name.')
    self.consume(TokenType.LEFT_PAREN, f'Expect \'(\' after {kind} name.')
    parameters = []
    if not self.check(TokenType.RIGHT_PAREN):
      parameters.append(self.consume(
        TokenType.IDENTIFIER, 'Expect parameter name.'))
      while self.match(TokenType.COMMA):
        parameters.append(self.consume(
          TokenType.IDENTIFIER, 'Expect parameter name.'))
        if len(parameters) >= 255:
          self.error(self.peek(), 'Can\'t have more than 255 parameters.')
    self.consume(TokenType.RIGHT_PAREN, 'Expect \')\' after parameters.')
    self.consume(TokenType.LEFT_BRACE, f'Expect \'{{\' before {kind} body.')
    body = self.block()
    return ast.FunctionDecl(name, parameters, body)

  def var_declaration(self) -> ast.VarDecl:
    name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
    initializer = None
    if self.match(TokenType.EQUAL):
      initializer = self.expression()
    self.consume(TokenType.SEMICOLON, 'Expect \';\' after value.')
    return ast.VarDecl(name, initializer)

  def statement(self) -> ast.Stmt:
    if self.match(TokenType.FOR):
      return self.for_statement()
    if self.match(TokenType.IF):
      return self.if_statement()
    if self.match(TokenType.PRINT):
      return self.print_statement()
    if self.match(TokenType.RETURN):
      return self.return_statement()
    if self.match(TokenType.WHILE):
      return self.while_statement()
    if self.match(TokenType.LEFT_BRACE):
      return ast.Block(self.block())
    return self.expression_statement()

  def for_statement(self) -> ast.Stmt:
    self.consume(TokenType.LEFT_PAREN, 'Expect \'(\' after `for`.')
    initializer = None
    if self.match(TokenType.SEMICOLON):
      pass
    elif self.match(TokenType.VAR):
      initializer = self.var_declaration()
    else:
      initializer = self.expression_statement()
    condition = None
    if not self.check(TokenType.SEMICOLON):
      condition = self.expression()
    self.consume(TokenType.SEMICOLON, 'Expect \';\' after loop condition.')
    increment = None
    if not self.check(TokenType.RIGHT_BRACE):
      increment = self.expression()
    self.consume(TokenType.RIGHT_PAREN, 'Expect \')\' after for clauses.')
    body = self.statement()
    if increment is not None:
      body = ast.Block([body, ast.ExpressionStmt(increment)])
    if condition is None:
      condition = ast.Literal(True)
    body = ast.While(condition, body)
    if initializer is not None:
      body = ast.Block([initializer, body])
    return body

  def if_statement(self) -> ast.If:
    self.consume(TokenType.LEFT_PAREN, 'Expect \'(\' after `if`.')
    condition = self.expression()
    self.consume(TokenType.RIGHT_PAREN, 'Expect \')\' after `if` condition.')
    then_branch = self.statement()
    else_branch = None
    if self.match(TokenType.ELSE):
      else_branch = self.statement()
    return ast.If(condition, then_branch, else_branch)

  def block(self) -> List[ast.Stmt]:
    statements = []
    while not (self.check(TokenType.RIGHT_BRACE) or self.is_at_end()):
      statements.append(self.declaration())
    self.consume(TokenType.RIGHT_BRACE, 'Expect \'}\' after block.')
    return statements

  def print_statement(self) -> ast.PrintStmt:
    value = self.expression()
    self.consume(TokenType.SEMICOLON, 'Expect \';\' after value.')
    return ast.PrintStmt(value)

  def return_statement(self) -> ast.ReturnStmt:
    keyword = self.previous()
    value = None
    if not self.check(TokenType.SEMICOLON):
      value = self.expression()
    self.consume(TokenType.SEMICOLON, 'Expect \';\' after return value.')
    return ast.ReturnStmt(keyword, value)

  def while_statement(self) -> ast.While:
    self.consume(TokenType.LEFT_PAREN, 'Expect \'(\' after `while`.')
    condition = self.expression()
    self.consume(TokenType.RIGHT_PAREN, 'Expect \')\' after `while` condition.')
    body = self.statement()
    return ast.While(condition, body)

  def expression_statement(self) -> ast.ExpressionStmt:
    value = self.expression()
    self.consume(TokenType.SEMICOLON, 'Expect \';\' after value.')
    return ast.ExpressionStmt(value)

  def expression(self) -> ast.Expr:
    return self.assignment()

  def assignment(self) -> ast.Expr:
    expr = self.or_()
    if self.match(TokenType.EQUAL):
      equals = self.previous()
      value = self.assignment()
      if isinstance(expr, ast.Variable):
        name = expr.name
        return ast.Assign(name, value)
      self.error(equals, "Invalid assignment target.")
    return expr

  def or_(self) -> ast.Expr:
    expr = self.and_()
    while self.match(TokenType.OR):
      operator = self.previous()
      right = self.and_()
      expr = ast.Logical(expr, operator, right)
    return expr

  def and_(self) -> ast.Expr:
    expr = self.equality()
    while self.match(TokenType.AND):
      operator = self.previous()
      right = self.equality()
      expr = ast.Logical(expr, operator, right)
    return expr

  def equality(self) -> ast.Expr:
    expr = self.comparison()
    while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
      operator = self.previous()
      right = self.comparison()
      expr = ast.Binary(expr, operator, right)
    return expr

  def comparison(self) -> ast.Expr:
    expr = self.term()
    while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS,
        TokenType.LESS_EQUAL):
      operator = self.previous()
      right = self.term()
      expr = ast.Binary(expr, operator, right)
    return expr

  def term(self) -> ast.Expr:
    expr = self.factor()
    while self.match(TokenType.PLUS, TokenType.MINUS):
      operator = self.previous()
      right = self.factor()
      expr = ast.Binary(expr, operator, right)
    return expr

  def factor(self) -> ast.Expr:
    expr = self.unary()
    while self.match(TokenType.SLASH, TokenType.STAR):
      operator = self.previous()
      right = self.unary()
      expr = ast.Binary(expr, operator, right)
    return expr

  def unary(self) -> ast.Expr:
    if self.match(TokenType.BANG, TokenType.MINUS):
      operator = self.previous()
      right = self.unary()
      return ast.Unary(operator, right)
    return self.call()

  def call(self) -> ast.Expr:
    expr = self.primary()
    while True:
      if self.match(TokenType.LEFT_PAREN):
        expr = self.finish_call(expr)
      else:
        break
    return expr
  
  def finish_call(self, expr: ast.Expr) -> ast.Call:
    arguments = []
    if not self.check(TokenType.RIGHT_PAREN):
      arguments.append(self.expression())
      while self.match(TokenType.COMMA):
        if len(arguments) >= 255:
          self.error(self.peek(), 'Can\'t have more than 255 arguments.')
        arguments.append(self.expression())
    paren = self.consume(TokenType.RIGHT_PAREN, 'Expect \')\' after arguments.')
    return ast.Call(expr, paren, arguments)

  def primary(self) -> ast.Expr:
    if self.match(TokenType.FALSE):
      return ast.Literal(False)
    if self.match(TokenType.TRUE):
      return ast.Literal(True)
    if self.match(TokenType.NIL):
      return ast.Literal(None)
    if self.match(TokenType.NUMBER, TokenType.STRING):
      return ast.Literal(self.previous().literal)
    if self.match(TokenType.IDENTIFIER):
      return ast.Variable(self.previous())
    if self.match(TokenType.LEFT_PAREN):
      expr = self.expression()
      self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
      return ast.Grouping(expr)
    raise self.error(self.peek(), 'Expect expression.')


def parse(lox: 'Lox', source_string: str) -> List[ast.Stmt]:
  parser = Parser(lox, list(scanner.scan(lox, source_string)))
  return parser.parse()
