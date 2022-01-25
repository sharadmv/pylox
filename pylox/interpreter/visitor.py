import dataclasses

from typing import Any, Dict, List, Optional

from pylox import errors
from pylox.interpreter import environment
from pylox.parser import ast
from pylox.parser import scanner

Expr = ast.Expr
Assign = ast.Assign
Binary = ast.Binary
Grouping = ast.Grouping
Literal = ast.Literal
Unary = ast.Unary
Variable = ast.Variable
Stmt = ast.Stmt
Block = ast.Block
ExpressionStmt = ast.ExpressionStmt
Print = ast.PrintStmt
VarDecl = ast.VarDecl
Token = scanner.Token
TokenType = scanner.TokenType
Environment = environment.Environment
Value = Any


@dataclasses.dataclass
class Interpreter(ast.NodeVisitor):
  lox: 'Lox'

  def __post_init__(self):
    from pylox.interpreter import callable
    self.globals = Environment()
    self.globals.define('clock', callable.Clock())
    self.env = self.globals
    self.locals: Dict[Expr, int] = {}

  def interpret(self, stmts: List[ast.Stmt]):
    try:
      for statement in stmts:
        self.execute(statement)
    except errors.RuntimeError as e:
      self.lox.runtime_error(e)

  def execute(self, stmt: ast.Stmt):
    stmt.accept(self)

  def execute_block(self, stmts: List[Stmt], env: Environment):
    previous = self.env
    try:
      self.env = env
      for stmt in stmts:
        self.execute(stmt)
    finally:
      self.env = previous

  def stringify(self, value: Value) -> str:
    if value is None:
      return 'nil'
    if isinstance(value, str):
      return value
    if isinstance(value, float):
      value = str(value)
      if value[-2:] == ".0":
        return value[:-2]
      return value
    return str(value)

  def evaluate(self, expr: Expr) -> Value:
    return expr.accept(self)

  def check_number_operand(self, operator: Token, operand: Value):
    if isinstance(operand, float):
      return
    raise errors.RuntimeError(operator, "Operand must be a number.")

  def check_number_operands(self, operator: Token, left: Value, right: Value):
    if isinstance(left, float) and isinstance(right, float):
      return
    raise errors.RuntimeError(operator, "Operands must be numbers.")

  def is_truthy(self, value: Value) -> bool:
    if isinstance(value, bool):
      return value
    if value is None:
      return False
    return True

  def lookup_variable(self, name: Token, expr: Variable) -> Value:
    distance = self.locals.get(expr, None)
    if distance is not None:
      return self.env.get_at(distance, name.lexeme)
    return self.globals.get(name)

  def resolve(self, expr: Expr, depth: int):
    self.locals[expr] = depth

  def visit_assign(self, expr: Assign) -> Value:
    value = self.evaluate(expr.value)
    distance = self.locals[expr]
    if distance is not None:
      self.env.assign_at(distance, expr.name, value)
    else:
      self.globals.assign(expr.name, value)
    return value

  def visit_binary(self, expr: Binary) -> Value:
    left = self.evaluate(expr.left)
    right = self.evaluate(expr.right)
    match expr.operator.type:
      case TokenType.MINUS:
        self.check_number_operands(expr.operator, left, right)
        return left - right
      case TokenType.SLASH:
        self.check_number_operands(expr.operator, left, right)
        return left / right
      case TokenType.PLUS:
        if isinstance(left, float) and isinstance(right, float):
          return left + right
        elif isinstance(left, str) and isinstance(right, str):
          return left + right
        raise errors.RuntimeError(
            expr.operator, "Operands must be numbers or strings.")
      case TokenType.STAR:
        self.check_number_operands(expr.operator, left, right)
        return left * right
      case TokenType.GREATER:
        self.check_number_operands(expr.operator, left, right)
        return left > right
      case TokenType.GREATER_EQUAL:
        self.check_number_operands(expr.operator, left, right)
        return left >= right
      case TokenType.LESS:
        self.check_number_operands(expr.operator, left, right)
        return left < right
      case TokenType.LESS_EQUAL:
        self.check_number_operands(expr.operator, left, right)
        return left <= right
      case TokenType.BANG_EQUAL:
        return left != right
      case TokenType.EQUAL_EQUAL:
        return left == right
      case _:
        return None

  def visit_grouping(self, expr: Grouping) -> Value:
    return self.evaluate(expr.expression)

  def visit_literal(self, expr: Literal) -> Value:
    return expr.value

  def visit_logical(self, expr: ast.Logical) -> Value:
    left = self.evaluate(expr.left)
    if expr.operator.type == TokenType.OR:
      if self.is_truthy(left):
        return left
    else:
      if not self.is_truthy(left):
        return left
    return self.evaluate(expr.right)

  def visit_set(self, expr: ast.Set) -> Value:
    obj = self.evaluate(expr.obj)
    from pylox.interpreter import lox_class
    if not isinstance(obj, lox_class.LoxInstance):
      raise errors.RuntimeError(expr.name, "Only instances have fields.")
    value = self.evaluate(expr.value)
    obj.set(expr.name, value)
    return value

  def visit_this(self, expr: ast.This) -> Value:
    return self.lookup_variable(expr.keyword, expr)

  def visit_unary(self, expr: Unary) -> Value:
    right = self.evaluate(expr.right)
    match expr.operator.type:
      case TokenType.MINUS:
        self.check_number_operand(expr.operator, right)
        return -right
      case TokenType.BANG:
        return not self.is_truthy(right)
      case _:
        return

  def visit_function_decl(self, stmt: ast.FunctionDecl) -> Value:
    from pylox.interpreter import callable
    function = callable.LoxFunction(stmt, self.env, False)
    self.env.define(stmt.name.lexeme, function)
    return

  def visit_call(self, expr: ast.Call) -> Value:
    callee = self.evaluate(expr.callee)
    arguments = []
    for arg in expr.arguments:
      arguments.append(self.evaluate(arg))
    from pylox.interpreter import callable
    if not isinstance(callee, callable.LoxCallable):
      raise errors.RuntimeError(expr.paren, 'Can only call functions and classes.')
    if len(arguments) != callee.arity():
      raise errors.RuntimeError(
          expr.paren, f'Expected {callee.arity()} arguments but got {len(arguments)}.')
    return callee.call(self, arguments)

  def visit_get(self, expr: ast.Get) -> Value:
    from pylox.interpreter import lox_class
    obj = self.evaluate(expr.obj)
    if isinstance(obj, lox_class.LoxInstance):
      return obj.get(expr.name)
    raise errors.RuntimeError(expr.name, 'Only instances have properties.')

  def visit_variable(self, expr: ast.Variable) -> Value:
    return self.lookup_variable(expr.name, expr)

  def visit_if(self, stmt: ast.If) -> Value:
    pred = self.evaluate(stmt.condition)
    if self.is_truthy(pred):
      self.execute(stmt.then_branch)
    elif stmt.else_branch is not None:
      self.execute(stmt.else_branch)
    return None

  def visit_expression_stmt(self, stmt: ExpressionStmt) -> Value:
    self.evaluate(stmt.expression)
    return

  def visit_print_stmt(self, stmt: Print) -> Value:
    value = self.evaluate(stmt.expression)
    print(self.stringify(value))
    return

  def visit_return_stmt(self, stmt: ast.ReturnStmt) -> Value:
    value = None
    if stmt.value is not None:
      value = self.evaluate(stmt.value)
    raise Return(value)

  def visit_while(self, stmt: ast.While) -> Value:
    while self.is_truthy(self.evaluate(stmt.condition)):
      self.execute(stmt.body)

  def visit_block(self, stmt: Block) -> Value:
    return self.execute_block(stmt.statements, Environment(parent=self.env))

  def visit_class(self, stmt: ast.Class) -> Value:
    self.env.define(stmt.name.lexeme, None)
    from pylox.interpreter import lox_class
    from pylox.interpreter import callable
    methods = {}
    for method in stmt.methods:
      func = callable.LoxFunction(method, self.env, method.name.lexeme == 'init')
      methods[method.name.lexeme] = func
    klass = lox_class.LoxClass(stmt.name.lexeme, methods)
    self.env.assign(stmt.name, klass)
    
  def visit_var_decl(self, stmt: VarDecl) -> Value:
    value = None
    if stmt.initializer is not None:
      value = self.evaluate(stmt.initializer)
    self.env.define(stmt.name.lexeme, value)
    return

@dataclasses.dataclass
class Return(Exception):
  value: Optional[Expr]
