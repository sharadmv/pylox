import contextlib
import dataclasses
import enum

from typing import Any, Dict, Generator, List

from pylox.parser import ast
from pylox.parser import scanner
from pylox.interpreter import visitor

Interpreter = visitor.Interpreter
Token = scanner.Token


class FunctionType(enum.Enum):
  NONE = enum.auto()
  FUNCTION = enum.auto()
  METHOD = enum.auto()
  INITIALIZER = enum.auto()


class ClassType(enum.Enum):
  NONE = enum.auto()
  CLASS = enum.auto()


@dataclasses.dataclass
class VariableResolver(ast.NodeVisitor):
  lox: 'Lox'
  interpreter: Interpreter

  def __post_init__(self):
    self.scopes: List[Dict[str, bool]] = []
    self.current_function = FunctionType.NONE
    self.current_klass = ClassType.NONE

  @contextlib.contextmanager
  def scope(self) -> Generator[None, None, None]:
    self.scopes.append({})
    yield
    self.scopes.pop()

  @contextlib.contextmanager
  def new_function(self, type: FunctionType) -> Generator[None, None, None]:
    prev = self.current_function
    self.current_function = type
    yield
    self.current_function = prev

  @contextlib.contextmanager
  def new_klass(self, type: ClassType) -> Generator[None, None, None]:
    prev = self.current_klass
    self.current_klass = type
    yield
    self.current_klass = prev

  def current_scope(self):
    return self.scopes[-1]

  def resolve(self, node: ast.Node) -> None:
    node.accept(self)

  def resolve_statements(self, stmts: List[ast.Stmt]) -> None:
    for stmt in stmts:
      self.resolve(stmt)
  
  def declare(self, name: Token):
    if not self.scopes:
      return
    scope = self.current_scope()
    if name.lexeme in scope:
      self.lox.token_error(name, 'Already a variable with this name in this scope.')
    scope[name.lexeme] = False
    
  def define(self, name: Token):
    if not self.scopes:
      return
    self.current_scope()[name.lexeme] = True

  def resolve_local(self, expr: ast.Expr, name: Token):
    for i, scope in enumerate(self.scopes[::-1]):
      if name.lexeme in scope:
        self.interpreter.resolve(expr, i)
        return
    
  def visit_assign(self, expr: ast.Assign) -> None:
    self.resolve(expr.value)
    self.resolve_local(expr, expr.name)

  def visit_call(self, expr: ast.Call) -> None:
    self.resolve(expr.callee)
    for arg in expr.arguments:
      self.resolve(arg)

  def visit_get(self, expr: ast.Get) -> None:
    self.resolve(expr.obj)

  def visit_binary(self, expr: ast.Binary) -> None:
    self.resolve(expr.left)
    self.resolve(expr.right)

  def visit_grouping(self, expr: ast.Grouping) -> None:
    self.resolve(expr.expression)

  def visit_literal(self, _: ast.Literal) -> None:
    return

  def visit_logical(self, expr: ast.Logical) -> None:
    self.resolve(expr.left)
    self.resolve(expr.right)

  def visit_set(self, expr: ast.Set) -> None:
    self.resolve(expr.value)
    self.resolve(expr.obj)

  def visit_this(self, expr: ast.This) -> None:
    if self.current_klass is ClassType.NONE:
      self.lox.error(expr.keyword, 'Can\'t use `this` outside of a class.')
    self.resolve_local(expr, expr.keyword)

  def visit_unary(self, expr: ast.Unary) -> None:
    self.resolve(expr.right)

  def visit_variable(self, expr: ast.Variable) -> None:
    if self.scopes and not self.current_scope()[expr.name.lexeme]:
      self.lox.token_error(
          expr.name, 'Can\'t read local variable in its own initializer')
    self.resolve_local(expr, expr.name)
    return

  def visit_function_decl(self, stmt: ast.FunctionDecl) -> None:
    self.declare(stmt.name)
    self.define(stmt.name)
    self.resolve_function(stmt, FunctionType.FUNCTION)

  def resolve_function(self, stmt: ast.FunctionDecl, func_type: FunctionType) -> None:
    with self.scope(), self.new_function(func_type):
      for param in stmt.params:
        self.declare(param)
        self.define(param)
      self.resolve_statements(stmt.body)

  def visit_if(self, stmt: ast.If) -> None:
    self.resolve(stmt.condition)
    self.resolve(stmt.then_branch)
    if stmt.else_branch:
      self.resolve(stmt.else_branch)

  def visit_expression_stmt(self, stmt: ast.ExpressionStmt) -> None:
    self.resolve(stmt.expression)

  def visit_print_stmt(self, stmt: ast.PrintStmt) -> None:
    self.resolve(stmt.expression)

  def visit_return_stmt(self, stmt: ast.ReturnStmt) -> None:
    if self.current_function is FunctionType.NONE:
      self.lox.token_error(stmt.keyword, 'Can\'t return from top-level code.')
    if stmt.value:
      if self.current_function is FunctionType.INITIALIZER:
        self.lox.token_error(stmt.keyword, 'Can\'t return from an initializer.')
      self.resolve(stmt.value)

  def visit_while(self, stmt: ast.While) -> None:
    self.resolve(stmt.condition)
    self.resolve(stmt.body)

  def visit_block(self, stmt: ast.Block) -> None:
    with self.scope():
      self.resolve_statements(stmt.statements)

  def visit_class(self, stmt: ast.Class) -> None:
    self.declare(stmt.name)
    self.define(stmt.name)
    with self.scope(), self.new_klass(ClassType.CLASS):
      self.current_scope()['this'] = True
      for method in stmt.methods:
        declaration = FunctionType.METHOD
        if method.name.lexeme == 'init':
          declaration = FunctionType.INITIALIZER
        self.resolve_function(method, declaration)

  def visit_var_decl(self, stmt: ast.VarDecl) -> None:
    self.declare(stmt.name)
    if stmt.initializer is not None:
      self.resolve(stmt.initializer)
    self.define(stmt.name)
